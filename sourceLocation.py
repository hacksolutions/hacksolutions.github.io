import json
import os
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

cdict = {'red':   [(0.0,  1, 1),
                   (0.5,  1, 1),
                   (1.0,  1, 1)],

         'green': [(0.0,  0.0, 0.0),
                   (1.0,  0.0, 0.0)],

         'blue':  [(0.0,  0.0, 0.0),
                   (1.0,  0.0, 0.0)],
                   
         'alpha':  [(0.0,  0.0, 0.0),
                   (1.0,  0.5, 0.5)],
                   }

def plume(s_x, s_y, t_x, t_y, windspeed, windDir):
    x = t_x - s_x
    y = t_y - s_y
    alpha = math.radians(windDir)
    a_x = x * math.cos(alpha) - y * math.sin(alpha)
    a_y = x * math.sin(alpha) - y * math.cos(alpha)
    return plumeModel(a_x, a_y, windspeed)

def plumeModel(x, y, windspeed):
    if x <= 0:
        return 0
    sigY = .04738 * x + 125.6
    sigZ = .02090 * x + 120.2
    eComp = math.exp(-((1/(2*sigZ))+((math.pow(y,2))/(2*sigY)))) 
    return (1/(math.pi*windspeed*sigY*sigZ)) * eComp

def mapPlume(s_x, s_y, windspeed, windDir, n, m):
    colorgrad = mpl.colors.LinearSegmentedColormap("Concentration", cdict)
    plumeMap = np.zeros((m, n))
    for i,v in enumerate([x / 10.0 for x in range(5, n*10, 10)]):
        for j,k in enumerate([x / 10.0 for x in range(5, m*10, 10)]):
            plumeMap[j, i] = plume(s_x, s_y, v, k, windspeed, windDir)
    plt.rcParams["figure.figsize"] = [7.00, 3.50]
    data = plumeMap
    plt.imshow(data, cmap=colorgrad)
    plt.axis('off')
    plt.savefig(os.path.dirname(os.path.realpath(__file__)) + '\\img\\' + str(s_x) + "_" + str(s_y) + "_" + str(windDir) + ".png")
    plt.show()

SOURCE_X = 25.7
SOURCE_Y = 32.1
WIND_DIRECTION = 246.93207131333335
GRANULARITY = 200

if __name__ == "__main__":
    mapPlume(SOURCE_X, SOURCE_Y, 1, WIND_DIRECTION, GRANULARITY, GRANULARITY/2)
