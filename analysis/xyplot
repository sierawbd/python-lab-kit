#!/bin/env python

import os, sys, argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import scipy.integrate
import numpy as np
import math
from parameter_extraction import *

# Example:
# python ./xyplot_mpl.py --xdata=VG --ydata=ID VD=0.05 gm 0krad_nfet5_*.csv

parser = argparse.ArgumentParser(description='Plot')
parser.add_argument('--xdata', dest="xdata", action="store", type=str, default='x', help='xdata name')
parser.add_argument('--xmin', dest="xmin", action="store", type=float, default=None, help='xdata min')
parser.add_argument('--xmax', dest="xmax", action="store", type=float, default=None, help='xdata max')
parser.add_argument('--xlabel', dest="xlabel", action="store", type=str, default=None, help='xdata label')
parser.add_argument('--xlog', dest="xlog", action="store_true", default=False, help='xdata log')
parser.add_argument('--xscale', dest="xscale", action="store", type=float, default=1, help='xdata scale')

parser.add_argument('--ydata', dest="ydata", action="store", type=str, default='y', help='Comma separated list of ydata names')
parser.add_argument('--ymin', dest="ymin", action="store", type=float, default=None, help='ydata min')
parser.add_argument('--ymax', dest="ymax", action="store", type=float, default=None, help='ydata max')
parser.add_argument('--ylabel', dest="ylabel", action="store", type=str, default=None, help='ydata label')
parser.add_argument('--ylog', dest="ylog", action="store_true", default=False, help='ydata log')
parser.add_argument('--yscale', dest="yscale", action="store", type=float, default=1, help='ydata scale')

parser.add_argument('--title', dest="title", action="store", type=str, default=None, help='Plot title')
parser.add_argument('--caption', dest="caption", action="store", type=str, default='', help='Figure caption')

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

if args.mplstyle:
    plt.style.use(args.mplstyle)        
fig,axes = plt.subplots(1,1,sharex=True)
ax=axes

###############################################################################
# Read datafile
###############################################################################
numSeries=0
for csvfile in csvfiles:
    data=read_data(csvfile,args.xdata,(args.ydata).split(','),where)
    xdata=data[0]
    xscaleddata=[ xx*float(args.xscale) for xx in xdata ]
    # Aggregating commands
    for cmd in commands:
        if cmd == "avg":
            avgvals=[0]*len(xdata)
            for i in range(len(xdata)):
                avgvals[i] = sum([ ydata[i] for ydata in data[1:] ]) / \
                             float(len(data)-1)
            data = [xdata,avgvals]
        if cmd == "min":
            minvals=[0]*len(xdata)
            for i in range(len(xdata)):
                minvals[i] = min([ ydata[i] for ydata in data[1:] ])
            data = [xdata,minvals]
        if cmd == "max":
            maxvals=[0]*len(xdata)
            for i in range(len(xdata)):
                maxvals[i] = max([ ydata[i] for ydata in data[1:] ])
            data = [xdata,maxvals]

    for ydata in data[1:]:
        for cmd in commands:
            tdata=[0]*len(ydata)
            ###################################################################
            # Transconductance
            ###################################################################
            if cmd == 'gm':
                args.ylabel = "gm (uS)"
                ydata = [1e6*x for x in gm(xdata,ydata)][1:-1]
                xdata = xdata[1:-1]
            if cmd == 'abs':
                args.ylabel = "abs(%s)" %(args.ylabel)
                ydata = [abs(x) for x in ydata]
            if cmd == 'integrate':
                ydata = scipy.integrate.cumtrapz(ydata,xdata,initial=0)
            if cmd == 'sum':
                ydata = scipy.integrate.cumtrapz(ydata,dx=1,initial=0)
            if cmd == 'rsum':
                ydata = reversed(scipy.integrate.cumtrapz(list(reversed(ydata)),dx=1,initial=0))
        yscaleddata = [ yy*float(args.yscale) for yy in ydata ]
        ax.plot(xscaleddata, yscaleddata,label=csvfile)
        numSeries=numSeries+1
        
if numSeries == 0:
    raise Exception("No data found")

###############################################################################
# Legend and Title
###############################################################################
handles, labels = ax.get_legend_handles_labels()
labels = [ os.path.splitext(os.path.split(x)[-1])[0] for x in labels ]
prefix_len=len(os.path.commonprefix(labels))
#labels = [ x[prefix_len:] for x in labels]

if numSeries > 1 and numSeries <= 10:
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
if args.width: sz[0] = args.width # in
if args.height: sz[1] = args.height # in
fig.set_size_inches(sz,forward=True)
plt.savefig(args.output,dpi=args.dpi)
exit()

###############################################################################
# Metadata
###############################################################################
# Use PIL to save some image metadata
from PIL import Image
from PIL import PngImagePlugin
im = Image.open(args.output)
meta = PngImagePlugin.PngInfo()
for x in where:
    meta.add_text(x, str(where[x]))
meta.add_text('caption',args.caption)
im.save(args.output, "png", pnginfo=meta)

#im2 = Image.open(args.output)
#print im2.info
