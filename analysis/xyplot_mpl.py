#!/bin/env python

import os, sys, argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np
import math

# Example:
# python ./xyplot_mpl.py --xdata=VG --ydata=ID VD=0.05 gm 0krad_nfet5_*.csv

parser = argparse.ArgumentParser(description='Plot')
parser.add_argument('--xdata', dest="xdata", action="store", type=str, default='x', help='xdata name')
parser.add_argument('--xmin', dest="xmin", action="store", type=float, default=None, help='xdata min')
parser.add_argument('--xmax', dest="xmax", action="store", type=float, default=None, help='xdata max')
parser.add_argument('--xlabel', dest="xlabel", action="store", type=str, default=None, help='xdata label')
parser.add_argument('--xlog', dest="xlog", action="store_true", default=False, help='xdata log')

parser.add_argument('--ydata', dest="ydata", action="store", type=str, default='y', help='ydata name')
parser.add_argument('--ymin', dest="ymin", action="store", type=float, default=None, help='ydata min')
parser.add_argument('--ymax', dest="ymax", action="store", type=float, default=None, help='ydata max')
parser.add_argument('--ylabel', dest="ylabel", action="store", type=str, default=None, help='ydata label')
parser.add_argument('--ylog', dest="ylog", action="store_true", default=False, help='ydata log')

parser.add_argument('--title', dest="title", action="store", type=str, default=None, help='Plot title')

parser.add_argument('--output', dest="output", action="store", type=str, default='foo.png', help='Output filename')
parser.add_argument('--mplstyle', dest="mplstyle", action="store", type=str, default=None, help='mplstyle file')
parser.add_argument('--dpi', dest="dpi", action="store", type=int, default=90, help='Output DPI')
parser.add_argument('--width', dest="width", action="store", type=float, default=None, help='Output width')
parser.add_argument('--height', dest="height", action="store", type=float, default=None, help='Output height')

args,unknown_args = parser.parse_known_args()
csvfiles=[]
commands=[]
where=dict()
for xx in unknown_args:
    # Look for key=value, filenames, and commands
    if '=' in xx:
        (k,v) = xx.split('=')
        try:
            where[k]=float(v)
        except:
            where[k]=v
    if os.path.exists(xx):
        csvfiles.append(xx)
    else:
        commands.append(xx)

fig,axes = plt.subplots(1,1,sharex=True)
ax=axes
if args.mplstyle:
    plt.style.use(args.mplstyle)

###############################################################################
# Read datafile
###############################################################################
#fh = open(pfile,'r')
#fh.close()
#data = {'x': [0,1,2,3,4,5], 'y': [2,3,4,5,6,7]}
numSeries=0
for csvfile in csvfiles:
    #data = np.genfromtxt(csvfile, delimiter=',',names=[args.xdata,args.ydata])
    # Extract and filter data
    data = np.genfromtxt(csvfile, delimiter=',',names=True)
    header = data.dtype.names
    for k in where:
        keycol=header.index(k)
        data = filter(lambda x: x[keycol] == where[k], data)
    xcol=header.index(args.xdata)
    ycol=header.index(args.ydata)
    data = filter(lambda x: x[xcol] != '', data)
    data = dict({args.xdata: [xx[xcol] for xx in data], args.ydata: [xx[ycol] for xx in data]})

    if len(data[args.xdata]) == 0:
        continue

    xdata=[]
    ydata=[]

    if type(data) == list: # If a list of dicts eg [{'x': 1, 'y': 2},...]
        pass
    elif type(data) == dict: # If a dict of lists {'x': [1, ...], 'y': [2, ....]}
        tdata=['']*len(data[args.xdata])
        for t in range(len(data[args.xdata])):
            tdata[t] = dict({args.xdata: data[args.xdata][t],
                             args.ydata: data[args.ydata][t]})
        data = tdata
        if len(xdata) > len(ydata):
            raise Exception("Insufficent ydata")
    else:
        raise Exception("Data file must either be a list of dicts or a dict of lists.")

    # Ensure that the data are sorted
    data = sorted(data, key=lambda x: x[args.xdata])
    xdata = [ xx[args.xdata] for xx in data ]
    ydata = [ yy[args.ydata] for yy in data ]

    for cmd in commands:
        tdata=[0]*len(ydata)
        #######################################################################
        # Transconductance
        #######################################################################
        if cmd == 'gm':
            args.ylabel = "gm (uS)"
            for i in range(1,len(ydata)-1):
                try:
                    # Central difference
                    dx = (xdata[i+1]-xdata[i-1]) #(xdata[i+1]-xdata[i])
                    dy = (ydata[i+1]-ydata[i-1]) #(ydata[i+1]-ydata[i])
                    tdata[i] = 1e6*dy/dx
                except:
                    tdata[i] = None
            ydata = tdata
    ax.plot(xdata,ydata,label=csvfile)
    numSeries=numSeries+1

if numSeries == 0:
    raise Exception("No data found")

###############################################################################
# Legend and Title
###############################################################################
handles, labels = ax.get_legend_handles_labels()
labels = [ os.path.splitext(os.path.split(x)[-1])[0] for x in labels ]
if numSeries > 1:
    plt.legend(handles,labels)
if args.title is None:
    title=', '.join(['%s=%s'%(key,str(value)) for (key,value) in where.iteritems()])
    plt.title(title)
else:
    plt.title(args.title)
    
###############################################################################
# X axis
###############################################################################
if args.xlabel:
    ax.set_xlabel(args.xlabel)
else:
    ax.set_xlabel(args.xdata)
if args.xlog:
    ax.set_xscale("log")
xmin, xmax = ax.get_xlim()
if args.xmin: xmin = args.xmin
if args.xmax: xmax = args.xmax
xspan=xmax-xmin
# Handle dates
if isinstance(xdata[0], datetime.datetime):
    if xspan.days > 3*365:
        ax.xaxis.set_major_locator(md.YearLocator())
        ax.xaxis.set_major_formatter(md.DateFormatter('%Y'))
    elif xspan.days > 60:
        ax.xaxis.set_major_locator(md.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(md.DateFormatter('%b'))
ax.set_xlim([xmin,xmax])

###############################################################################
# Y axis
###############################################################################
if args.ylabel:
    ax.set_ylabel(args.ylabel)
else:
    ax.set_ylabel(args.ydata)
if args.ylog:
    ax.set_yscale("log")
ymin, ymax = ax.get_ylim()
if args.ymin: ymin = args.ymin
if args.ymax: ymax = args.ymax
ax.set_ylim([ymin,ymax])

###############################################################################
# Output
###############################################################################
sz=fig.get_size_inches()
if args.width: sz[0] = width # in
if args.height: sz[1] = height # in
fig.set_size_inches(sz,forward=True)
plt.savefig(args.output,dpi=args.dpi)
