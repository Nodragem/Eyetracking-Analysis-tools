import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("WxAgg")
import matplotlib.pyplot as plt


class ProgressBar():
    def __init__(self, text_to_display, value_max = 100, pos = (None,None)):

        self.value_max = value_max
        self.fig = plt.figure(figsize=(10, 1))
        if pos[0] is not None:
            thismanager = plt.get_current_fig_manager()
            thismanager.window.SetPosition((pos[0], pos[1]))
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
        plt.show()
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
        self.list_keys = np.unique(df["trial ID"])
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
        self.origin_col = "black"
        self.orig_position = None
        if (self.markers_table is not None) and ("rejected" in self.markers_table.columns):
            print "Markers_table retrieved from Hard drive..."
            select = self.markers_table["rejected"] == True
            self.tagged_trials = np.unique(self.markers_table.ix[select, "trial_ID"]).tolist()
        else:
            self.tagged_trials = []
        self.detected_trials = []
        self.selected_axe = None
        self.nb_page = self.nb_trials/self.n_plot + 1
        
    def getMarks(self, trial_nb, table): ## get Markers from the Markers Table
        c1, c2, c3 = "red", "magenta", "green"
        list_markers = [[0,0,0], [c1,c2,c3]]
        if (trial_nb < 1) or (table is None):
            return list_markers
        select = (table["trial_ID"] == trial_nb)
        list_markers[0] = table.ix[select, ["time"]].values
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
            self.list_ax.append(ax)
        self.cid = self.fig.canvas.mpl_connect('key_press_event', self.onPressedKey)
        self.mid = self.fig.canvas.mpl_connect('button_press_event', self.onMouseClick)
        #select  = (self.df["trial ID"] <= end) &  (self.df["trial ID"] >= start)
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
            if self.orig_position != None:
                ax.set_position(self.orig_position)
                for axis in event.canvas.figure.axes:
                    axis.set_visible(True)
                self.orig_position = None
            else:
                # On left click, zoom the selected axes
                self.orig_position = ax.get_position()
                ax.set_position([0.1, 0.1, 0.85, 0.85])
                for axis in event.canvas.figure.axes:
                    # Hide all the other axes...
                    if axis is not ax:
                        axis.set_visible(False)
            
        else:
            # No need to re-draw the canvas if it's not a left or right click
            return
        event.canvas.draw()
        
    def getKeyTrial(self, selected_axe):
        if (self.selected_axe != None):
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
            print "right"
            self.current_page = (self.current_page + 1) % self.nb_page
        elif (event.key == "a"):
            self.current_page = (self.current_page - 1) % self.nb_page
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
            rs["rejected"] = np.array([False, False, False]*len(np.unique(rs["trial_ID"]))).T
            ## be carefull, trial ID is now trial_ID:
            rs.ix[rs["trial_ID"].isin(self.tagged_trials), "rejected"] = True
            rs["Condition"] = "default"
            print "Save the file as %s in %s"%(self.name+"-seq", self.output_store)
            store[self.name+"-seq"] = rs
            store.close()
            #plt.suptitle(self.name+"-saved")
            self.fig_title.set_text(self.name+"-saved")
            print "Tagged trials saved!"
            return 1
        
    def getInfoForPage(self, n):
        start = ( (n-1) * self.n_plot )%self.nb_trials + 1  ## for example start = 161
        end = start + self.n_plot - 1  # 161 + 50 - 1 = 210
        if end > self.nb_trials:
            end = self.nb_trials 
        totag = np.in1d(self.list_keys[(start-1):end], self.tagged_trials)
        toshade = np.in1d(self.list_keys[(start-1):end], self.detected_trials)
        print "Page %d show the trials: %d -- %d "%(n, start, end)
        #select  = (self.df["trial ID"] <= end) &  (self.df["trial ID"] >= start)
        select  = self.df["trial ID"].isin(self.list_keys[(start-1):end])  # don't forget the start starts at 1
        return start, end, select, totag.tolist(), toshade.tolist()
        
    def drawEyeMovement(self, df, page_number):
        ''' m1, m2 and m3 try to mark the target appearance, the saccade's start and saccade's end'''

        start, end, select, tagged, detected = self.getInfoForPage(page_number)
        print "tagged: ", tagged
        index = 0
        for key, grp in df.ix[select, :].groupby("trial ID"):  # not really pretty to not check the size
            self.origin_col = "black"  # we have to reset the origin color as we are not on the same page anymore
            key = int(key)
            ax = self.list_ax[index % self.n_plot]
            iter_lines = iter(ax.get_lines())
            iter_lines.next().set_data(grp["time"].values, grp[self.var[0]].values)
            iter_lines.next().set_data(grp["time"].values, grp[self.var[1]].values)
            list_markers = self.getMarks(key, self.markers_table)
            for m in list_markers[0]:
                iter_lines.next().set_data((m,m), (0, 1500)) #ax.get_ylim())
            ax.set_axis_bgcolor((1,1,1))
            ax.set_title("Key %d"%key, color = "black")
            index += 1
            
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

def findTheLast(condition):
    try:
        m1 = np.where(condition)[0][-1]
    except:
        m1 = -1
    finally:
        return m1


def applyToGroupSlice(trial, mtab1, mtab2, f = lambda x:x):
    ''' you have to only give trial with marker '''
    no_trial = trial["trial ID"].iloc[0]

    t1 = mtab1.ix[mtab1["trial_ID"] == no_trial, "time"].iloc[0]
    t2 = mtab2.ix[mtab2["trial_ID"] == no_trial, "time"].iloc[0]
    #print "\r trial %d from %d to %d"%(no_trial, t1, t2),
    select = (trial["time"] < t2) & (trial["time"] > t1)
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
    no_trials = np.unique(m_tab["trial_ID"])

    print "\t- extract the time markers (Stim ON, sacc. start, sacc. end)"
    m1 = m_tab.ix[:, ["trial_ID", "time"]].loc[m_tab.marker == 0].reset_index()  ## target ON
    m2 = m_tab.ix[:, ["trial_ID", "time"]].loc[m_tab.marker == 1].reset_index()
    m3 = m_tab.ix[:, ["trial_ID", "time"]].loc[m_tab.marker == 2].reset_index()  ## end of saccade for each trial

    print "\t- extract the start position, end position and the saccade's amplitude:"
    p2 = m_tab.ix[:, ["xp", "yp" ]].loc[m_tab.marker == 1].values
    p3 = m_tab.ix[:, ["xp", "yp" ]].loc[m_tab.marker == 2].values
    ## we use numpy cause pandas is fucking annoying with its index:
    ## p2 + p3 would give NaN cause they have different indexing
    amp_trials = np.sqrt( (p3[:,0] - p2[:,0])**2 + (p3[:,1] - p2[:,1])**2 )

    print "\t- make list of trials meeting the following Conditions: "
    print "\t\t 1-list trials where there is NaN during the saccade, or out side the screen..."
    mask1 = df.groupby("trial ID").apply(applyToGroupSlice, mtab1 = m2, mtab2 = m3, f = isPositionWeird)
    NaN_sacc = no_trials[mask1.values].tolist()
    #print "NaN in saccades:", NaN_sacc

    print "\t\t 2-list trials which failed to have markers from computeMarkers:"
    nomark_sacc = m_tab.ix[m_tab.time == -1, "trial_ID"].values.tolist()
    #print "Marker missing:", nomark_sacc

    print "\t\t 3-list trials with reaction time under 80 ms:"
    mask2 = (m2["time"] -m1["time"]) < 80
    shortRT_sacc = no_trials[mask2.values].tolist()
    #print "Short RT:", shortRT_sacc

    print "\t\t 4-list trials where saccade duration is longer than the RT (this is suspicious)"
    mask3 = (m2["time"]-m1["time"]) < (m3["time"]-m2["time"])
    double_sacc = no_trials[mask3.values].tolist()
    #print "Double Sacc.:", double_sacc

    print "\t\t 5-list trials with a too small amplitude ( < 1/2 of target eccentricity)"
    tooshort_sacc = no_trials[amp_trials < 330].tolist() ## in pixels, <==> 7.5 degrees
    #print "Too small:", tooshort_sacc

    print "Merge and save the different lists in %s." % (savename+"-suspects.csv")
    ## put all of them together without duplicates:
    suspected = list(set(NaN_sacc + nomark_sacc + shortRT_sacc + double_sacc + tooshort_sacc))
    table = pd.DataFrame([suspected, NaN_sacc, nomark_sacc, shortRT_sacc, double_sacc, tooshort_sacc]).T
    table.columns = ["Suspected", "NaNduringSacc", "MarkerMissing", "ShortRT", "SaccDurationOnRT", "smallAmplitude"]
    print os.getcwd()
    table.to_csv(savename+"-suspects.csv")

    print "Number of suspected:", len(suspected), "\n", suspected
    print "Saved."

    return suspected


def getMarkersFromGroup(grp):
    c1, c2, c3 = "red", "magenta", "green"
    list_markers = [[0,0,0], [c1,c2,c3]]
    if not isinstance(grp, pd.core.frame.DataFrame):
        return list_markers
    list_markers[0] = computeMarkers(grp, time_only =True)
    return list_markers
    
def computeMarkers(grp, time_only = False, progress_bar = (0, None)):
    ''' time only is usefull to just get the time marker without the positions '''
    if progress_bar[1] != None:
        progress_bar[1].step(progress_bar[0])
        
    list_markers =  [0,0,0]
    if not isinstance(grp, pd.core.frame.DataFrame):
        print "computeMarkers: You didn't give me a DataFrame"
        return list_markers
    
    m1  = list_markers[0] = findTheFirst(grp["stimuliON"]>0)
    if m1 != -1:
        #print m1, grp.shape
        base_pos = grp.irow(m1).loc[["xp","yp"]].values
        #print "Baseline:", base_pos
        ## we search the saccade's end first
        abs_velocity = np.abs(grp["vx"])+np.abs(grp["vy"])
        ## sse the EyeLink 1000 manual for inspiration:
        threshold_velocity = (abs_velocity<10)
        threshold_amplitude = np.sqrt((grp["xp"]-base_pos[0])**2+(grp["yp"]-base_pos[1])**2) > 44 ## pixels, which is near to 1.0 degrees
        threshold_acc = np.append(np.diff(abs_velocity)*1000 < 6000, False)
        m2 = list_markers[2] = findTheFirst( threshold_acc & threshold_velocity & threshold_amplitude & (grp["stimuliON"]>0))
    else:
        m2 = list_markers[2] = -1

    if m2 != -1:
        ## then we search the start of this saccade
        ## m2 already fit with a time in ms as the eyetracker was at 1000Hz
        threshold_velocity = (np.abs(grp["vx"])+np.abs(grp["vy"])<30)
        threshold_acc = np.append(np.diff(abs_velocity)*1000 < 6000, False)
        threshold_amplitude = np.sqrt((grp["xp"]-base_pos[0])**2+(grp["yp"]-base_pos[1])**2) < 18 ## 0.30 degrees
        list_markers[1] = findTheLast(threshold_acc & threshold_velocity & threshold_amplitude &(grp["time"]<m2))
    else: ## if m2 doesn't exist, there is no sense to find m3
        list_markers[1] = -1

    if time_only:
        return np.array(list_markers)
    else:
        mat = []
        for m in list_markers:
            if m == -1:
                no_trial = grp["trial ID"].iloc[0]
                mat.append([no_trial, -1, -1,-1,-1, -1])
            else:
                try:
                    mat.append( *grp.ix[grp["time"] == m, ["trial ID","trial type","target dir","time", "xp", "yp"]].values)
                except Exception as e:
                    print "There may be duplicate trials on this DataFrame"
                    print e
                    print grp.ix[grp["time"] == m, ["trial ID","trial type","target dir","time", "xp", "yp"]].values
                    exit()
        
        return pd.DataFrame(mat, columns = ["trial_ID","trial_type","target_dir","time", "xp", "yp"])


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
            print np.unique(r.ix[r.rejected == True, "trial_ID"])
        else:
            print "and doesn't contains rejected trials yet."
        return r
    else:
        print "Markers-Table NOT Found in store, proceed to its creation: "
        groups = df.groupby(df["trial ID"])
        progress_bar = ProgressBar("Creation of the table ",value_max=len(groups), pos = (0, 200))
        progress_bar.setText("Create a Markers Table of eye movements...")
        step = 1 #100. / len(groups)
        r_new = groups.apply(f, progress_bar = (step, progress_bar))
        nb_trials = len(np.unique(r_new["trial_ID"]))
        r_new["marker"] = np.array([0, 1, 2]*nb_trials).T
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