#!/usr/bin/env python

import sys
import time
import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from sklearn.cluster import KMeans

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


# Example solution implementation
def my_solution(pers, hosps, result_file):
    x = np.array([[p.x, p.y] for p in pers])
    kmeans = KMeans(n_clusters=len(hosps), random_state=0).fit(x)
    i = 0
    for hx, hy in kmeans.cluster_centers_:
        hosps[i].x = int(hx)
        hosps[i].y = int(hy)
        i = i + 1

    with open(result_file, "w") as output_file:
        # Write the hospital coordinates as provided
        for h in hosps:
            output_file.write(f"H{h.hid}:{h.x},{h.y}\n")
        output_file.write("\n")

        # Come up with a rescue plan.
        # For each ambulance, rescue the closest 4 people that would survive and take them to the nearest hospital.
        # Repeat until all people are rescued.

        # # Write the rescue plan as provided
        # output_file.write("0 H2 P124 P284 P273 P256 H2\n")

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
    paths = readresults(persons, hospitals, result_file)  # Get paths after processing results

    # After processing results, visualize the paths
    visualize_ambulance_paths(paths, hospitals, persons)
