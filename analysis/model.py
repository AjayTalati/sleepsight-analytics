# !/bin/python3

import datetime
import numpy as np
import pandas as pd

class ModelPrep:

    @property
    def discretisedStationarySymptomScoreTable(self):
        return self.__discretisedStationarySymptomScoreTable

    @discretisedStationarySymptomScoreTable.setter
    def discretisedStationarySymptomScoreTable(self, dSST):
        self.__discretisedStationarySymptomScoreTable = dSST

    @property
    def discretisedRawSymptomScoreTable(self):
        return self.__discretisedRawSymptomScoreTable

    @discretisedRawSymptomScoreTable.setter
    def discretisedRawSymptomScoreTable(self, dSST):
        self.__discretisedRawSymptomScoreTable = dSST

    def __init__(self):
        pass

    def discretiseSymtomScore(self, stationarySymptom, rawSymptom):
        m = round(np.mean(stationarySymptom['total']), 1)
        sd = round(np.std(stationarySymptom['total']), 2)
        minorIdx = stationarySymptom['total'] >= (m + sd)
        labels = ['major'] * len(minorIdx)
        for i in np.where(minorIdx == True)[0]:
            labels[i] = 'minor'
        labelsTable = pd.DataFrame(labels)
        labelsTable.columns = ['label']
        labelsTable.index = stationarySymptom.index
        self.discretisedStationarySymptomScoreTable = pd.concat([stationarySymptom, labelsTable], axis=1)
        self.discretisedRawScoreTable = pd.concat([rawSymptom, labelsTable], axis=1)


class GpModel:

    def __init__(self, xFeatures, yFeature, dayDivisionHour=0):
        self.divTime = datetime.time(hour=dayDivisionHour)
        self.xFeatures = xFeatures
        self.yFeature = yFeature

    def submitData(self, active, passive):
        self.activeData = active
        self.passiveData = passive
        self.yData = self.activeData[['datetime', self.yFeature]]
        xSelection = ['timestamp'] + self.xFeatures
        self.xData = self.passiveData[xSelection]

    def createIndexTable(self):
        self.indexDict = []
        self.extractDateIdxsFromYData()
        self.extractDateIdxsFromXDataBasedOnY()

    def extractDateIdxsFromYData(self):
        for i in range(len(self.yData)):
            entry = {'index': i}
            entry['y'] = float(self.yData[i:i+1][self.yFeature])
            startDate, endDate = self.determineDatesFromYData(i)
            entry['dateStart'] = startDate
            entry['dateEnd'] = endDate
            self.indexDict.append(entry)

    def determineDatesFromYData(self, index):
        dt_str = list(self.activeData[index:(index+1)]['datetime'])[0]
        dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
        dtEnd = dt.replace(hour=self.divTime.hour, minute=0)
        tDay = datetime.timedelta(days=1)
        tMin = datetime.timedelta(minutes=1)
        dtStart= dtEnd - tDay + tMin
        return (dtStart, dtEnd)

    def extractDateIdxsFromXDataBasedOnY(self):
        idxStart = 0
        idxEnd = 0
        currentTableIndex = 0
        for i in range(len(self.xData)):
            dateStart = self.indexDict[currentTableIndex]['dateStart']
            dateEnd = self.indexDict[currentTableIndex]['dateEnd']
            dateXDataStr = list(self.xData[i:(i + 1)]['timestamp'])[0]
            dateXData = datetime.datetime.strptime(dateXDataStr, '%Y-%m-%d %H:%M')
            if dateXData <= dateStart and dateXData < dateEnd:
                idxStart = i
            if dateXData <= dateEnd:
                idxEnd = i
            if dateXData == dateEnd or i == (len(self.xData) - 1):
                self.indexDict[currentTableIndex]['indexStart'] = idxStart
                self.indexDict[currentTableIndex]['indexEnd'] = idxEnd
                currentTableIndex += 1

