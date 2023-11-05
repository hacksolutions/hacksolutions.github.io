import numpy as np
import pandas as pd
from sklearn import linear_model
import csv
import datetime
import json
import os

START = 1681776002
END = 1681862399

def findCleanData(leaks, size):
    cleanTime = [0] * (END-START)
    intervals = []
    for row in leaks:
        if (row[12] == "tEnd"):
            continue
        rangeS = int(row[11])
        rangeE = int(row[12])
        for i in range(rangeS - START, rangeE - START):
            cleanTime[i] = 1
    
    prev = 0
    s = 0
    for i,v in enumerate(cleanTime):
        if v == 0 and v != prev:
            s = i
        elif (v == 1 and v != prev) or (i == size - 5 and v==0):
            intervals.append((s, i))
            s=-1
        prev = v
    return intervals

#timeKey refers to a timestamp series which has been floored to the nearest minute
def poolByMinute(frame, dataKeys, timeKey):
    pooledFrame = pd.DataFrame(columns=dataKeys)
    for n in dataKeys:
        sum = 0
        cnt = 0
        time = int(floorMultMin(frame[timeKey][0]))
        for i,v in enumerate(frame[n]):
            if time != floorMultMin(frame[timeKey][i]):
                if (floorMultMin(frame[timeKey][i]) - time > 60):
                    for j in range(floorMultMin(time), floorMultMin(frame[timeKey][i]), 60):
                        pooledFrame.at[int((j-START)/60), n] = sum/cnt
                pooledFrame.at[floorMultMin(time - START)/60, n] = sum/cnt
                cnt = 0
                sum = 0
                time = floorMultMin(frame[timeKey][i])
            cnt+=1
            sum+=frame[n][i]
    return pooledFrame

def buildDeltaFrame(X, names):
    deltaFrame = pd.DataFrame()
    for n in names:
        deltaFrame[n] = (X[n].diff()).abs()
    return deltaFrame

def buildDeltaFrameY(Y, names):
    deltaFrame = pd.DataFrame(index=Y.index)
    deltaFrame["Concentration"] = np.zeros(len(Y))
    print(Y)
    print(deltaFrame["Concentration"])
    for n in names:
        deltaFrame["Concentration"] = deltaFrame["Concentration"].add(Y[n])
    deltaFrame["Concentration"] = deltaFrame["Concentration"].div(len(names))
    deltaFrame["Concentration"] = deltaFrame["Concentration"].diff().abs()
    return deltaFrame

def buildRegression(X, Y):
    regr = linear_model.LinearRegression()
    regr.fit(X,Y)
    return regr

def getEpoch(inp):
    #4/18/2023  12:00:00 AM
    tmp = inp.split(" ")
    big = tmp[0].split("/")
    small = tmp[1].split(":")
    epoch = int((datetime.datetime(int(big[2]),int(big[0]),int(big[1]), hour = int(small[0]), minute= int(small[1]))).replace(tzinfo=datetime.timezone.utc).timestamp())
    epoch = floorMult(epoch, 60)
    return epoch

def getErrorRanges(errorFrame,range):
    acceptable = range
    ranges = []
    s=-1
    prevErr = False
    for i,v in enumerate(errorFrame):
        if (v > acceptable and prevErr == False):
            s = i
        elif (v < acceptable and prevErr == True):
            ranges.append((s, i))
            s = -1
        prevErr = v>acceptable
    return ranges


def floorMultMin(n):
    return n - (n%60)

def floorMult(n,mult):
    return n - (n%mult)

def normalize(X):
    return (X-X.min())/(X.max()-X.min())

def writeLeakDetections(y_labels, y_actual, y_prediction, range):
    rangeDict = {}
    for l in y_labels:
        print(y_prediction[0])
        print(y_actual[l])
        errorFrame = y_prediction[0].sub(y_actual[l]).abs()
        print(errorFrame)
        ranges = getErrorRanges(errorFrame, range)
        outFrame = pd.DataFrame(columns=["actual", "predicted", "upper"])
        outFrame["predicted"] = y_prediction[0]
        outFrame["actual"] = y_actual[l]
        outFrame["upper"] = y_prediction[0] + range
        #outFrame.to_csv("//csv//" + (l.split('_')[0] + (l.split('_'))[1] + l.split('_')[2])+"_graph.csv")
        rangeDict[l.split('_')[0] + (l.split('_'))[1] + l.split('_')[2]] = ranges
    print(json.dumps(rangeDict))
    with open(os.path.dirname(os.path.realpath(__file__)) + "\\json\\leakTimes.json", 'w') as f:
        json.dump(rangeDict, f)
        

    

weatherSize = 0
sensorSize = 0

x_params = ["Barometric_Pressure","Humidity","Temperature","Wind_Directior","Wind_Speed"]
y_params = []
x_params_trimmed = ["Barometric_Pressure","Humidity","Temperature"]
x_params_avg = ["Barometric_Pressure_AVG","Humidity_AVG","Temperature_AVG","Wind_Directior_AVG","Wind_Speed_AVG"]
x_params_avg_trimmed = ["Barometric_Pressure_AVG","Humidity_AVG","Temperature_AVG"]

if __name__ == "__main__":
    weather = open("weather_data.csv", newline="")
    concentration = open("sensor_readings.csv", newline="")
    leaks = open("leak_locations_and_rate.csv", newline="")

    w_reader = csv.reader(weather,delimiter=',')
    c_reader = csv.reader(concentration, delimiter=',')
    l_reader = csv.reader(leaks, delimiter=',')

    weatherFrame = pd.read_csv("weather_data.csv", sep = ',', header=0)
    weatherFrame['timestamp'] = weatherFrame['timestamp'].apply(getEpoch)

    fullFrame = pd.read_csv("sensor_readings.csv", sep = ',', header=0, low_memory=False)
    fullFrame['timestamp'] = fullFrame['timestamp'].apply(floorMultMin)
    y_params=fullFrame.columns.values[2:]

    sensorSize = len(weatherFrame)

    cleanIntervals  = findCleanData(l_reader, sensorSize)

    

    cleanIntervalsAdj = (int(cleanIntervals[1][0] / 60) ,int(cleanIntervals[1][1] / 60))

    print(cleanIntervalsAdj)

    averagedWeatherFrame = poolByMinute(weatherFrame, x_params, "timestamp")
    averagedFullFrame = poolByMinute(fullFrame, y_params, "timestamp")

    print(weatherFrame['timestamp'].diff().max())
    print(fullFrame['timestamp'].diff().max())
    print(averagedWeatherFrame)
    print(averagedFullFrame)

    diffWeatherFrame = buildDeltaFrame(averagedWeatherFrame, x_params_trimmed)
    diffSensorsFrame = buildDeltaFrame(averagedFullFrame, y_params)
    diffFullFrame = buildDeltaFrameY(averagedFullFrame, y_params)

    print("Post Delta --------------------------------")
    print(diffWeatherFrame)
    print(diffSensorsFrame)
    print(diffFullFrame)

    predModel = buildRegression(diffWeatherFrame[x_params_trimmed].loc[(cleanIntervalsAdj[0]):(cleanIntervalsAdj[1])], diffFullFrame["Concentration"].loc[(cleanIntervalsAdj[0]):(cleanIntervalsAdj[1])])

    predicted = pd.DataFrame(predModel.predict(diffWeatherFrame[1:]))
    actual = diffFullFrame[1:]

    print(predicted)
    print(actual)

    stdev = (predicted[0].loc[cleanIntervalsAdj[0]: cleanIntervalsAdj[1]].sub(actual["Concentration"]).loc[cleanIntervalsAdj[0]:cleanIntervalsAdj[1]]).std()

    print(stdev)

    writeLeakDetections(fullFrame.columns.values[2:], diffSensorsFrame, predicted, stdev*20)

    print(averagedWeatherFrame.loc[444, "Wind_Directior"])




    #print(diffFullFrame["Concentration"].loc[(cleanIntervalsAdj[0]):(cleanIntervalsAdj[1])])
    #stdev = diffFullFrame["Concentration"].loc[(cleanIntervalsAdj[0]):(cleanIntervalsAdj[1])].std()

    
