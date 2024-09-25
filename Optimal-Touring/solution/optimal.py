import random
import sys
from collections import namedtuple
from typing import List, Dict, Tuple

Site = namedtuple('Site', ['id', 'avenue', 'street', 'desired_time', 'value'])
TimeWindow = namedtuple('TimeWindow', ['site_id', 'day', 'begin_hour', 'end_hour'])

class Solution:
    def __init__(self, routes: List[List[int]]):
        self.routes = routes

def parse_input(filename: str) -> Tuple[List[Site], List[TimeWindow]]:
    with open(filename, 'r') as file:
        content = file.read()
    max_days = 0
    lines = content.strip().split('\n')
    sites = []
    time_windows = []
    parsing_sites = True
    
    for line in lines[1:]:  # Skip the header line
        if line == "" or len(line.split()) == 0:
            continue
        if line.strip() == "site day beginhour endhour":
            parsing_sites = False
            continue        
        if parsing_sites:
            site_id, avenue, street, desired_time, value = map(int, line.split())
            sites.append(Site(site_id, avenue, street, desired_time, value))
        else:
            site_id, day, begin_hour, end_hour = map(int, line.split())
            time_windows.append(TimeWindow(site_id, day, begin_hour, end_hour))
            max_days = max(max_days, day)
    
    return sites, time_windows, max_days

def calculate_travel_time(site1: Site, site2: Site) -> int:
    return abs(site1.avenue - site2.avenue) + abs(site1.street - site2.street)

def is_feasible_route(route: List[int], sites: List[Site], time_windows: Dict[int, TimeWindow], day: int) -> bool:
    if not route:
        return True
    current_time = time_windows[route[0]].begin_hour * 60
    for i in range(len(route)):
        site = sites[route[i] - 1]
        tw = time_windows[route[i]]
        if tw.day != day:
            return False
        if current_time < tw.begin_hour * 60:
            current_time = tw.begin_hour * 60
        current_time += site.desired_time
        if current_time >= (tw.end_hour + 1) * 60:
            return False
        if i < len(route) - 1:
            current_time += calculate_distance(site, sites[route[i+1] - 1])
    return True

def write_solution_to_file(solution: Solution, sites: List[Site], time_windows: List[TimeWindow]):
    with open('result.txt', 'w', encoding="utf-8") as f:
        for day, route in enumerate(solution.routes):
            current_time = 0
            for index, site in enumerate(route):
                begin_time = time_windows[site].begin_hour * 60
                if current_time < begin_time:
                    f.write(f"{begin_time - current_time}\n")
                    f.write("delay\n")
                    current_time = begin_time
                f.write(f"{site}\n")
                f.write("move\n")
                f.write(f"{site}\n")
                f.write("getCost\n")
                f.write("delay\n")
        f.close()

def calculate_solution_value(solution: Solution, sites: List[Site]) -> int:
    return sum(sites[site_id - 1].value for route in solution.routes for site_id in route)

def generate_initial_solution(sites: List[Site], max_days: int) -> Solution:
    site_ids = [site.id for site in sites]
    random.shuffle(site_ids)
    print(f"shuffled routes: {site_ids}")
    routes = [site_ids[i::max_days] for i in range(max_days)]
    print(f"routes: {routes}")
    return Solution(routes)

def generate_neighborhood(solution: Solution, time_windows: Dict[int, TimeWindow]) -> List[Solution]:
    neighborhood = []
    for i in range(len(solution.routes)):
        for j in range(i+1, len(solution.routes)):
            for site in solution.routes[i]:
                if time_windows[site].day == j + 1:  # Check if the site can be moved to this day
                    new_solution = Solution([route[:] for route in solution.routes])
                    new_solution.routes[i].remove(site)
                    new_solution.routes[j].append(site)
                    neighborhood.append(new_solution)
    return neighborhood

def is_tabu(move: Tuple[int, int, int], tabu_list: List[Tuple[int, int, int]], iteration: int, tabu_tenure: int) -> bool:
    return any(m == move and iteration - i <= tabu_tenure for i, m in enumerate(tabu_list))

def update_tabu_list(tabu_list: List[Tuple[int, int, int]], move: Tuple[int, int, int], iteration: int) -> None:
    tabu_list.append((iteration, *move))

def tabu_search(sites: List[Site], time_windows: List[TimeWindow], max_days: int, max_iterations: int, tabu_tenure: int) -> Solution:
    tw_dict = {tw.site_id: tw for tw in time_windows}
    initial_solution = generate_initial_solution(sites, max_days)
    best_solution = initial_solution
    current_solution = initial_solution
    tabu_list = []

    for iteration in range(max_iterations):
        neighborhood = generate_neighborhood(current_solution, time_windows)
        best_neighbor = None
        best_neighbor_value = float('-inf')

        for neighbor in neighborhood:
            move = (neighbor.routes[0][0], neighbor.routes[1][0], neighbor.routes[1][-1])
            if is_tabu(move, tabu_list, iteration, tabu_tenure) and calculate_solution_value(neighbor, sites) <= calculate_solution_value(best_solution, sites):
                continue
            
            if all(is_feasible_route(route, sites, tw_dict, day+1) for day, route in enumerate(neighbor.routes)):
                neighbor_value = calculate_solution_value(neighbor, sites)
                if neighbor_value > best_neighbor_value:
                    best_neighbor = neighbor
                    best_neighbor_value = neighbor_value

        if best_neighbor is None:
            break

        current_solution = best_neighbor
        update_tabu_list(tabu_list, move, iteration)

        if calculate_solution_value(current_solution, sites) > calculate_solution_value(best_solution, sites):
            best_solution = current_solution

    return best_solution

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    # Parse input
    sites, time_windows, max_days = parse_input(input_file)

    # Set parameters
    max_iterations = 100000
    tabu_tenure = 50

    # Run tabu search
    # for tenure in range(5,50):
    best_solution = tabu_search(sites, time_windows, max_days, max_iterations, tabu_tenure)

    # Print results
    print("Best solution:")
    for i, route in enumerate(best_solution.routes):
        print(f"Day {i+1}: {route}")
    print(f"Total value: {calculate_solution_value(best_solution, sites)}")
    write_solution_to_file(best_solution, sites, time_windows)

if __name__ == "__main__":
    main()