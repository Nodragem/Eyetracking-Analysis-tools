import numpy as np
import sklearn.neighbors as sk
from sklearn.grid_search import GridSearchCV
import scipy.stats as sc
import pandas as pd
from scipy.interpolate import interp1d
import scipy  
import scikits.bootstrap as bootstrap

def removeRT(tab, limsup = 300):
    ##print "reaction time filter: <", limsup
    selection_start = (tab.marker == 1) 
    selection_ON = (tab.marker == 0) 
    RT = tab.ix[selection_start, "time"].values[:] - tab.ix[selection_ON, "time"].values[:]
    #print RT
    if RT > limsup:
        return pd.DataFrame()
    else:
        return tab

def getHalfDistribution(halfdist, tab):
    selectDistractor = (tab["trial_type"].values == 0)  
    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)\
    & selectDistractor
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)\
    & selectDistractor
    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]
    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    data_mirroted = mirrorConditions(target_dir, data_driftcorrected)
    
    #RT = tab.ix[selection_start, "time"].values[:] - tab.ix[selection_ON, "time"].values[:]
    
    
    per_overzero = sum(data_mirroted[:,1]>0)/float(len(data_mirroted[:,1]))
    #per_underzero = sum(data_mirroted[:,1]<0)/float(len(data_mirroted[:,1]))
    
    return per_overzero #, per_underzero

def getMirrotedData(halfdist, tab, xandy=False):
    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)

    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]
       
    target_dir = tab.ix[selection_end, ["target_dir"]].values[:]
    ## let's just take Y-axis:
    if (xandy == False):
        data_mirroted = mirrorConditions(target_dir, data_driftcorrected)[:,1]
    else:
        data_mirroted = mirrorConditions(target_dir, data_driftcorrected)
    
    c = tab.ix[selection_end, ["trial_type"]].values[:]
    c = c.reshape(len(c))
    return data_mirroted, c ## c is a selector
    

def getDriftCorrectedData(halfdist, tab, xandy=False):
    selection_end = (tab.marker == 2) & selectByHalfDistance(tab, halfdist)
    selection_start = (tab.marker == 1) & selectByHalfDistance(tab, halfdist)

    data_driftcorrected = tab.ix[selection_end, ["xp","yp"]].values[:]\
                        - tab.ix[selection_start, ["xp","yp"]].values[:]

    c = tab.ix[selection_end, ["trial_type"]].values[:]
    c = c.reshape(len(c))
    return data_driftcorrected, c 
    
def findLocalMaximum(x, ycurve):
    b = ycurve[1:] < ycurve[:-1]
    c = ycurve[1:] > ycurve[:-1]
    d =  b[1:] & c[:-1]
    index = np.where(d==True)[0] + 1
    return x[index], ycurve[index]

def findLocalMinimum(x, ycurve):
    b = ycurve[1:] > ycurve[:-1]
    c = ycurve[1:] < ycurve[:-1]
    d =  b[1:] & c[:-1]
    index = np.where(d==True)[0] + 1
    return x[index], ycurve[index]

def selectByHalfDistance(df, halfdist, section = "both"): ## return a boolean mask
    if halfdist == None:
        return True
    abs_dir = abs(df["target dir"])
    selectLeft = ( abs_dir > 90) & (180-abs_dir == halfdist) ## and is like intersection
    selectRight = (abs_dir <= 90) & (abs_dir == halfdist)
    if section == "both":
        return (selectLeft | selectRight) ## or is like Union
    elif section =="left":
        return selectLeft
    elif section =="right":
        return selectRight
    else:
        return 0
  
def mirrorConditions(targ_dir, pos, section="all"): ## data has to be centered on zero
    new_pos = np.array(pos)
    if len(targ_dir.shape)>1:
        targ_dir = targ_dir.reshape(len(targ_dir))
    target_left = (abs(targ_dir) > 90)
    target_down = (targ_dir < 0)
    if section == "all":
        new_pos[target_left, 0] = -new_pos[target_left, 0]
        new_pos[target_down, 1] = -new_pos[target_down, 1]
    elif section == "horizontal":
        new_pos[target_left, 0] = -new_pos[target_left, 0]
    elif section == "vertical":
        new_pos[target_down, 1] = -new_pos[target_down, 1]
    return new_pos

def checkRejected(seqdata, trajdata, name="NO NAME"):
    if "rejected" in seqdata.columns:
        good_trials = np.unique(seqdata.ix[seqdata.rejected == False, "trial_ID"])
        seqdata = seqdata.ix[seqdata["trial_ID"].isin(good_trials), :]
        trajdata = trajdata.ix[trajdata["trial ID"].isin(good_trials), :]
        return seqdata, trajdata
    else:
        print "no rejected columns, can't work on", name
        return 0

def selectIfInRectangle(traj_grouped, center, radius, point_to_test="end"):
    if point_to_test == "end":
        p = traj_grouped[["xp","yp"]].iloc[-1,:].values
        print "\r p:", p[0], ",", p[1],
    elif point_to_test == "start":
        p = traj_grouped[["xp","yp"]].iloc[-0,:].values
    elif type(point_to_test) is int:
        p = traj_grouped[["xp","yp"]].iloc[point_to_test,:].values
    else:
        p = [0, 0]
        #return pd.DataFrame(columns=traj_grouped.columns)
        
    if len(center) < 2:
        print "A center need a x and a y coordinate ..."
    if (abs(p[0]) < (center[0] + radius[0])) and (abs(p[1]) < (center[1] + radius[1])):
        return traj_grouped


def center(tab):
    #print tab.ix[:, "xp"].head(1).values
    tab.ix[:, "xp"] = tab.ix[:, "xp"] - tab.ix[:, "xp"].head(1).values
    tab.ix[:, "yp"] = tab.ix[:, "yp"] - tab.ix[:, "yp"].head(1).values
    #tab.ix[:, "time"] = tab.ix[:, "time"] - tab.ix[:, "time"].head(1).values
    return tab

def centerC(tab, trial_type=[], center_type=[]):
    #print tab.ix[:, "xp"].head(1).values
    if len(trial_type) == 0  or len(center_type) == 0:
        tab.ix[:, "xp"] = tab.ix[:, "xp"] - tab.ix[:, "xp"].head(1).values
        tab.ix[:, "yp"] = tab.ix[:, "yp"] - tab.ix[:, "yp"].head(1).values
        tab.ix[:, "time"] = tab.ix[:, "time"] - tab.ix[:, "time"].head(1).values
    else:
        a = np.where(np.array(trial_type) == tab["trial type"].head(1).values[0])[0][0]
        tab.ix[:, "xp"] = tab.ix[:, "xp"] - tab.ix[:, "xp"].head(1).values + center[a][0]
        tab.ix[:, "yp"] = tab.ix[:, "yp"] - tab.ix[:, "yp"].head(1).values + center[a][1]
        tab.ix[:, "time"] = tab.ix[:, "time"] - tab.ix[:, "time"].head(1).values
    return tab

def select(tab, name, inf, sup):
    return tab[(tab[name] > inf) & (tab[name] < sup)]

def extractOneSaccadeRT(grp_seqdata, saccade = 2, reference = None, col_name = "RT"):
    if reference is None:
        marker_ref = (saccade - 1)*2 ## this marker is the end of the previous saccade
    else:
        marker_ref = reference
    ## here, the second selection, we take only trial with a second saccade end
    trial_nb = grp_seqdata["trial_ID"].head(1).values[0]
    #print "\r ", trial_nb,
    if np.sum(grp_seqdata.marker == marker_ref+2) != 1:
        print "\r The saccade number", saccade, "was not found for this trial: ", trial_nb,
        df = pd.DataFrame(columns=np.hstack((grp_seqdata.columns.values, [col_name])))
        #print df
        return df
    ## now we plot an histogram the reaction time of the second saccades
    df = grp_seqdata.ix[grp_seqdata.marker == marker_ref, :] ## end of the previous saccade -- all columns
    zero = grp_seqdata.ix[grp_seqdata.marker == marker_ref, "time"].values[0] ## end of the previous saccade
    start = grp_seqdata.ix[grp_seqdata.marker == marker_ref+1, "time"].values[0] ## start of the wanted saccade
    RT = start - zero
    df[col_name] = RT
    #print df
    return df


def extractOneSaccadeTraj(grp_seqdata, trajdata, saccade = 2, section="saccade"):
    marker_ref = (saccade - 1)*2 ## this marker is the end of the previous saccade
    ## here, the second selection, we take only trial with a second saccade end
    trial_nb = grp_seqdata["trial_ID"].head(1).values[0]
    #print "\r ", trial_nb,
    if np.sum(grp_seqdata.marker == marker_ref+2) != 1:
        print "\r The saccade number", saccade, "was not found for this trial: ", trial_nb,
        df = pd.DataFrame(columns=trajdata.columns)
        #print df.columns
        return df
    #print "I passed"
    zero = grp_seqdata.ix[grp_seqdata.marker == marker_ref, "time"].values[0] ## end of the previous saccade
    start = grp_seqdata.ix[grp_seqdata.marker == marker_ref+1, "time"].values[0] ## start of the wanted saccade
    end = grp_seqdata.ix[grp_seqdata.marker == marker_ref+2, "time"].values[0] ## end of the wanted saccade
    #print "I passed", zero, start, end
    if section == "saccade":
        selection = (trajdata["trial ID"] == trial_nb) & (trajdata["time"] < end) & (trajdata["time"] > start)
    elif section == "fixation":
        selection = (trajdata["trial ID"] == trial_nb) & (trajdata["time"] < start) & (trajdata["time"] > zero)
    elif section == "all":
        selection = (trajdata["trial ID"] == trial_nb) & (trajdata["time"] < end) & (trajdata["time"] > zero)
    #print trajdata.columns
    return trajdata.ix[selection,:]

def select_slice(tab, time1, time2, f = lambda x:x):
    t2 = time2.ix[time2["trial_ID"].values == tab["trial ID"].head(1).values, "time"].values[0]
    t1 = time1.ix[time1["trial_ID"].values == tab["trial ID"].head(1).values, "time"].values[0]
    #print "times are:", t1, t2
    select = (tab["time"] < t2 ) & (tab["time"] > t1)
    return f(tab.ix[select, :])

def computeAngleDeviation(tab, bins):
    if sum( (tab["phi"] > 90) | (tab["phi"] < -90) ) > 1:
        return pd.DataFrame(columns = ["dev","std"])
    f = interp1d(tab["r"], -tab["phi"], kind= "linear")
    new_radius = np.arange(tab["r"].min(),tab["r"].max(), bins)
    return pd.DataFrame({"dev": np.mean(f(new_radius)),"std": np.std(f(new_radius).std())}, index=[tab["trial ID"].head(1).values])

def meanTraj0(grouped):
    """ Deprecated"""
    meanTrajectory = -1
    numberPoints = -1
    k = 0
    for name, data in grouped:
        #print meanTrajectory
        print "\r ", k,
        if np.isnan(data["xp"].iloc[0]):
            print "NaN found!"
            continue
        if k == 0:
            meanTrajectory = data.reset_index(drop=True)
        else:
            #print data
            meanTrajectory = meanTrajectory.add(data.reset_index(drop=True)) #, fill_value=0)
        k+=1
    #print meanTrajectory
    meanTrajectory/= k
    #print meanTrajectory["trial type"]
    print "first loop passed"

    stdTrajectory = -1
    k = 0
    for name, data in grouped:
        if np.isnan(data["xp"].iloc[0]):
            continue
        diffFromMean = meanTrajectory.add(-data.reset_index(drop=True))#, fill_value=0)**2
        new_std = np.sqrt(diffFromMean.astype(float))
        if k == 0:
            stdTrajectory = new_std
        else:
            stdTrajectory = stdTrajectory.add(new_std) #, fill_value = 0)
        k+=1
    stdTrajectory /= k
    print "second loop passed"
    return meanTrajectory, stdTrajectory, k

def meanTraj(grouped, dlist = ["xp", "yp"], bootstrap = False):
    """ Compute the average trajectory of a bench of trajectories. It normalized the trajectories over time before to perform the averaging... 
    Be carefull, the option Bootstrap work only when there one dimension to average, and it changes the output format of stdTrajectories"""
    trajectories = -1
    k = 0
    for name, data in grouped:
        #print trajectories
        #print data
        print "\r Iteration ", k,
        if np.isnan(data[dlist[0]].iloc[0]):
            print "NaN found!"
            continue
        f = interp1d(data["time"].values, data[dlist].values, kind= "linear", axis=0)
        norm_time = np.linspace(data["time"].min(),data["time"].max(), 100)
        new_data = np.hstack((np.arange(100)[:,np.newaxis],f(norm_time)))
        #print new_data
        if k == 0:
            trajectories = new_data
        else:
            #print data
            trajectories = np.dstack((trajectories, new_data))
        k+=1
    #print meanTrajectory
    trajectories = trajectories.astype(float)
    k = np.sum(1-np.isnan(trajectories[0,1,:]))
    print "total trials:", k
    #print trajectories
    #raw_input("wait...")
    meanTrajectory = pd.DataFrame(np.nanmean(trajectories, axis=2),columns=["time"]+dlist)
    stdTrajectory = pd.DataFrame(np.nanstd(trajectories, axis=2),columns=["time"]+dlist)
    print "first loop passed"
    return meanTrajectory, stdTrajectory, k
    
def appendToACube(cube, new_slice):
    if (cube.shape[0] < new_slice.shape[0]):
        ## ^- we need to check that the array is big enough as we didnt normalized the time
        if len(cube.shape) > 2:
            correct_size = np.zeros((new_slice.shape[0], cube.shape[1], cube.shape[2]))
            correct_size[:] = np.nan
            correct_size[0:cube.shape[0],:,:] = cube
        else:
            correct_size = np.zeros((new_slice.shape[0], cube.shape[1]))
            correct_size[:] = np.nan
            correct_size[0:cube.shape[0],:] = cube
        cube = correct_size
    elif cube.shape[0] > new_slice.shape[0]:
        correct_size = np.zeros((cube.shape[0], new_slice.shape[1]))
        correct_size[:] = np.nan
        correct_size[0:new_slice.shape[0],:] = new_slice
        new_slice = correct_size
    return np.dstack((cube, new_slice))
    
def meanTraj1D(grouped, dlist = ["xp"], bootstraping = False, aligned = False):
    """ Compute the average trajectory of a bench of trajectories. It normalized the trajectories over time before to perform the averaging... 
    Be carefull, the option Bootstrap work only when there one dimension to average, and it changes the output format of stdTrajectories"""
    trajectories = -1
    k = 0
    for name, data in grouped:
        #print trajectories
        #print data
        print "\r Iteration ", k,
        if np.isnan(data[dlist[0]].iloc[0]):
            print "NaN found!"
            continue
        if aligned == False:
            f = interp1d(data["time"].values, data[dlist].values, kind= "linear", axis=0)
            norm_time = np.linspace(data["time"].min(),data["time"].max(), 100)
            new_data = np.hstack((np.arange(100)[:,np.newaxis],f(norm_time)))
        else:
            new_data = np.hstack((data["time"].values[:,np.newaxis], data[dlist].values))
            new_data[:,0] -= new_data[0,0]
        #print new_data
        if k == 0:
            trajectories = new_data
        else:
            if (aligned == True):
                trajectories = appendToACube(trajectories, new_data) ## safer
            else:
                trajectories = np.dstack((trajectories, new_data)) ## quicker and no need to be safe
        k+=1
    #print meanTrajectory
    ## trajectories should here looks like: (time, dlist, trials)
    trajectories = trajectories.astype(float)
    k = np.sum(1-np.isnan(trajectories[0,1,:]))
    print "total trials:", k
    #print trajectories
    #raw_input("wait...")
    meanTrajectory = pd.DataFrame(np.nanmean(trajectories, axis=2),columns=["time"]+dlist)
    if bootstraping == False:
        print "Compute the usual standard deviation..."
        stdTrajectory = np.nanstd(trajectories[:,1,:], axis = 1)*1.96/np.sqrt(np.sum(1-np.isnan(trajectories[:,0,:]), axis=1))
        stdTrajectory = np.vstack((meanTrajectory.iloc[:,1] + stdTrajectory, meanTrajectory.iloc[:,1] -stdTrajectory))
        stdTrajectory = pd.DataFrame(stdTrajectory.T, columns = ["CI_inf", "CI_sup"])
    else:
        print "Start Bootstrap of the confidence interval..."
        stdTrajectory = np.array([bootstrap.ci(trajectories[i+1, 1, :], statfunction = np.nanmean, method="bca") for i in range(trajectories.shape[0]-2) ])
        stdTrajectory = pd.DataFrame(np.vstack(((0,0), stdTrajectory, (0,0))), columns = ["CI_inf", "CI_sup"])
  
    # compute 95% confidence intervals around the mean  
    #CIs = bootstrap.ci(data=treatment1, statfunction=scipy.mean) 
    #print meanTrajectory["trial type"]
    print "first loop passed"
    return meanTrajectory, stdTrajectory, k