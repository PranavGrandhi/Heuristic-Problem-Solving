import random
import sys
from copy import deepcopy
from typing import List, Dict, Tuple
import math

class Site:
    def __init__(self, site_id, avenue, street, desired_time, value):
        self.id = site_id
        self.avenue = avenue
        self.street = street
        self.desired_time = desired_time  # in minutes
        self.value = value
        self.open_days = []
        self.time_windows = {}  # day -> {'begin_hour': x, 'end_hour': y}

    def add_time_window(self, day, begin_hour, end_hour):
        self.open_days.append(day)
        self.time_windows[day] = {'begin_hour': begin_hour, 'end_hour': end_hour}

def parse_input(filename: str) -> Tuple[Dict[int, Site], int]:
    with open(filename, 'r') as file:
        lines = file.readlines()
    sites = {}
    max_day = 0
    parsing_sites = True

    for line in lines[1:]:  # Skip the header line
        line = line.strip()
        if line == "" or len(line.split()) == 0:
            continue
        if line.strip() == "site day beginhour endhour":
            parsing_sites = False
            continue
        if parsing_sites:
            site_id, avenue, street, desired_time, value = line.split()
            site_id = int(site_id)
            avenue = int(avenue)
            street = int(street)
            desired_time = int(desired_time)
            value = float(value)
            sites[site_id] = Site(site_id, avenue, street, desired_time, value)
        else:
            site_id, day, begin_hour, end_hour = map(int, line.split())
            sites[site_id].add_time_window(day, begin_hour, end_hour)
            if day > max_day:
                max_day = day

    return sites, max_day

def calculate_travel_time(site1: Site, site2: Site) -> int:
    return abs(site1.avenue - site2.avenue) + abs(site1.street - site2.street)

class Particle:
    def __init__(self, sites: Dict[int, Site], max_day: int):
        self.sites = sites
        self.max_day = max_day
        self.routes = {day: [] for day in range(1, max_day + 1)}
        self.best_routes = None
        self.best_value = -math.inf
        self.velocity = []
        self.initialize_routes()
        self.evaluate()

    def initialize_routes(self):
        site_ids = list(self.sites.keys())
        random.shuffle(site_ids)
        for site_id in site_ids:
            site = self.sites[site_id]
            possible_days = site.open_days
            if not possible_days:
                continue
            day = random.choice(possible_days)
            self.routes[day].append(site_id)
        for day in self.routes:
            random.shuffle(self.routes[day])

    def evaluate(self):
        self.value = 0
        self.total_reward = 0
        self.feasible_routes = {}
        for day in self.routes:
            route = self.routes[day]
            route_reward, feasible_route = self.evaluate_route(route, day)
            self.total_reward += route_reward
            self.feasible_routes[day] = feasible_route
        if self.total_reward > self.best_value:
            self.best_value = self.total_reward
            self.best_routes = deepcopy(self.routes)

    def evaluate_route(self, route: List[int], day: int) -> Tuple[float, List[int]]:
        current_time = 0
        total_reward = 0
        feasible_route = []
        for i, site_id in enumerate(route):
            site = self.sites[site_id]
            tw = site.time_windows.get(day)
            if not tw:
                continue
            begin_time = tw['begin_hour'] * 60
            end_time = (tw['end_hour'] + 1) * 60 - 1

            # Travel time from previous site
            if feasible_route:
                prev_site = self.sites[feasible_route[-1]]
                travel_time = calculate_travel_time(prev_site, site)
                current_time += travel_time
            else:
                current_time = 0

            arrival_time = current_time

            # Wait until the site opens
            waiting_time = max(begin_time - arrival_time, 0)
            arrival_time += waiting_time

            # Time needed at site
            departure_time = arrival_time + site.desired_time

            # Check if we can finish visiting before the site closes
            if departure_time <= end_time:
                # We can visit this site
                total_reward += site.value
                feasible_route.append(site_id)
                current_time = departure_time
            else:
                # Cannot visit this site within its time window
                continue

        return total_reward, feasible_route

    def update_velocity(self, global_best):
        self.velocity = []
        # Move towards personal best
        for day in self.routes:
            route = self.routes[day]
            best_route = self.best_routes.get(day, [])
            common_sites = set(route).intersection(set(best_route))
            for site_id in common_sites:
                i = route.index(site_id)
                j = best_route.index(site_id)
                if i != j:
                    self.velocity.append(('swap', day, i, j))
            sites_to_add = [site for site in best_route if site not in route]
            for site_id in sites_to_add:
                self.velocity.append(('add', day, site_id))
            sites_to_remove = [site for site in route if site not in best_route]
            for site_id in sites_to_remove:
                self.velocity.append(('remove', day, site_id))

        # Move towards global best
        for day in self.routes:
            route = self.routes[day]
            global_route = global_best.best_routes.get(day, [])
            common_sites = set(route).intersection(set(global_route))
            for site_id in common_sites:
                i = route.index(site_id)
                j = global_route.index(site_id)
                if i != j:
                    self.velocity.append(('swap', day, i, j))
            sites_to_add = [site for site in global_route if site not in route]
            for site_id in sites_to_add:
                self.velocity.append(('add', day, site_id))
            sites_to_remove = [site for site in route if site not in global_route]
            for site_id in sites_to_remove:
                self.velocity.append(('remove', day, site_id))

    def apply_velocity(self):
        for move in self.velocity:
            if move[0] == 'swap':
                day, i, j = move[1], move[2], move[3]
                if i < len(self.routes[day]) and j < len(self.routes[day]):
                    self.routes[day][i], self.routes[day][j] = self.routes[day][j], self.routes[day][i]
            elif move[0] == 'add':
                day, site_id = move[1], move[2]
                site = self.sites[site_id]
                if day in site.open_days and site_id not in self.routes[day]:
                    self.routes[day].append(site_id)
            elif move[0] == 'remove':
                day, site_id = move[1], move[2]
                if site_id in self.routes[day]:
                    self.routes[day].remove(site_id)
        self.velocity = []

    def mutate(self, iteration, max_iterations):
        # Compute mutation_rate
        mutation_rate = 1 - (iteration / max_iterations)
        MAX_MUTATIONS = 20  # Adjust as needed
        num_mutations = max(1, int(mutation_rate * MAX_MUTATIONS))

        for _ in range(num_mutations):
            # Randomly select a mutation type
            mutation_type = random.choice(['swap_within_day', 'swap_between_days', 'move_between_days', 'reverse_segment'])

            if mutation_type == 'swap_within_day':
                day = random.choice(list(self.routes.keys()))
                if len(self.routes[day]) > 1:
                    i, j = random.sample(range(len(self.routes[day])), 2)
                    self.routes[day][i], self.routes[day][j] = self.routes[day][j], self.routes[day][i]

            elif mutation_type == 'swap_between_days':
                day1, day2 = random.sample(list(self.routes.keys()), 2)
                if self.routes[day1] and self.routes[day2]:
                    idx1 = random.randrange(len(self.routes[day1]))
                    idx2 = random.randrange(len(self.routes[day2]))
                    site1 = self.routes[day1][idx1]
                    site2 = self.routes[day2][idx2]
                    if day2 in self.sites[site1].open_days and day1 in self.sites[site2].open_days:
                        self.routes[day1][idx1], self.routes[day2][idx2] = site2, site1

            elif mutation_type == 'move_between_days':
                day_from, day_to = random.sample(list(self.routes.keys()), 2)
                if self.routes[day_from]:
                    site_id = random.choice(self.routes[day_from])
                    site = self.sites[site_id]
                    if day_to in site.open_days:
                        self.routes[day_from].remove(site_id)
                        self.routes[day_to].append(site_id)

            elif mutation_type == 'reverse_segment':
                day = random.choice(list(self.routes.keys()))
                if len(self.routes[day]) > 2:
                    start_idx = random.randint(0, len(self.routes[day]) - 2)
                    end_idx = random.randint(start_idx + 1, len(self.routes[day]) - 1)
                    self.routes[day][start_idx:end_idx+1] = list(reversed(self.routes[day][start_idx:end_idx+1]))

class PSO:
    def __init__(self, sites: Dict[int, Site], max_day: int, num_particles: int, num_iterations: int):
        self.sites = sites
        self.max_day = max_day
        self.num_particles = num_particles
        self.num_iterations = num_iterations
        self.particles = [Particle(sites, max_day) for _ in range(num_particles)]
        self.global_best = max(self.particles, key=lambda p: p.best_value)

    def run(self):
        for iteration in range(self.num_iterations):
            for particle in self.particles:
                particle.update_velocity(self.global_best)
                particle.apply_velocity()
                particle.mutate(iteration, self.num_iterations)
                particle.evaluate()
                if particle.best_value > self.global_best.best_value:
                    self.global_best = deepcopy(particle)
            print(f"Iteration {iteration + 1}/{self.num_iterations}, Best Value: {self.global_best.best_value}")

    def write_solution(self, filename='result.txt'):
        with open(filename, 'w') as f:
            for day in sorted(self.global_best.feasible_routes.keys()):
                route = self.global_best.feasible_routes[day]
                if not route:
                    continue
                current_time = 0
                for i, site_id in enumerate(route):
                    site = self.sites[site_id]
                    tw = site.time_windows.get(day)
                    if not tw:
                        continue
                    begin_time = tw['begin_hour'] * 60
                    end_time = (tw['end_hour'] + 1) * 60 - 1

                    # Travel time from previous site (except for the first site)
                    if i > 0:
                        prev_site = self.sites[route[i - 1]]
                        travel_time = calculate_travel_time(prev_site, site)
                        current_time += travel_time
                    else:
                        current_time = 0

                    arrival_time = current_time

                    # Wait until the site opens
                    waiting_time = max(begin_time - arrival_time, 0)
                    arrival_time += waiting_time

                    # Time spent at the site
                    total_delay = waiting_time + site.desired_time

                    # Update current time
                    current_time = arrival_time + site.desired_time

                    # Output site number
                    f.write(f"{site_id}\n")
                    f.write("move\n")

                    # Output total delay time
                    f.write(f"{int(total_delay)}\n")
                    f.write("delay\n")

        print(f"Solution written to {filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python pso_solution.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    sites, max_day = parse_input(input_file)

    # Set PSO parameters
    num_particles = 30
    num_iterations = 100

    # Run PSO
    pso = PSO(sites, max_day, num_particles, num_iterations)
    pso.run()

    # Write the best solution to file
    pso.write_solution()

if __name__ == "__main__":
    main()
