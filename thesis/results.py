import numpy as np
import pandas as pd
from analysis import InfoGain
import matplotlib.pyplot as plt


class Compliance:
    def __init__(self, aggregates):
        self.aggr = aggregates
        self.dfCount, self.dfDaily = self.aggr.getMissingness()
        self.passiveIdxNames = ['No Missingness', 'Not Charged', 'Not Worn', 'Transmission Failure']
        self.passiveDenominator = 60 * 24 * 56
        self.passiveDenominatorDaily = 60 * 24
        self.activeIdxNames = ['symptom', 'sleep']
        self.activeDenominator = 56
        self.activeDenominatorDaily = 1

    def normaliseMissingness(self):
        self.dfCount.loc[self.passiveIdxNames] = round(self.dfCount.loc[self.passiveIdxNames] / self.passiveDenominator * 100)
        self.dfCount.loc[self.activeIdxNames] = round(self.dfCount.loc[self.activeIdxNames] / self.activeDenominator * 100)
        for key in self.dfDaily.keys():
            self.dfDaily[key][self.passiveIdxNames] = round(
                self.dfDaily[key][self.passiveIdxNames] / self.passiveDenominatorDaily * 100)
            self.dfDaily[key][self.activeIdxNames] = self.dfDaily[key][self.activeIdxNames] / self.activeDenominatorDaily * 100

    def formatComplianceOverTime(self):
        dfCountGroup = self.dfCount.T
        self.dfCountMean = dfCountGroup.mean()
        self.dfCountSEM = dfCountGroup.sem()

        dailyList = [self.dfDaily[key] for key in self.dfDaily.keys()]
        dfConcat = pd.concat((dailyList))
        dfConcatRow = dfConcat.groupby(dfConcat.index)
        self.dfDailyMean = dfConcatRow.mean()
        self.dfDailySEM = dfConcatRow.sem()

    def plot(self, show=False):
        plt.close('all')
        plt.figure(figsize=(9, 9))

        plt.subplot(2, 5, (1, 5))
        self.dfCount.T.plot(kind='bar', ax=plt.gca())
        plt.axhline(y=70, color='black', linewidth=0.7)
        plt.title('A', loc='left', size='16')
        plt.xlabel('Participant')
        plt.ylabel('Data completeness (%)')
        plt.legend([])

        print(self.dfDailyMean)
        plt.subplot(2, 5, (6,8))
        self.dfDailyMean.plot(yerr=self.dfDailySEM ,ax=plt.gca(), elinewidth=0.6)
        plt.axhline(y=70, color='black', linewidth=0.7)
        plt.title('B', loc='left', size='16')
        plt.xlabel('Study period (in days)')
        plt.ylabel('Data completeness (%)')
        plt.legend(bbox_to_anchor=(0, -0.5, 1., .102), loc=8,
                   ncol=3, mode="expand", borderpad=0.6, frameon=True)

        plt.subplot(2, 5, (9,10))
        self.dfCountMean.plot(kind='bar',yerr=self.dfCountSEM)
        plt.axhline(y=70, color='black', linewidth=0.7)
        plt.xticks(fontsize='9', rotation=90)
        plt.title('C', loc='left', size='16')
        plt.xlabel('Missingness categories')
        plt.ylabel('Data completeness (%)')
        plt.tight_layout()

        if show:
            plt.show()
        return plt

    def generateFigure(self, show=False, save=True):
        self.normaliseMissingness()
        self.formatComplianceOverTime()
        plt = self.plot()
        if save:
            path = self.aggr.pathPlot + 'Compliance.png'
            plt.savefig(path, dpi=600)
        if show:
            plt.show()

    def exportLatexTable(self, save=True):
        tmpTable = pd.concat((self.dfCountMean, self.dfCountSEM), axis=1)
        tmpTable.columns = ['Mean (%)', 'SD (%)']
        tmpTable.index = [str.capitalize(idx) for idx in tmpTable.index]
        tmpTable['Mean (%)'] = tmpTable['Mean (%)'].astype(int)
        tmpTable['SD (%)'] = tmpTable['SD (%)'].round(1)
        latextTable = tmpTable.to_latex()
        if save:
            path = self.aggr.pathPlot + 'ComplianceTable.tex'
            f = open(path, 'w')
            f.write(latextTable)
            f.close()


class InfoGainTable:

    def __init__(self, infoTable, labels):
        self.labelsOfLabels = labels.keys()
        self.labels = labels
        self.info = infoTable
        self.features = self.info.columns
        self.results = pd.DataFrame(data=np.zeros((len(self.features), len(self.labelsOfLabels))),
                                    columns=self.labelsOfLabels)
        self.results.index = self.features
        self.entropy = pd.DataFrame(data=np.zeros((1, len(self.labelsOfLabels))),
                                    columns=self.labelsOfLabels)
        self.entropy.index = ['Entropy']

    def run(self):
        for labelOfLabels in self.labelsOfLabels:
            labels = self.labels[labelOfLabels]
            ig = InfoGain(self.info, labels)
            ig.calcInfoGain()
            self.results[labelOfLabels] = ig.infoGainTable['Information Gain']
            self.entropy[labelOfLabels] = ig.entropy

    def __str__(self):
        rendered = 'Information Gain for {}\n\n'.format(self.labelsOfLabels)
        rendered += '{}\n\n'.format(self.entropy)
        rendered += 'Compliance Info Gain\n{}\n\n'.format(self.results)
        return rendered