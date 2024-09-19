import OptimalTouring as Game

x = Game.OptimalTouring("sites.txt")
fileName = "myCode.txt"
with open(fileName, "r") as f:
    lines = f.readlines()

i = -1
stack = []
while i < len(lines)-1:
    i += 1
    line = lines[i].strip()  # Remove leading/trailing whitespace

    # Skip empty lines
    if not line:
        continue

    # Skip comment lines
    if line.startswith('#'):
        continue

    # For debug use
    # if print, print the stack, and press enter to continue
    if "print" in line:
        print(stack)
        input()
        continue

    # if state, print the current state, and press enter to continue
    if "state" in line:
        print(x.getState())
        input()
        continue

    # For Coding
    # if integer, just push it to stack
    try:
        stack.append(int(line))
        continue
    except:
        pass

    # if jmp, jump to the line of last stack value and pop that value
    if "jmp" in line:
        i = stack[-1]-2
        stack = stack[:-1]
        continue

    # if jcp, pop and compare top 2 values in stack, if the top 1 is larger, pop and jump to top3 th line
    if "jcp" in line:
        if stack[-1] > stack[-2]:
            i = stack[-3]-2
            stack = stack[:-3]
        else:
            stack = stack[:-2]
        continue  # Add continue here to avoid processing further

    # if +, pop and add the top 2 value in stack and push back to stack
    if "+" in line:
        stack[-2] = stack[-1] + stack[-2]
        stack = stack[:-1]
        continue

    # if -, pop and do "top value - second top value in stack", and push the result back to stack
    if "-" in line:
        stack[-2] = stack[-1] - stack[-2]
        stack = stack[:-1]
        continue

    # if pop, pop the top value in stack
    if "pop" in line:
        stack = stack[:-1]
        continue

    # if swap, x=top-value, swap the second top value in stack with xth top value, then pop the top value
    if "swap" in line:
        a = stack[-1]
        b = stack[-2]
        stack[-2] = stack[-a]
        stack[-a] = b
        stack = stack[:-1]
        continue

    # if cpy, copy and push the top value in stack
    if "cpy" in line:
        stack.append(stack[-1])
        continue

    # if move, move to the site with siteId = top value in stack, pop the value
    if "move" in line:
        x.sendMove(siteId=stack[-1])
        stack = stack[:-1]
        continue

    # if delay, delay the amount of time in stack, pop the value
    if "delay" in line:
        x.sendMove(delayTime=stack[-1])
        stack = stack[:-1]
        continue

    # if getTimeRemain, push the remainTime to stack
    if "getTimeRemain" in line:
        stack.append(x.getDay()*1440 - x.getTime())
        continue

    # if getCost, pop the top value in stack as x, and push the time needed for x site to stack
    if "getCost" in line:
        stack[-1] = x.getSites()[stack[-1]-1][2]
        continue

    # if getReward, pop the top value in stack as x, and push the reward for x site to stack
    if "getReward" in line:
        stack[-1] = x.getSites()[stack[-1]-1][3]
        continue

    # if getStart, x=top 1 value, y = top 2 value, pop top 2 values in stack, and push the start time of site x in day y
    if "getStart" in line:
        a = stack[-1]
        b = stack[-2]
        stack = stack[:-1]
        stack[-1] = x.getSites()[a-1][4][b-1][0]
        continue

    # if getEnd, x=top 1 value, y = top 2 value, pop top 2 values in stack, and push the end time of site x in day y
    if "getEnd" in line:
        a = stack[-1]
        b = stack[-2]
        stack = stack[:-1]
        stack[-1] = x.getSites()[a-1][4][b-1][1]
        continue

    # if getMaxSitesNo, push the max site number to stack
    if "getMaxSitesNo" in line:
        stack.append(x.getMaxSitesNo())
        continue

x.settlement()
x.printPath()
input()
