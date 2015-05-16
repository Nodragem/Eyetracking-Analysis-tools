import os
import pandas as pd
import numpy as np
import matplotlib
import subprocess

''' multicleaning manage several saccades and it is then slower than singlecleaning'''

#matplotlib.use("WxAgg")
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import eyetools.figure as fg
#matplotlib.colors.ColorConverter.colors['i'] = (0, 0, 0, 0)
COLOR_LIST = np.array(("green", "blue", "red", "w"))
Type_color = np.array(("green", "blue", "red"))
#E_SACC_TYPE = np.array((1, 1, 2)) ## Expected Saccade in each condition (TRIAL_TYPE)
E_SACC_TYPE = np.array((0, 1, 1)) ## Expected Saccade in each condition (TRIAL_TYPE)
TRIAL_COL_NAME = "TRIAL_ID"

class ProgressBar():
    def __init__(self, text_to_display, value_max = 100, pos = (None,None)):

        self.value_max = value_max
        self.fig = plt.figure(figsize=(10, 1))
        if pos[0] is not None:
            thismanager = plt.get_current_fig_manager()
            #thismanager.window.SetPosition((pos[0], pos[1]))
        self.ax = plt.subplot(111)
        self.text_to_display = text_to_display
        #self.ax.margins(1.0,1.0)
        self.ax.set_xlim((0,self.value_max))
        self.ax.set_ylim((0,1))
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.title = self.ax.set_title("Progress")
        self.text = self.ax.text(0.5,0.5, "start", horizontalalignment='center', verticalalignment='center', transform=self.ax.transAxes)
        self.rect = self.ax.barh(0, 0, height = 1, left=0)[0]

        #self.text = ""
        self.value = 0
        plt.ion()
        self.fig.show(warn=True)
        #plt.show()
        plt.tight_layout(pad=1)
        #plt.draw()

    def step(self,v):
        self.value += v
        print "\r\t--> Progress %d/%d"%(self.value, self.value_max),

        self.rect.set_width(int(self.value))
        self.text.set_text("%d/%d" % (self.value, self.value_max))
        self.ax.figure.canvas.draw()
        #plt.draw()
    
    def setText(self, text):
        print text
        self.title.set_text(text)
        self.ax.figure.canvas.draw()
        
    def destroy(self):
        #print "\n Progress bar killed"
        #plt.ioff()
        plt.close(self.fig)


class TrialPlotter:
    def __init__(self, df, name, markers_table = None, var = ("xp","yp") ):
        self.name = name
        self.output_store = ""
        self.saved = True
        self.df = df
        self.markers_table = markers_table
        self.list_keys = np.unique(df[TRIAL_COL_NAME])
        self.nb_trials = len(self.list_keys)
        self.cid = None 
        self.mid = None
        self.fig = plt.figure()
        self.fig_title = self.fig.suptitle(self.name, fontsize = 20)
        self.n_plot = 50
        self.n_col = 10
        self.var = var
        self.n_row = (self.n_plot-1)/self.n_col + 1
        self.current_page = 1  
        self.list_ax = []
        self.list_texts = []
        self.textHidden = False
        self.origin_col = "black"
        self.orig_position = None
        self.zoomed_ax = None
        if (self.markers_table is not None) and ("rejected" in self.markers_table.columns):
            print "Markers_table retrieved from Hard drive..."
            select = self.markers_table["rejected"] == True
            self.tagged_trials = np.unique(self.markers_table.ix[select, "TRIAL_ID"]).tolist()
        else:
            self.tagged_trials = []
        self.detected_trials = []
        self.selected_axe = None
        self.nb_page = self.nb_trials/self.n_plot + 1
        
    def getMarks(self, trial_nb, table): ## get Markers from the Markers Table
        global COLOR_LIST
        list_markers = [[0]*9, COLOR_LIST[[3]*9]]
        if (trial_nb < 1) or (table is None):
            return list_markers
        select = (table["TRIAL_ID"] == trial_nb)
        list_markers[0] = table.ix[select, ["time"]].values
        list_markers[1] = COLOR_LIST[table.ix[select, ["marker"]].values.astype(int)%2 + 1] ## COLOR_LIST is an numpy array
        list_markers[1][0] = COLOR_LIST[0]
        #print list_markers
        return list_markers
 
    def startPlot(self, start = 1, end = 50, xylim = ((0,1600),(0, 1280))):
        for i in xrange(self.n_plot):
            ax = plt.subplot(self.n_row, self.n_col, i+1)
            ax.plot([], [], 'black')
            ax.plot([], [], 'grey')
            ax.set_xlim(*xylim[0])
            ax.set_ylim(*xylim[1])
            list_markers = self.getMarks(-1, self.markers_table)
            for m, c in zip(*list_markers):
                ax.axvline(m, color = c)
            ax.yaxis.set_ticks([0])
            ax.xaxis.set_ticks([0])
            text1 = ax.text(0.05, 0.95,"T", horizontalalignment='left', verticalalignment="top", transform=ax.transAxes)
            self.list_texts.append(text1)
            self.list_ax.append(ax)
        self.cid = self.fig.canvas.mpl_connect('key_press_event', self.onPressedKey)
        self.mid = self.fig.canvas.mpl_connect('button_press_event', self.onMouseClick)
        #select  = (self.df[TRIAL_COL_NAME] <= end) &  (self.df[TRIAL_COL_NAME] >= start)
        self.drawEyeMovement(self.df, self.current_page)
        ## turn off the shortcut of MatplotLib
        self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)
        #self.fig.show()
        plt.show(block=True)
        ##raw_input("check...")
    
    def onMouseClick(self, event):
        ax = event.inaxes ## axes are roughly the subplots' area
        if ax is None:
            return 0
        if event.button is 1:
            if self.selected_axe == ax:
                ax.title.set_color(self.origin_col)
                self.selected_axe = None
            else:
                if self.selected_axe != None:
                    self.selected_axe.title.set_color(self.origin_col) ## put back the color of the old selected
                self.selected_axe = ax
                self.origin_col = ax.title.get_color()
                ax.title.set_color("red")
            
        elif event.button is 3:
            # On right click, restore the axes
            if self.zoomed_ax != None:
                self.zoomed_ax.set_position(self.orig_position)
                for axis in event.canvas.figure.axes:
                    axis.set_visible(True)
                self.orig_position = None
                self.zoomed_ax = None
            else:
                # On left click, zoom the selected axes
                self.zoomed_ax = ax
                self.orig_position = ax.get_position()
                self.zoomed_ax.set_position([0.1, 0.1, 0.85, 0.85])
                for axis in event.canvas.figure.axes:
                    # Hide all the other axes...
                    if axis is not self.zoomed_ax:
                        axis.set_visible(False)
            
        else:
            # No need to re-draw the canvas if it's not a left or right click
            return
        event.canvas.draw()
        
    def getKeyTrial(self, selected_axe):
        if (selected_axe != None):
            return (int(selected_axe.get_title().split(" ")[1]) ) ## 1 + 161 - 1 to reach the 161th trial
        else:
            return 0
    
    def onPressedKey(self, event):
        #print "Pressed Key:", event.key
        if (event.key == "r"):
            self.startPlot()
            return

        elif (event.key == 'ctrl+t'):
            self.fig_title.set_text(self.name+"*")
            print "Merge detected and tagged trials..."
            print type(self.tagged_trials), type(self.detected_trials)
            self.tagged_trials = list(set(self.tagged_trials + self.detected_trials))
            print "There are %d tagged trials now."%len(self.tagged_trials)

        elif (event.key == 'alt+t'):
            self.fig_title.set_text(self.name+"*")
            print "Ummerge detected and tagged trials..."
            self.tagged_trials = [e for e in self.tagged_trials if e not in self.detected_trials]
            print "There are %d tagged trials now."%len(self.tagged_trials)

        elif (event.key == " ") & (self.selected_axe != None):
            self.fig_title.set_text(self.name+"*")
            selected_trial = self.getKeyTrial(self.selected_axe)
            if selected_trial not in self.tagged_trials:
                ## if not already in tagged trials, mark it:
                self.tagged_trials.append(selected_trial)
                self.origin_col = "blue" ## put the original color (without selection) to blue
                self.selected_axe.title.set_color("blue") ## override also the actual color
            else:
                self.tagged_trials.remove(selected_trial)
                self.origin_col = "black" ## put the original color (without selection) to blue
                self.selected_axe.title.set_color("yellow") ## override also the actual color
            self.fig.canvas.draw()
            print "\r", self.tagged_trials,
            return

        elif (event.key == "ctrl+s"):
            self.saveFile()

        elif (event.key == "d"):
            self.current_page = (self.current_page + 1) % self.nb_page
        elif (event.key == "a"):
            self.current_page = (self.current_page - 1) % self.nb_page
        elif (event.key == "t"):
            self.textHidden = not self.textHidden
        elif (event.key == "f"):
            try:
                TRIAL_ID = self.getKeyTrial(self.selected_axe)
                select = self.df[TRIAL_COL_NAME] == TRIAL_ID
                pos = self.df.ix[select, ["time","xp", "yp"]]
                fig = plt.figure()
                ax = fig.add_subplot(111)
                fg.plotting(pos,ax, xmin=0, xmax=1280, ymin=0, ymax=1024)
                ax.set_title("Trajectory Trial %d"%TRIAL_ID)
                fig.show()
            except:
                return
            return
        elif (event.key == "ctrl+n"):
            note_file = os.path.dirname(self.output_store)+"/"+self.name+"-notes.txt"
            print "Create note file:", note_file
            subprocess.call(["Notepad", note_file], shell=True)
        else:
            return

        self.drawEyeMovement(self.df, self.current_page)
        
    def setOutput(self, path):
        self.output_store = path
    
    def saveFile(self):
        ''' save the given markers_table with the rejected trials '''
        if self.output_store == "":
            print "File not saved. \nPlease set an Output Store to enable saving..."
            return 0
        ## add information on the result table:
        else:
            store = pd.HDFStore(self.output_store)
            rs = self.markers_table
            rs["rejected"] = False #np.array([False, False, False]*len(np.unique(rs["TRIAL_ID"]))).T
            ## be carefull, trial ID is now TRIAL_ID:
            rs.ix[rs["TRIAL_ID"].isin(self.tagged_trials), "rejected"] = True
            rs["Condition"] = "default"
            print "Save the file as %s in %s"%(self.name+"-seq", self.output_store)
            store[self.name+"-seq"] = rs
            store.close()
            #plt.suptitle(self.name+"-saved")
            self.fig_title.set_text(self.name+"-saved")
            print "Tagged trials saved!"
            print "Number of rejected:", len(self.tagged_trials), "\n"
            return 1
        
    def getInfoForPage(self, n):
        start = ( (n-1) * self.n_plot )%self.nb_trials + 1  ## for example start = 161
        end = start + self.n_plot - 1  # 161 + 50 - 1 = 210
        if end > self.nb_trials:
            end = self.nb_trials 
        totag = np.in1d(self.list_keys[(start-1):end], self.tagged_trials)
        toshade = np.in1d(self.list_keys[(start-1):end], self.detected_trials)
        print "Page %d show the trials: %d -- %d "%(n, start, end)
        #select  = (self.df[TRIAL_COL_NAME] <= end) &  (self.df[TRIAL_COL_NAME] >= start)
        select  = self.df[TRIAL_COL_NAME].isin(self.list_keys[(start-1):end])  # don't forget the start starts at 1
        return start, end, select, totag.tolist(), toshade.tolist()
        
    def drawEyeMovement(self, df, page_number):
        ''' m1, m2 and m3 try to mark the target appearance, the saccade's start and saccade's end'''

        start, end, select, tagged, detected = self.getInfoForPage(page_number)
        #print "tagged: ", tagged
        index = 0
        for key, grp in df.ix[select, :].groupby(TRIAL_COL_NAME):  # not really pretty to not check the size
            self.origin_col = "black"  # we have to reset the origin color as we are not on the same page anymore
            key = int(key)
            ax = self.list_ax[index % self.n_plot]
            text = self.list_texts[index % self.n_plot]
            iter_lines = iter(ax.get_lines())
            list_markers = self.getMarks(key, self.markers_table)
            list_coords = list_markers[0].tolist()
            list_colors = list_markers[1].tolist()
            #if state_draw == "OVER_TIME":
            for i, line in enumerate(iter_lines):
                if i == 0: line.set_data(grp["time"].values, grp[self.var[0]].values)
                elif i == 1: line.set_data(grp["time"].values, grp[self.var[1]].values)
                elif (i-2) < len(list_coords): # len(list_coords) is equal to len(list_colors)
                    j = i-2
                    m, c = list_coords[j][0], list_colors[j][0] ## that would be better to not need the [0] but yeah...
                    line.set_data((m,m), (0,1500))
                    line.set_color(c)
                else:
                    line.set_data((0,0), (0,1500))
                    line.set_color("green")
            ax.set_xlim(list_coords[0][0]-200, list_coords[-1][0]+200)
            ax.set_axis_bgcolor((1,1,1))
            ax.set_title("Key %d"%key, color = "black")
            trial_type = grp["TRIAL_TYPE"].iloc[0]
            if self.textHidden == False:
                text.set_text("T%d"%trial_type)
                text.set_color(Type_color[int(trial_type)%len(Type_color)])
            else:
                text.set_text("")
            index += 1
            #if state_draw == "OVER_SPACE":
            #    scatter
            
        if len(tagged) > 0:
            for i, m in enumerate(tagged):
                if m:
                    self.fig.get_axes()[i].title.set_color("blue")  # m-1 cause the list starts with an index of 0
        if len(detected) > 0:
            for i, d in enumerate(detected):
                if d:
                    self.fig.get_axes()[i].set_axis_bgcolor((1, 0.85, 0.85))
                    
        self.fig.canvas.draw()
        
def printHello():
    print "Hello! I'm here to clean the Data!'"
    
def findTheFirst(condition):
    try:
        m1 = np.where(condition)[0][0]
    except:
        m1 = -1
    finally:
        return m1

def findTheFirsofAll(condition):
    try:
        m1 = np.where(condition)[0][:]
        print m1
        #sys.exit()
    except:
        m1 = -1
    list_m1 =[]
    if m1 is not -1 and len(m1>1):
        list_m1.append(m1[0])
        previous_t = m1[0]
        for t in m1:
            if abs(t-previous_t) > 10: #millisecond
                list_m1.append(t)
            previous_t = t
    else:
        list_m1 = [-1]
    return list_m1

def findTheLast(condition):
    try:
        m1 = np.where(condition)[0][-1]
    except:
        m1 = -1
    finally:
        return m1

def findTheLastofAll(condition):
    try:
        m1 = np.where(condition)[0][:]
    except:
        m1 = -1
    list_m1 = []
    if m1 is not -1 and len(m1>1):
        list_m1.append(m1[-1])
        previous_t = m1[0]
        for t in reversed(m1):
            if abs(t-previous_t) > 10: ## milliseconds
                list_m1.append(t)
            previous_t = t
    else:
        list_m1 = [-1]
    return list_m1


def applyToGroupSlice(trial, time1, time2, f = lambda x:x):
    ''' you have to only give trial with marker '''
    select = (trial["time"] < time2) & (trial["time"] > time1)
    return f(trial.ix[select, ["xp", "yp"]])

def isPositionWeird(g, xlim = (0,1280), ylim=(0,1024), tol = 40.0):
    if sum(np.isnan(g["xp"])):
        return True
    elif sum( (g["xp"] > (xlim[1]+tol)) | (g["xp"] < (xlim[0]-tol)) ):
        return True
    elif sum( (g["yp"] > (ylim[1]+tol)) | (g["yp"] < (ylim[0]-tol)) ):
        return True
    else:
        return False

def createSuspectTrialsList(df, m_tab, savename = "suspect-log.csv", force_rewritting = False):
    """ The function tries to guess which trial is bad for analysis from
    the raw data "df" and the marker's table "m_tab" """

    print "\n--------------"
    print ">> Run createSuspectTrialsList on %s:"%savename
    print "--------------"
    if os.path.isfile(savename+"-suspects.csv") and not force_rewritting:
        suspected = pd.read_csv(savename+"-suspects.csv").loc[:, "Suspected"].values.tolist() ## the suspected trials are on the first columns
        print "\nList of Suspected Trial found on the Hard Drive."
        print "and contains this suspected trials:"
        print suspected
        return suspected

    ## list of trials, to select with a mask:
    print "\nNo list of suspected trial on the Hard Drive:"
    print "Analyse trials for catching suspect trials..."
    no_trials = np.unique(m_tab["TRIAL_ID"])
    pb = ProgressBar("try to find suspect trials:")
    ##print m_tab
    detail = m_tab.groupby("TRIAL_ID").apply(isSuspect, rawdata=df, progress_bar = (100./len(no_trials), pb))

    print "Merge and save the different lists in %s." % (savename+"-suspects.csv")
    ## put all of them together without duplicates:
    suspected = list(set(detail["TRIAL_ID"]))
    content = [
        suspected,
        list(set(detail.ix[detail.type == "weirdPosition", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "markersError", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "NoSaccades", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "ShortRT", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "longDuration", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "shortAmplitude", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "TooManySaccades", "TRIAL_ID"].values)),
        list(set(detail.ix[detail.type == "NotEnoughSaccades", "TRIAL_ID"].values))
    ]
    table = pd.DataFrame(content).T
    table.columns = ["Suspected", "weirdPosition", "markersError","NoSaccades", "ShortRT", "longDuration", "shortAmplitude", "TooManySaccades", "NotEnoughSaccades"]


    #print os.getcwd()
    print table
    table.to_csv(savename+"-suspects.csv")

    print "Number of suspected:", len(suspected), "\n", suspected
    print "Saved."
    pb.destroy()
    return suspected


def isSuspect(trial, rawdata=[], progress_bar = (0, None) ):
    ''' time only is usefull to just get the time marker without the positions '''
    if progress_bar[1] != None:
        progress_bar[1].step(progress_bar[0])

    columns = ["TRIAL_ID", "type"]
    trial = trial.reset_index(drop=True)
    TRIAL_ID = trial.ix[0, "TRIAL_ID"]
    type_trial = float(trial.ix[0, "TRIAL_TYPE"])
    print TRIAL_ID
    if sum(trial.marker % 2 == 1) < 1 or sum(trial.marker % 2 == 0) < 1:
        result = [TRIAL_ID, "NoSaccades"]
        print "No markers detected"
        return pd.DataFrame([result], columns = columns)
    # if sum(np.sort(trial.marker.values) != trial.marker.values) != 0:
    #     result = [TRIAL_ID, "markersError"]
    #     print "markersError: \n", trial.marker.values, np.sort(trial.marker.values)
    #     return pd.DataFrame([result], columns = columns)

    for i, line in trial.iterrows():
        #print i
        if i % 2 == 1:
            continue
        try:
            m1, m2, m3 = trial.ix[i,:], trial.ix[i+1,:], trial.ix[i+2,:]
        except:
            print "No following saccade"
            continue
        nb_saccade = i/2 + 1
        #print "NaN in saccades:", NaN_sacc
        # print "\t- make list of trials meeting the following Conditions: "
        # print "\t\t 1-list trials where there is NaN during the saccade, or out side the screen..."
        #print "\t\t 3-list trials with reaction time under 80 ms:"
        if (nb_saccade > E_SACC_TYPE[type_trial]):
            result = [TRIAL_ID, "TooManySaccades"]
            print "Too many Saccades"
            return pd.DataFrame([result], columns=columns)

        if ((i+2) == (trial.shape[0]-1)) and (nb_saccade < E_SACC_TYPE[type_trial]):
            result = [TRIAL_ID, "NotEnoughSaccades"]
            print "Not enough Saccades"
            return pd.DataFrame([result], columns=columns)

        if (m2["time"] - m1["time"]) < 80:
            result = [TRIAL_ID, "ShortRT"]
            print "shortRT"
            return pd.DataFrame([result], columns=columns)

        #print "\t\t 4-list trials where saccade duration is longer than the RT (this is suspicious)"
        if (m3["time"] - m2["time"]) > 150:
            result = [TRIAL_ID, "longDuration"]
            print "longDuration"
            return pd.DataFrame([result], columns=columns)

        ## test for a blink in the detected saccade:
        if applyToGroupSlice(rawdata[rawdata[TRIAL_COL_NAME]==TRIAL_ID], m2["time"], m3["time"], isPositionWeird):
            result = [TRIAL_ID, "weirdPosition"]
            print "weirdPosition"
            return pd.DataFrame([result], columns=columns)

    print "No problem found!"
    return pd.DataFrame(columns=columns)
        # amplitude_trials = np.sqrt((m3["xp"] - m2["xp"])**2 + (m3["yp"] - m2["yp"])**2)
        # #print "\t\t 5-list trials with a too small amplitude ( < 1/2 of target eccentricity)"
        # if amplitude_trials < 330: ## in pixels, <==> 7.5 degrees
        #     result = [TRIAL_ID, "shortAmplitude"]
        #     return pd.DataFrame([result], columns=columns)

def getMarkersFromGroup(grp):
    c1, c2, c3 = "red", "magenta", "green"
    list_markers = [[0,0,0], [c1,c2,c3]]
    if not isinstance(grp, pd.core.frame.DataFrame):
        return list_markers
    list_markers[0] = computeMarkers(grp, time_only = True)
    return list_markers


def placeMarkers(condition, position_mat, threshold_amplitude): ## to be continued
    '''
    :param condition: it is a chain of booleans which tells if we are UNDER
    the threshold to detect a saccade and if we are AFTER the stimulus onset
    :return: a dataframe with columns ["marker", "event_time"],
    marker: 0 marks the Fixation Press
            odd integer (1,3,5,...) marks the presumed start of saccades,
            even integer (2,4,6,...) marks the presumed end of saccades.
    event_time: the time of the events. The dataframe is sorted on this event_time columns.
    This sorting should lead to a marker order like 0,1,2,3,4,... if the trial is a good one and if the saccade detection works well.
    '''
    d = np.diff(condition.astype(int))
    ## the following should find the start of the saccade
    startings = np.where(d == -1)[0][:]+1 ## timing assumption (1 step == 1 ms)
    #print startings
    ## the following should find the end of saccades, but also the stimulus onset
    endings = np.where(d == 1)[0][:]+1
    #endings = np.array(((np.arange(len(endings)))*2,endings)).T
    #print endings
    if len(endings) < 1 or len(startings) < 1:
        return pd.DataFrame(np.array([(-1,-1)]), columns=["marker","event_time"])
    list_markers = [endings[0]]
    for end in endings[1:]:
        starts = startings[startings<end]
        if len(starts) > 0:
            start = starts[-1]
            #print start
            p1 = position_mat.irow(start).loc[["xp","yp"]].values
            p2 = position_mat.irow(end).loc[["xp","yp"]].values
            #print p1, p2
            distance = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
            #print distance
            if distance > threshold_amplitude:
                list_markers.append(start)
                list_markers.append(end)
    list_markers = np.vstack((np.arange(len(list_markers)), list_markers))
    list_markers = pd.DataFrame(list_markers.T, columns=["marker","event_time"])
    return list_markers



def computeMarkers(grp, time_only = False, progress_bar = (0, None)):
    ''' time_only is usefull to just get the time marker without the positions '''
    if progress_bar[1] != None:
        progress_bar[1].step(progress_bar[0])
        
    list_markers = [0,0,0]
    if not isinstance(grp, pd.core.frame.DataFrame):
        print "computeMarkers: You didn't give me a DataFrame"
        return list_markers

    ## we search the saccade's end first
    abs_velocity = np.abs(grp["vx"])+np.abs(grp["vy"])
    ## see the EyeLink 1000 manual for inspiration:
    threshold_velocity = (abs_velocity<10)
    threshold_acc = np.append(np.diff(abs_velocity)*1000 < 6000, False)
    threshold_amplitude = 150
    list_markers = placeMarkers(threshold_acc & threshold_velocity & (grp["Fixation0"]== "OFF"), grp[["xp", "yp"]], threshold_amplitude)
    ## Fixation != ON may look counter intuitive, but we actually want the data after the fixation has been pressed. (PRESSED and OFF states)

    if time_only:
        return list_markers
    else:
        mat = []
        for i, line in list_markers.iterrows():
            time_event = line["event_time"]
            marker = line["marker"]
            if time_event == -1:
                no_trial = grp[TRIAL_COL_NAME].iloc[0]
                mat.append([no_trial, -1, -1,-1,-1, -1, -1])
            else:
                try:
                    newline = grp.ix[grp["time"] == time_event, [TRIAL_COL_NAME,"TRIAL_TYPE","TRIAL_CODE","time", "xp", "yp"]].values.tolist()[0]
                    #print newline + [marker]
                    mat.append(newline + [marker])
                except Exception as e:
                    print "There may be duplicate trials on this DataFrame"
                    print e
                    print grp.ix[grp["time"] == time_event, [TRIAL_COL_NAME,"TRIAL_TYPE","TRIAL_CODE","time", "xp", "yp"]].values
                    exit()
        
        return pd.DataFrame(mat, columns = ["TRIAL_ID","TRIAL_TYPE","TRIAL_CODE","time", "xp", "yp", "marker"])


def createAMarkersTable(df, filename, output_store, f, force_rewritting = False):
    print "\n--------------"
    print ">> Run createAMarkersTable on %s"%filename
    print "--------------"
    store = pd.HDFStore(output_store)
    if ("/"+filename+"-seq" in store.keys()) and not force_rewritting:
        r = store[filename+"-seq"]
        print "Markers-Table Found in store"
        if "rejected" in r.columns:
            print "and contains rejected trials:"
            print np.unique(r.ix[r.rejected == True, "TRIAL_ID"])
        else:
            print "and doesn't contains rejected trials yet."
        return r
    else:
        print "Markers-Table NOT Found in store, proceed to its creation: "
        groups = df.groupby(df[TRIAL_COL_NAME])
        progress_bar = ProgressBar("Creation of the table ",value_max=len(groups), pos = (0, 200))
        progress_bar.setText("Create a Markers Table of eye movements...")
        step = 1 #100. / len(groups)
        r_new = groups.apply(f, progress_bar = (step, progress_bar))
        r_new  = r_new.reset_index(drop = True)
        if ("/"+filename+"-seq" in store.keys()):
            r = store[filename+"-seq"]
            if "rejected" in r.columns:
                print "A Table with tags already exists. The tags will be kept for the new table."
                r_new["rejected"] = r["rejected"]
        print "\nSave the table..."
        store[filename+"-seq"] = r_new
        store.close()
        progress_bar.destroy()
        print "Done!"
        return r_new