#!/usr/bin/env python

#76 best score till now

import sys
import time
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances
from sklearn_extra.cluster import KMedoids

# Utility function to calculate Manhattan distance
def take_time(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)


# Exception classes
class ValidationError(ValueError):
    pass


class FormatSyntaxError(ValidationError):
    pass


class DataMismatchError(ValidationError):
    pass


class IllegalPlanError(ValidationError):
    pass


# Person object
PID = 0


class Person:
    def __init__(self, x, y, st):
        global PID
        PID += 1
        self.pid = PID
        self.x = x
        self.y = y
        self.st = st
        self.rescued = False
        return

    def __repr__(self):
        return 'P%d:(%d,%d,%d)' % (self.pid, self.x, self.y, self.st)


# Hospital object
HID = 0


class Hospital:
    def __init__(self, x, y, num_amb):
        global HID
        HID += 1
        self.hid = HID
        self.x = x
        self.y = y
        # amb_time array represents the time at which each ambulance ended its last tour.
        self.num_amb = num_amb
        self.amb_time = [0] * num_amb
        return

    def __repr__(self):
        return 'H%d:(%d,%d)' % (self.hid, self.x, self.y)

    def rescue(self, pers, end_hospital, start_time):
        if self.num_amb == 0:
            raise IllegalPlanError('No ambulance left at the hospital %s.' % self)
        else:
            self.amb_time.sort()
            if self.amb_time[0] > start_time:
                raise IllegalPlanError(
                    'No ambulance left at hospital %s at the start time %d minutes.' % (self, start_time))
        if 4 < len(pers):
            raise IllegalPlanError('Ignoring line as cannot rescue more than four people at once: %s.' % pers)
        already_rescued = list(filter(lambda p: p.rescued, pers))
        if already_rescued:
            print('Person %s already rescued.' % already_rescued)
        # t: time when end hospital is reached
        t = start_time + 1
        start = self
        for p in pers:
            t += take_time(start, p)
            start = p

        t += len(pers)
        t += take_time(start, end_hospital)

        self.amb_time.sort()
        rescued_persons = []
        for (i, t0) in enumerate(self.amb_time):
            if (t0 > start_time):
                continue
            rescued_persons = list(filter(lambda p: p.st >= t and p.rescued is False, pers))
            break
        self.amb_time[i] = t

        end_hospital.num_amb += 1
        end_hospital.amb_time.append(self.amb_time[i])

        self.num_amb -= 1
        self.amb_time.pop(i)

        for (i, p) in enumerate(rescued_persons):
            p.rescued = True
        if len(rescued_persons) == 0:
            print('Nobody will make it by end of %d minutes.' % t)
        else:
            if len(rescued_persons) == len(pers):
                print('Rescued:', ' and '.join(map(str, rescued_persons)), 'at', t, 'minutes | Ended at Hospital',
                      end_hospital)
            else:
                print('Rescued:', ' and '.join(map(str, rescued_persons)), 'at', t, 'minutes | Ended at Hospital',
                      end_hospital, "| Rest could not make it in time.")
        return rescued_persons


# Read input data function
def read_data(fname="input_data.txt"):
    persons = []
    hospitals = []
    mode = 0

    with open(fname, 'r') as fil:
        data = fil.readlines()

    for line in data:
        line = line.strip().lower()
        if line.startswith("person") or line.startswith("people"):
            mode = 1
        elif line.startswith("hospital"):
            mode = 2
        elif line:
            if mode == 1:
                (a, b, c) = map(int, line.split(","))
                persons.append(Person(a, b, c))
            elif mode == 2:
                (c,) = map(int, line.split(","))
                hospitals.append(Hospital(-1, -1, c))

    return persons, hospitals

def custom_distance(p1, p2, alpha=1, beta=1):
    spatial_dist = abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
    urgency_p1 = 1 / p1[2]
    urgency_p2 = 1 / p2[2]
    time_dist = abs(urgency_p1 - urgency_p2)
    return alpha * spatial_dist + beta * time_dist

# Example solution implementation
def my_solution(pers, hosps, result_file):
    # Perform k-means clustering to determine hospital locations
    x = np.array([[p.x, p.y, p.st] for p in pers])
    distance_matrix = pairwise_distances(x, metric=lambda u, v: custom_distance(u, v))
    kmedoids = KMedoids(n_clusters=len(hosps), metric='precomputed', random_state=0).fit(distance_matrix)

    medoid_indices = kmedoids.medoid_indices_
    medoids = x[medoid_indices]

    for i, hosp in enumerate(hosps):
        hosp.x = int(medoids[i][0])
        hosp.y = int(medoids[i][1])

    with open(result_file, "w") as output_file:
        # Write the hospital coordinates to the output file
        for h in hosps:
            output_file.write(f"H{h.hid}:{h.x},{h.y}\n")
        output_file.write("\n")

        # Create a list of unrescued persons
        unrescued_persons = pers.copy()

        # Main loop: While there are unrescued persons
        while unrescued_persons:
            any_rescued_in_this_iteration = False  # Flag to check if anyone was rescued in this iteration

            # For each hospital
            for hosp in hosps:
                # While there are ambulances available at this hospital
                while hosp.num_amb > 0:
                    # Get the earliest available ambulance time at this hospital
                    hosp.amb_time.sort()
                    start_time = hosp.amb_time[0]

                    # Initialize variables for the route
                    current_time = start_time
                    current_location = (hosp.x, hosp.y)
                    route = [f"{current_time} H{hosp.hid}"]
                    picked_persons = []

                    # Ambulance capacity
                    capacity = 4

                    # Build the route by selecting persons one by one
                    while capacity > 0:
                        # Find candidates who can be picked next
                        candidates = []

                        for p in unrescued_persons:
                            # Travel time from current location to person's location
                            travel_time_to_p = abs(current_location[0] - p.x) + abs(current_location[1] - p.y)

                            # Remaining survival time from current time
                            remaining_survival_time = p.st - current_time

                            if remaining_survival_time <= 0:
                                continue  # Cannot rescue this person as their survival time has expired

                            # Time to load the person (1 minute)
                            load_time = 1

                            # Estimate arrival time at this person's location
                            arrival_time_at_p = current_time + travel_time_to_p

                            # Update time after loading the person
                            time_after_loading_p = arrival_time_at_p + load_time

                            # Calculate travel time from person's location back to hospital
                            travel_time_to_hosp = abs(p.x - hosp.x) + abs(p.y - hosp.y)

                            # Estimate arrival time at hospital if we go directly after picking up this person
                            arrival_time_at_hosp = time_after_loading_p + travel_time_to_hosp

                            # Add unloading time at hospital (1 minute)
                            total_time_if_only_p = arrival_time_at_hosp + 1

                            # Check if this person can be delivered to the hospital before their survival time
                            if total_time_if_only_p <= p.st:
                                # Calculate priority score
                                # Adjust weights alpha and beta as needed
                                alpha = 4.5  # Weight for travel time
                                beta = 0  # Negative weight for remaining survival time to prioritize lower times
                                priority_score = alpha * travel_time_to_p + beta * remaining_survival_time

                                candidates.append((p, priority_score, travel_time_to_p, remaining_survival_time))

                        if not candidates:
                            break  # No candidates can be picked next

                        # Sort candidates based on priority score (lower score has higher priority)
                        candidates.sort(key=lambda x: x[1])

                        person_added = False
                        # Try to add candidates one by one
                        for candidate in candidates:
                            p = candidate[0]
                            travel_time_to_p = candidate[2]
                            # Remaining survival time is candidate[3]

                            # Update current_time to arrival at p
                            arrival_time_at_p = current_time + travel_time_to_p
                            # Load time
                            load_time = 1
                            time_after_loading_p = arrival_time_at_p + load_time
                            # Update current location
                            new_current_location = (p.x, p.y)

                            # Travel time back to hospital
                            travel_time_to_hosp = abs(new_current_location[0] - hosp.x) + abs(new_current_location[1] - hosp.y)
                            # Total time to return to hospital after picking up this person
                            total_time_to_hospital = time_after_loading_p + travel_time_to_hosp
                            # Add unloading time
                            total_time_with_unloading = total_time_to_hospital + 1

                            # Check if all picked persons and this person can be delivered on time
                            all_persons_delivered_on_time = True
                            for picked_p in picked_persons:
                                # Their arrival time at hospital is total_time_with_unloading
                                if total_time_with_unloading > picked_p['person'].st:
                                    all_persons_delivered_on_time = False
                                    break

                            if total_time_with_unloading > p.st:
                                all_persons_delivered_on_time = False

                            if all_persons_delivered_on_time:
                                # We can add this person to the route
                                current_time = time_after_loading_p  # Update current time after loading
                                current_location = new_current_location  # Update current location
                                picked_persons.append({'person': p, 'pickup_time': current_time})
                                route.append(f"P{p.pid}")
                                unrescued_persons.remove(p)
                                capacity -= 1
                                any_rescued_in_this_iteration = True
                                person_added = True
                                break  # Go back to while capacity > 0 loop to find next person

                        if not person_added:
                            # No suitable candidate could be added without exceeding survival times
                            break

                    # After picking up persons, travel back to hospital
                    if picked_persons:
                        # Travel time back to hospital from current location
                        travel_time_to_hosp = abs(current_location[0] - hosp.x) + abs(current_location[1] - hosp.y)
                        current_time += travel_time_to_hosp
                        current_location = (hosp.x, hosp.y)
                        # Unload time
                        current_time += 1
                        # Add ending hospital to route
                        route.append(f"H{hosp.hid}")

                        # Write the route to the output file
                        output_file.write(" ".join(route) + "\n")

                        # Update ambulance availability
                        hosp.amb_time[0] = current_time  # Update the ambulance's availability time
                        # Sort the ambulance times again
                        hosp.amb_time.sort()

                    else:
                        # No persons were picked in this route
                        break  # No point in continuing with this ambulance at this time

                    # If there are no more unrescued persons, break
                    if not unrescued_persons:
                        break

                # If there are no more unrescued persons, break
                if not unrescued_persons:
                    break

            # After checking all hospitals, if no one was rescued in this iteration, it means
            # no remaining persons can be rescued. Break out of the loop and finish.
            if not any_rescued_in_this_iteration:
                print("No more persons can be rescued. Finishing the rescue plan.")
                break

    print(f"Solution written to {result_file}")

# Function to read the result file and process paths for visualization
def readresults(persons, hospitals, fname):
    print('Reading data:', fname)
    res = {}
    score = 0
    hospital_index = 0
    paths = []  # List to store paths for visualization

    with open(fname, 'r') as fil:
        data = fil.readlines()

    for (i, line) in enumerate(data):
        if line.startswith('H'):
            print("\n" + line, end=" ")
            hospital_no = int(line.replace('H', '').split(':')[0])
            hospital_coordinates = line.replace('H', '').split(':')[1].split(',')
            (x, y) = [int(coordinates) for coordinates in hospital_coordinates]
            print(f"Hospital #{hospital_no}: coordinates ({x},{y})")
            hospitals[hospital_no - 1].x = x
            hospitals[hospital_no - 1].y = y
            continue

        line = line.strip()
        if not line:
            continue

        print("\n" + line, end="\n ")

        try:
            hos = None
            end_hos = None
            rescue_persons = []
            start_time = int(line.split()[0])
            route = line.split()[1:]

            # Collect coordinates for visualization
            route_coords = []

            for (i, w) in enumerate(route):
                if w[0] == 'H':
                    hospital_index = int(w[1:])
                    if i == 0:
                        hos = hospitals[hospital_index - 1]
                    else:
                        end_hos = hospitals[hospital_index - 1]
                    route_coords.append((hos.x, hos.y))
                elif w[0] == 'P':
                    person_index = int(w[1:])
                    per = persons[person_index - 1]
                    rescue_persons.append(per)
                    route_coords.append((per.x, per.y))

            if end_hos:
                route_coords.append((end_hos.x, end_hos.y))

            if hos and end_hos:
                rescue_persons = hos.rescue(rescue_persons, end_hos, start_time)
                score += len(rescue_persons)

                # Store the path information for visualization
                paths.append({
                    'start_time': start_time,
                    'coordinates': route_coords
                })

        except ValidationError as x:
            print('!!!', x)

    print('Total score:', score)
    return paths  # Return the paths for visualization


# Visualization function for ambulance paths
def visualize_ambulance_paths(paths, hospitals, persons):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Extract times for color mapping
    times = [path['start_time'] for path in paths]
    min_time, max_time = min(times), max(times)

    # Use color mapping (green to red)
    norm = plt.Normalize(min_time, max_time)
    cmap = cm.get_cmap('RdYlGn_r')  # Gradient from green to red

    # Set of rescued patients
    rescued_patients = set()

    # Plot paths, add arrows, and mark rescued patients
    for path in paths:
        x_coords = [p[0] for p in path['coordinates']]
        y_coords = [p[1] for p in path['coordinates']]

        # Calculate color based on start time
        color = cmap(norm(path['start_time']))
        ax.plot(x_coords, y_coords, color=color, linewidth=1)

        # Add arrows in the middle of paths
        for i in range(len(x_coords) - 1):
            ax.annotate('', xy=(x_coords[i + 1], y_coords[i + 1]), xytext=(x_coords[i], y_coords[i]),
                        arrowprops=dict(arrowstyle="->", color=color, lw=1))

        # Mark rescued patients
        for i in range(1, len(x_coords) - 1):
            ax.scatter(x_coords[i], y_coords[i], color='deepskyblue', marker='o', s=10, zorder=2)  # Rescued patient
            rescued_patients.add((x_coords[i], y_coords[i]))  # Record rescued patient coordinates

    # Plot unrescued patients (light gray)
    for person in persons:
        if (person.x, person.y) not in rescued_patients:
            ax.scatter(person.x, person.y, color='gray', marker='o', s=10, zorder=1)  # Unrescued patient

    # Set title and labels
    ax.set_title('Ambulance Pickup Problem Visualization')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')

    # Draw dashed grid, set interval to 1
    ax.set_xticks(np.arange(0, 150, 10))  # Set x-axis tick interval
    ax.set_yticks(np.arange(0, 350, 10))  # Set y-axis tick interval
    ax.grid(which='both', linestyle='--', linewidth=0.5)  # Draw dashed grid

    # Add colorbar
    plt.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), label='Time')

    # Plot hospital locations and ensure they are on top
    for hospital in hospitals:
        ax.scatter(hospital.x, hospital.y, marker='s', color='red', zorder=5)  # Set zorder to ensure it appears on top
        ax.text(hospital.x, hospital.y, f'H{hospital.hid}', fontsize=12, ha='right',
                zorder=6)  # Set zorder to be even higher

    plt.show()


# Main function

if __name__ == "__main__":
    input_file = "input_data.txt"
    # result_file = "sample_result.txt"
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        result_file = sys.argv[2]
    else:
        result_file = "Outputs/team_name.txt"  # default output

    print("Using " + input_file + " as input.\n")

    persons, hospitals = read_data(input_file)

    # Check if the result file already has content
    if os.path.exists(result_file) and os.path.getsize(result_file) > 0:
        print(f"Result file {result_file} already exists and has content.")
        print("Skipping solution generation and proceeding to validation and visualization.")
    else:
        # If the result file is empty or doesn't exist, call the solution
        start = datetime.datetime.now()

        print(f"Generating solution and writing to {result_file}...")
        my_solution(persons, hospitals, result_file)

        end = datetime.datetime.now()
        t = end - start
        if t.seconds >= 120:
            print("\n\tCode took too long to run. No points awarded.")
            sys.exit()

    # Read results for visualization
    persons, hospitals = read_data(input_file)
    paths = readresults(persons, hospitals, result_file)  # Get paths after processing results

    # After processing results, visualize the paths
    visualize_ambulance_paths(paths, hospitals, persons)
