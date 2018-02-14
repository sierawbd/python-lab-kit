#!/bin/env python
import numpy as np
import math

def read_data(csvfile,xdata,ydata,where):
    data = np.genfromtxt(csvfile, delimiter=',',names=True)
    header = data.dtype.names
    for k in where:
        keycol=header.index(k)
        data = filter(lambda x: x[keycol] == where[k], data)
    xcol=header.index(xdata)
    print csvfile, header, ydata
    ycols=[header.index(yy) for yy in ydata]
    data = filter(lambda x: x[xcol] != '', data)
    # Want x list, y1 list, y2 list
    retdata = [ [xx[xcol] for xx in data] ]
    for i in range(len(ycols)):
        retdata.append( [yy[ycols[i]] for yy in data ] )
    return retdata
    
    print [[xx[ycol] for ycol in ycols] for xx in data]
    data = dict({xdata: [xx[xcol] for xx in data], ydata: [[xx[ycol] for ycol in ycols] for xx in data]})

    if len(data[xdata]) == 0:
        return (None,None)

    if type(data) == list: # If a list of dicts eg [{'x': 1, 'y': 2},...]
        pass
    elif type(data) == dict: # If a dict of lists {'x': [1, ...], 'y': [2, ....]}
        tdata=['']*len(data[xdata])
        for t in range(len(data[xdata])):
            tdata[t] = dict({xdata: data[xdata][t],
                             ydata: data[ydata][t]})
        data = tdata
        #if len(data[xdata]) > len(data[ydata]):
        #    raise Exception("Insufficent ydata")
    else:
        raise Exception("Data file must either be a list of dicts or a dict of lists.")

    # Ensure that the data are sorted
    data = sorted(data, key=lambda x: x[xdata])
    return ([ xx[xdata] for xx in data ],[ yy[ydata] for yy in data ])

def peak(xdata,ydata):
    return max(zip(xdata,ydata),key=lambda x: x[1])

def gm(xdata,ydata):
    """Returns transconductance (S) array for xy data"""
    tdata = [0]*len(xdata)
    for i in range(1,len(xdata)-1):
        dx = (xdata[i+1]-xdata[i-1]) #(xdata[i+1]-xdata[i])
        dy = (ydata[i+1]-ydata[i-1]) #(ydata[i+1]-ydata[i])
        try:
            tdata[i] = dy/dx
        except:
            tdata[i] = None
    return tdata

def peak_gm(xdata,ydata):
    """Returns the location, current, and peak gm value"""
    tdata=gm(xdata,ydata)
    return max(zip(xdata,ydata,tdata),key=lambda x: x[2])

def SS(xdata,ydata):
    # Find the datapoints for 10nA and 100pA
    (v1,i1)=min(zip(xdata,ydata),key=lambda xx: abs(xx[1]-100e-12))
    (v2,i2)=min(zip(xdata,ydata),key=lambda xx: abs(xx[1]-10e-9))
    return 1000*(v2-v1)/(math.log(i2,10)-math.log(i1,10)) # mV/decade

def xinterp(xdata,ydata,x0):
    for i in range(0,len(xdata)):
        if xdata[i] <= x0 and xdata[i+1] > x0:
            return ydata[i] + (x0-xdata[i])*(ydata[i+1]-ydata[i])/(xdata[i+1]-xdata[i])
    raise Exception("Could not interpolate")

def yinterp(xdata,ydata,y0):
    for i in range(0,len(xdata)):
        if ydata[i] <= y0 and ydata[i+1] > y0:
            return xdata[i] + (y0-ydata[i])*(xdata[i+1]-xdata[i])/(ydata[i+1]-ydata[i])
    return None
    
def vth(xdata,ydata,method='cc',Vd=None,W=None,L=None):
    if method == 'elf':        
        (Vappx,Id_appx,gm_peak) = peak_gm(xdata,ydata)
        Vcross = Vappx - (Id_appx)/gm_peak
        return Vcross - 0.5*Vd
    if method == 'cc':
        # Find the datapoint nearest NIds=10nA
        Ids=(10e-9)/(W/float(L))
        return yinterp(xdata,ydata,Ids)
