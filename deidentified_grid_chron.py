
"""
This script converts a .slt transcript file to our chronological .TextGrid format.
This allows us to run desaltify on the .slt transcripts.

Here's a sample from a .TextGrid file: (The 2 time1 time2 means tier 2 (the Examiner) spoke from time1 to time2, 
and said the phrase on the following line in quotes)

2 128.90218325 130.061723356
"XXX." [removed for privacy]
2 130.061723356 131.087755102
""
2 131.087755102 132.519175887
"XXX." [removed for privacy]
2 132.519175887 133.509886621
""
2 133.509886621 135.898074937
"XXX." [removed for privacy]

As seen above, .TextGrid files need to record the time interval for each speaker's utterance, 
and then the time interval for how long it has been since a speaker last spoke.

But, the .slt files don't have time stamps, only pauses and minute-marks. So, we have to
create a system to best mimic that .TextGrid set-up.

We have two general time stamp variables (timestamp1, timestamp2), 
and a boolean and a gap count for each tier (child_boolean, examiner_boolean, comment_boolean, 
                                            child_gap_count, examiner_gap_count, comment_gap_count
                                            activity_gap_count).
(We don't need an activity_boolean because there should be no gaps between activities--we use the count just to calculate length)

We have a function time_function that could potentially calculate a specific length
of each utterance based upon number of words, but here we just have it set to 
each utterance is a delta, .1 second. 

Then, we run through the (pre-processed) original .slt file, and simulate the time stamps and formatting
using our timestamps, booleans, and gap counts (explained further in the main file).

"""
import sys
from grid_helper_functions import time_to_seconds, pre_process, first_real_line, number_of_lines, go_here, preamble, time_function

activities = ["= CONSTRUCTION TASK", "= PLAY", 
                    "= DEMONSTRATION TASK", "= PICTURE DESCRIPTION", 
                    "= WORDLESS PICTURE BOOK", "= CARTOONS", 
                    "= xEMOTIONS CONVERSATION", "= xSOCIAL DIFFICULTIES AND ANNOYANCE CONVERSATION", 
                     "= xEMOTIONS", "= BREAK",
                    "= xFRIENDS AND MARRIAGE CONVERSATION", "= CREATING A STORY", 
                    "= xLONELINESS CONVERSATION"]


def main(orig):
    #creating replace.txt, our pre-processed file:
    pre_process(orig)

    #converting the time given at the end of the txt file to seconds:
    leng = number_of_lines("replace.txt")
    time = go_here("replace.txt", leng-1)
    time = time[0:7]
    time = time_to_seconds(time)
    lines = []

    #initializing a variable for activities
    temp = 1

    #writing the preliminary lines
    lines = preamble(lines, time)
    
    with open("replace.txt", "r") as f2:
        #get to the beginning:
        x = first_real_line(f2)
        count = x[0]
        x = x[1]


        #initializing our variables:
        i = count 

        child_boolean = True 
        examiner_boolean = True 
        comment_boolean = True

        child_gap_count = .1 
        examiner_gap_count = .1 
        comment_gap_count = .1
        activity_gap_count = .1

        timestamp1 = 0.0 
        timestamp2 = 0.1 

        #our main loop
        while x:
            #if we are at the end of the file, add the last stuff:
            if i == leng-1:
                #lines.append("%s%s%s%s%s" % ("1 ", timestamp2-child_gap_count, " ", time, "\n"))
                lines.append("1 " + str(timestamp2-child_gap_count) + " " + str(time) + "\n")
                lines.append('""\n')  
                lines.append("2 " + str(timestamp2-examiner_gap_count) + " " + str(time) + "\n")
                lines.append('""\n')                                      
                lines.append("4 " + str(timestamp2-comment_gap_count) + " " + str(time) + "\n")   
                lines.append('""\n')          
                break
            #if Examiner spoke:
            if x[0] == "E" or x[0] == "O":
                #set other booleans to false, add time for this utterance to other gap counts: 
                child_boolean = False
                comment_boolean = False
                child_gap_count+=time_function(x)
                comment_gap_count +=time_function(x)
                activity_gap_count+=time_function(x)
                #if the examiner boolean is false (i.e., the examiner didn't just speak), print the gap since they last spoke:
                #also change examiner boolean to true, gap to 0:
                if examiner_boolean == False:
                    lines.append("2 " + str(timestamp2-examiner_gap_count) + " " + str(timestamp2) + "\n")
                    lines.append('""\n')
                    examiner_boolean = True 
                examiner_gap_count = 0 
                #add length of this utterance to general timestamps:
                timestamp1+=time_function(x) 
                timestamp2+=time_function(x) 
                #add the lines for the current utterance: 
                lines.append("2 " + str(timestamp1) +" " + str(timestamp2) + "\n")
                y = x
                y = y[2:-1]
                y = y.replace('"', '')
                lines.append('"' + y + '"' + "\n") 
            #if child spoke:
            elif x[0] == "C": 
                #set other booleans to false, add time for this utterance to other gap counts:
                examiner_boolean = False
                comment_boolean = False
                examiner_gap_count+=time_function(x)
                comment_gap_count +=time_function(x)
                activity_gap_count +=time_function(x)
                #if the child boolean is false (i.e., the child didn't just speak), print the gap since they last spoke:
                #also change child boolean to true, gap to 0:
                if child_boolean == False: 
                    lines.append("1 " + str(timestamp2-child_gap_count) + " " + str(timestamp2) + "\n")
                    lines.append('""\n')
                    child_boolean = True 
                child_gap_count = 0 
                #add length of this utterance to general timestamps:
                timestamp1+=time_function(x) 
                timestamp2+=time_function(x)
                #add the lines for the current utterance: 
                lines.append("1 " + str(timestamp1) + " " + str(timestamp2) + "\n")
                y = x
                y = y[2:-1]
                y = y.replace('"', '')
                lines.append('"' + y + '"' + "\n")
            #if there's a pause:
            elif x[0] == ";" or x[0] == ":":
                #convert that pause to seconds, and add it to the timestamps, gaps:
                y = time_to_seconds(x)
                timestamp1 += y
                timestamp2 += y
                examiner_gap_count += y
                child_gap_count += y
                comment_gap_count +=y
                activity_gap_count +=y
                #change booleans to false (now there's a gap since they all last spoke):
                child_boolean = False
                examiner_boolean = False
                comment_boolean = False
            #if there's a minute mark:
            elif x[0] == "-":
                #convert that minute mark to seconds:
                y = time_to_seconds(x)
                #move the gaps to be the previous gap, plus how far we are past the previous timestamp2 
                examiner_gap_count = y-(timestamp2-examiner_gap_count)  
                child_gap_count = y-(timestamp2-child_gap_count)
                comment_gap_count = y-(timestamp2-comment_gap_count)
                activity_gap_count = y-(timestamp2-activity_gap_count)
                timestamp1 = y-.1 
                timestamp2 = y
                child_boolean = False
                examiner_boolean = False
                comment_boolean = False
            #if there's an =, so either a comment or activity:
            elif x[0] == "=":
                #if an activity:
                if x[:-1] in activities:
                    #if not the first activity:
                    if temp!=1:
                        #correct the previous activity time:
                        lines[temp-1] = "3 " + str(timestamp2-activity_gap_count) + " " + str(timestamp2) + "\n"
                    #for the current activity, add a temporary time stamp line:
                    lines.append("temp_time" + "\n")
                    #add the activity name:
                    y = x
                    y = y[2:-1]
                    y = y.replace('"', '')
                    temp = len(lines)
                    lines.append('"' + y + '"' + "\n")
                    #change activity gap count to 0:
                    activity_gap_count = 0
                #if a comment:
                elif x[:-1] not in activities:
                    #if the comment boolean is false (i.e., there wasn't just a comment), print the gap since the last comment:
                    #also change comment boolean to false, gap to 0:
                    if comment_boolean == False:
                        lines.append("4 " + str(max(0, timestamp1-comment_gap_count)) + " " + str(timestamp1) + "\n")
                        lines.append('""\n')
                        comment_boolean = True
                    comment_gap_count = 0
                    #add the lines for the current comment: 
                    lines.append("4 " + str(timestamp1) + " " + str(timestamp2) + "\n")
                    y = x
                    y = y[2:-1]
                    y = y.replace('"', '')
                    lines.append('"' + y + '"' + "\n")
            i+=1
            x = f2.readline()

        #last thing, adding last activity:
        lines[temp-1] = "3 " + str(timestamp2-activity_gap_count) + " " + str(time) + "\n"

        #writing the new file:
        with open(str(orig)[:-4] + "_new.TextGrid", "w+") as f:
            for x in lines:
                f.write(str(x))

if __name__=='__main__':
    main(sys.argv[1])
