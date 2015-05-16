__author__ = 'c1248317'

import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import eyetools.util as util

color_bg = "#3C3C3C"

WIDTH_SCREEN = 1280
HEIGHT_SCREEN = 1024
PIXEL_PER_CENTIMETER = 500./14.3
DISTANCE = 72.0

class MonitorConverter():
    def __init__(self, width=WIDTH_SCREEN, height=HEIGHT_SCREEN, ppc = PIXEL_PER_CENTIMETER, distance = DISTANCE):
        self.width = width
        self.height = height
        self.distance = distance
        self.ppc = ppc
        self.cpp = 1./self.ppc
        self.width_cm = self.width * self.cpp
        self.height_cm = self.height * self.cpp

    def pixToDegrees(self, pixels):
        return np.degrees(np.arctan(pixels*self.cpp/self.distance))

    def degToPixels(self, degrees):
        return (self.distance * np.tan(np.radians(degrees)))*self.ppc

def toPolar(x, y, offset=0):
    return np.array((np.sqrt(x**2 + y**2), np.degrees(np.arctan2(y,x))-offset))

def toCartesian(r, phi, offset = 0):
    return r*np.cos(np.radians(phi)), r*np.sin(np.radians(phi))

def plotting(tab, ax, xname="xp", ynames=["yp"], xmin=None, xmax=None, ymin=None, ymax=None, cmap=plt.get_cmap("jet"), color = "default", zorder = 3):
    #print tab["trial ID"].head(1).values[0]
    if color == "default":
        buff = tab["time"].iloc[-1] - tab["time"].iloc[0]
        buff = (tab["time"] - tab["time"].iloc[0]) / float(buff)
        colors = buff.values.tolist()
    else:
        colors = color
    yvalues = tab[ynames].sum(1).values
    ax.scatter(tab[xname].values, yvalues, c=colors, linewidths=0, alpha=0.7, cmap = cmap, zorder=zorder)
    if all(value is not None for value in [xmin,xmax,ymin,ymax]):    
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
    return tab

def plotting1d(tab, ax, xmin, xmax, ymin, ymax, cmap=plt.get_cmap("jet"), color = "default"):
    #print tab["trial ID"].head(1).values[0]
    if color == "default":
        #buff = tab["time"].iloc[-1] - tab["time"].iloc[0]
        buff = (tab["time"] - tab["time"].iloc[0]) #/ float(buff)
        colors = buff.values.tolist()
    else:
        colors = color
    ax.scatter(buff.values, tab["yp"].values, c=colors, linewidths=0, alpha=0.7, cmap = cmap)    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    return tab

def plotting3d(tab, ax, xmin, xmax, ymin, ymax, cmap=plt.get_cmap("jet"), color = "default"):
    #print tab["trial ID"].head(1).values[0]
    if color == "default":
        buff = tab["time"].iloc[-1] - tab["time"].iloc[0]
        buff = (tab["time"] - tab["time"].iloc[0])# / float(buff)
        colors = buff.values.tolist()
    else:
        colors = color
    ax.scatter(tab["xp"].values, tab["yp"].values, buff.values, c=colors, linewidths=0, alpha=0.7, cmap = cmap)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    return tab


def plotSlowVSFast(seqdata, trajdata, xmin, xmax, ymin, ymax, d1):
    matplotlib.rcParams.update({'font.size': 15})
    matplotlib.rcParams['figure.figsize'] = (6,15)
    global color_bg

    d1 = d1
    d2 = 180.0 - d1

    criterion_seq = (seqdata["trial_type"] == 2) & \
        ((seqdata["target_dir"]==d1) | (seqdata["target_dir"]==d2))
    trials_RT = seqdata.ix[criterion_seq,["trial_ID","RTsecond"]]
    trials_slowRT = trials_RT.ix[trials_RT.RTsecond > trials_RT["RTsecond"].median(), :]
    #print trials_slowRT["RTsecond"], trials_slowRT["RTsecond"].size
    trials_fastRT = trials_RT.ix[trials_RT.RTsecond < trials_RT["RTsecond"].median(), :]
    #print trials_fastRT["RTsecond"], trials_fastRT["RTsecond"].size

    if trials_RT["RTsecond"].values.size < 1:
        fig = plt.figure()
        fig.suptitle("Data from %s \n Target direction %3.3f $^\circ$ and %3.3f $^\circ$ (NO SECOND SACCADE)."%(list_seqnames[i], d1, d2))
        plt.savefig("Detail-Direction-%d-%s.png"%(d1, list_seqnames[i]), dpi = 300)
        return 0

    fig = plt.figure()
    fig.suptitle("Data from %s \n Target direction: %3.3f$^\circ$ and %3.3f$^\circ$."%(list_seqnames[i], d1, d2))
    #print trials_RT["RTsecond"]
    rect = 0.10, 0.80, 0.80, 0.12
    ax = fig.add_axes(rect, axisbg = color_bg)
    ax.set_title("Histogram of second saccade RT")
    ax.hist(trials_RT["RTsecond"].values, bins=25, range=(0,400))
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 50)
    ax.vlines(trials_RT["RTsecond"].median(), 0, 50, colors = "red")
    criterion_traj = (trajdata["trial type"] == 2) & \
        (trajdata["stimuliON"]>0) & \
        ((trajdata["target dir"]==d1) | (trajdata["target dir"]==d2)) & \
        trajdata["trial ID"].isin(trials_slowRT.trial_ID)

    traj_slowRT = trajdata.ix[criterion_traj, ["trial ID", "time", "xp", "yp"]]
    rect = 0.10, 0.45, 0.80, 0.30
    ax = fig.add_axes(rect, axisbg = color_bg)
    #print traj_slowRT
    traj_slowRT = traj_slowRT.groupby("trial ID").apply(util.center)
    #print traj_slowRT
    traj_slowRT.groupby("trial ID").apply(plotting, ax=ax)
    ax.set_title("Slow RT Saccade Trajectories(above the median)")

    criterion_traj = (trajdata["trial type"] == 2) & \
        (trajdata["stimuliON"]>0) & \
        ((trajdata["target dir"]==d1) | (trajdata["target dir"]==d2)) & \
        trajdata["trial ID"].isin(trials_fastRT.trial_ID)

    traj_fastRT = trajdata.ix[criterion_traj, ["trial ID", "time", "xp", "yp"]]
    rect = 0.10, 0.10, 0.80, 0.30
    ax = fig.add_axes(rect, axisbg = color_bg)
    traj_fastRT  = traj_fastRT.groupby("trial ID").apply(util.center)
    traj_fastRT.groupby("trial ID").apply(plotting, ax=ax)
    ax.set_title("Fast RT Saccade Trajectories(under the median)")
    plt.savefig("Detail-Direction-%d-%s.png"%(d1, list_seqnames[i]), dpi = 300)
    return 1