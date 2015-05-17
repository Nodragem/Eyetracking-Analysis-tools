To convert EDF files to a HDF5 file, you will need the edf2asc.exe provided by Eyelink.

Here the help output of the software, in case you have specific requirement.

USAGE: edf2asc.exe  [options] <input .edf file>
OPTIONS: -p <path> writes output with same name to <path> directory
         -p *.<ext> writes output of same name with new extension
         -d <filename> creates log data file
         -t use only tabs as delimiters
         -c check consistency
         -z disable check consistency and fix the errors
                   -v verbose - reports warning messages.
                   -y overwrite asc file if exists.
If no output file name, will match wildcards on input file name,
and will write output files to new path or will overwrite old files.
DATA OPTIONS: -sp  outputs sample raw pupil position if present
              -sh  outputs sample HREF angle data if present
              -sg  outputs sample GAZE data if present (default)
      -l or -nr   outputs left-eye data only if binocular data file
      -r or -nl   outputs right-eye data only if binocular data file
      -res         outputs resolution data if present
      -vel (-fvel) outputs sample velocity (-fvel matches EDFVIEW numbers)
      -s or -ne   outputs sample data only
      -e or -ns   outputs event data only
      -miss <value>     replaces missing (x,y) in samples with <value>
      -setres <xr> <yr> uses a fixed <xr>,<yr> resolution always
      -defres <xr> <yr> uses a default <xr>,<yr> resolution if none in file
      -nv         hide viewer commands
      -nst        blocks output of start events
      -nmsg       blocks message event output
      -neye       outputs only non-eye events (for sample-only files)
 Use  -neye     to get samples labeled with non-eye events only
 Use  -neye -ns to get non-eye events only
 Use  -utf8/-UTF8 to force the output file to be opened using utf-8 encoding
m.
-nflags to disable flags data for EyeLink II or EyeLink1000 data files.
-hpos  output head marker positions
-avg  output average data
-ftime output float time
-input output input values in samples.
-buttons output buttons values in samples.
-failsafe runs in failsafe mode and recover partial edf file
-ntarget to disable target data for EyeLink1000 Remote data files.
-ntime_check to disable large time stamp check.
-npa_check disable pupil area check to get gaze, href and raw data.


Scene camera parameters
-gazemap  outputs gaze data in avi coordinates. -g  can also be used instead
-insertframe  inserts frame number. -i can also be used instead
-scenecam  same as using -gazemap -insertframe together