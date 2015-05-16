Use multicleaning library to clean/analyse data with multi saccades per trial
Use singlecleaning library is you aim one saccade per trial. 

Here a description of what does my program:
- it converts Eyelink file in array-file, and give the statistics of missing trials found at this step,
- it store all the trials by sessions in a HDF5 file. You need to have file name which are meaningfull to find them back.

For example, use a file-name like MGF8TpB2 to specify Megardon Geoffrey, Frequence 80%, Target Present, Block 2.
- it  is done to detect one saccade in a periode of time (if there are more than one saccade, it put the trial is a suspect list)
- it marks the onset of the target, the start and the end of saccade it found
- from those markers it makes a list of suspect trials
- it displays trials on page of 50x10 plots. You pass to the next/previous page with the right/left key of the keyboard.
- click left button on a trial to display the trial on fullscreen to see it more precisely, click again to come back to the normal display,
- click right button to select a trial 
- press space to add/remove the selected to the list of rejected trials,
- it displays a slightly red background for the trials of the suspect list,
- Ctrl+F to selected all the suspected trials, Alt+F to deselected all the suspected trials,
- Ctrl+S to save the selected trials and mark them as rejected.
- the final file gives would a list of events (target onset, saccade start, saccade end) with a flag "condition", "trial", "rejected"