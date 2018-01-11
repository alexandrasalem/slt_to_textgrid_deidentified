#my helper functions for grid_chron.py

import re
from time import strptime
from datetime import timedelta

def pre_process(orig):
    new = []
    first_line = None
    pattern1 = re.compile("^([ECOP])\s") #compiling means it only has to do that work once (not that big a deal though)
    pattern2 = re.compile("^([\$\+;:=-])")

    with open(orig, "r") as f2:
        current_line = None
        for row in f2:
            row = row.replace("\ufeff", "")
            row = row.strip()
            if pattern1.match(row) or pattern2.match(row):
                if current_line is not None:
                    new.append(current_line)
                current_line = row
            else:
                print(row)
                if len(row) == 0:
                    continue #no reason to keep empty rows
                assert current_line is not None, "This row is messed up: " + row
                current_line += " " + row
        new.append(current_line) #get the last line

    with open("replace.txt", "w+") as f3:
        first_line = new[0]
        for line in new:
            f3.write(line + "\n")
    return first_line

def tiers(line):
    tiers = []
    line = line.upper()
    pattern1 = re.compile("OTHER")
    pattern2 = re.compile("PARENT")
    count = 2
    if pattern1.search(line):
        tiers.append("Other")
    if pattern2.search(line):
        tiers.append("Parent")
    return tiers

def first_real_line(file):
    current = file.readline()
    count = 1
    while current[0] != "=" and current[0] != "-":
        current = file.readline()
        count+=1
    #return count
    x = [count, current]
    return x

def go_here(file, i):
    with open(file, "r") as f:
        current = f.readline()
        count = 0
        while count < i:
            current = f.readline()
            count+=1      
    return current

def preamble(ls, time, tiers):
    ls.append('"Praat chronological TextGrid text file"\n')
    ls.append("0.0 " + str(time) + "   !" + " Time domain.\n")
    ls.append(str(len(tiers) + 4) + "   ! Number of tiers.\n")
    ls.append('"IntervalTier" "Child" 0 ' + str(time) + '\n"IntervalTier" "Clinician" 0 ' + str(time) + '\n"IntervalTier" "Activity" 0 ' + str(time)+ '\n"IntervalTier" "Comments" 0 ' + str(time)+ '\n')
    for tier in tiers:
        ls.append('"IntervalTier" "' + tier + '" 0 ' + str(time) + '\n')
    return ls
    
def time_function(line):
    return .1

def time_to_seconds(line):
    line = line.strip()
    line = line.replace(" ", "")
    pattern = "^[-:;](\d+:\d\d)"
    result = re.match(pattern, line)

    assert result is not None, "This line begins with '-' or ';' or ':' but isn't a time!"+line
    time_string = result.group(1)

    test = time_string.split(":")
    time_string = str(int(test[0])//60) + ":" + str(int(test[0])%60) + ":" + test[1]

    t = strptime(time_string, "%H:%M:%S")
    seconds = timedelta(hours = t.tm_hour,minutes=t.tm_min,seconds=t.tm_sec).total_seconds()
    return seconds

def number_of_lines(file):
    i = 0
    with open(file, "r") as f:
        x = f.readline()
        while x:
            i+=1
            x = f.readline()
    return i

