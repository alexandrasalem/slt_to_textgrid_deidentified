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
and a boolean and a gap count for each tier: 
- child_boolean
- examiner_boolean
- comment_boolean 
- child_gap_count 
- examiner_gap_count 
- comment_gap_count
- activity_gap_count

(We don't need an activity_boolean because there should be no gaps between activities--we use the count just to calculate length)

We have a function time_function that could potentially calculate a specific length
of each utterance based upon number of words, but here we just have it set to 
each utterance is a delta, .1 second. 

Then, we run through the (pre-processed) original .slt file, and simulate the time stamps and formatting
using our timestamps, booleans, and gap counts (explained further in the main file).