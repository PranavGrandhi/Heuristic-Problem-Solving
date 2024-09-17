import OptimalTouring as Game

x = Game.OptimalTouring("sites.txt")

sites = x.getSites()
days = x.getDay()

pri = [days + 1 for i in range(len(sites))]
for i in range(len(sites)):
    for j in range(days):
        if sites[i][4][j][0] != 0 or sites[i][4][j][1] != 0:
            pri[i] = pri[i] - 1


# Edge Weight from site i to site j
def weight(i, j):
    return (sites[j][3]**5 * pri[j]**0) / (sites[j][2]**1 * (abs(sites[i][0]-sites[j][0]) + abs(sites[i][1] - sites[j][1]))**1)


adj_list = []
for i in range(len(sites)):
    temp_list = []
    for j in range(len(sites)):
        if i == j:
            temp_list.append(0)
        else:
            temp_list.append(weight(i, j))
    adj_list.append(temp_list)

# Day wise, Hour wise availability of sites
avail_map = {day: {open_hour: [] for open_hour in range(24)} for day
in range(days)}
for i in range(len(sites)):
    site = sites[i]
    for day in range(len(site[4])):
        open_hour = site[4][day][0] // 60
        close_hour = site[4][day][1] // 60
        while open_hour < close_hour:
            avail_map[day][open_hour].append(i + 1)
            open_hour += 1

# Compute V/T rank for all sites
rank_map = {i + 1: sites[i][3] / sites[i][2] for i in range(len(sites))}

# Start the game
curr_state = {'day': 0, 'time': 0, 'x': 0, 'y': 0, 'val': 0, 'travel': 0}
visited = [False for _ in range(len(sites))]


def add_time(minutes):
    x.sendMove(delayTime=minutes)
    curr_state['time'] += minutes / 60
    if curr_state['time'] >= 24:
        curr_state['day'] += 1
        curr_state['time'] = minutes % 60


def get_available_sites():
    return avail_map[curr_state['day']][int(curr_state['time'])]


def travel_time(x1, y1, x2=None, y2=None):
    x2 = x2 or curr_state['x']
    y2 = y2 or curr_state['y']
    return abs(x2 - x1) + abs(y2 - y1)

while curr_state['day'] < days:

    # Skipping empty hours
    while not bool(get_available_sites()):
        add_time(60)

    # Finding the first site with max V/T greedily
    first_site = [None, -1]
    for site in get_available_sites():
        if rank_map[site] > first_site[1] and not visited[site-1]:
            first_site = [site, rank_map[site]]

    # Spend time at the first site
    starting_day = curr_state['day']
    add_time(sites[first_site[0]][2])
    visited[first_site[0] - 1] = True
    curr_state['x'] = sites[first_site[0] - 1][0]
    curr_state['y'] = sites[first_site[0] - 1][1]
    curr_state['val'] += sites[first_site[0] - 1][3]
    x.sendMove(siteId=first_site[0])
    x.sendMove(delayTime=sites[first_site[0] - 1][2])

    # Choose next site

    result = []
    prev_site = first_site
    while starting_day == curr_state['day']:
        max_rank_site = [None, -1]
        time_to_travel, time_spent = -1, -1
        for site_i in get_available_sites():
            if adj_list[prev_site[0] - 1][site_i - 1] > max_rank_site[1] and not visited[site_i - 1]:
                time_to_travel = travel_time(sites[site_i - 1][0],sites[site_i - 1][1])
                desired_time = sites[site_i - 1][2]
                if curr_state['time'] * 60 + time_to_travel >= sites[site_i - 1][4][curr_state['day']][0] and \
                        curr_state['time'] * 60 + desired_time + time_to_travel <= sites[site_i - 1][4][curr_state['day']][1]:
                    max_rank_site = [site_i, adj_list[prev_site[0]][site_i - 1]]
                    time_spent = time_to_travel + desired_time
        if time_spent != -1:
            add_time(time_spent)
            prev_site = max_rank_site
            visited[prev_site[0] - 1] = True
            curr_state['x'] = sites[prev_site[0] - 1][0]
            curr_state['y'] = sites[prev_site[0] - 1][1]
            curr_state['val'] += sites[prev_site[0] - 1][3]
            curr_state['travel'] += time_to_travel
            x.sendMove(siteId=prev_site[0])
            x.sendMove(delayTime=time_spent)
        else:
            curr_state['day'] += 1
            curr_state['time'] = 0
    # print(curr_state)
    x.settlement()