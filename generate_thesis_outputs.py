from thesis import Aggregates, Compliance, InfoGainTable

path = '/Users/Kerz/Documents/projects/SleepSight/ANALYSIS/data/'
plot_path = '/Users/Kerz/Documents/projects/SleepSight/ANALYSIS/plots/'

# Compliance Figure
aggr = Aggregates('.pkl', path, plot_path)
comp = Compliance(aggr)
comp.generateFigure(show=False, save=True)
comp.exportLatexTable(save=True)

# Compliance Information Gain
comp = Compliance(aggr)
comp.normaliseMissingness()
labelsNoMissingness = comp.dfCount.T['No Missingness']
labelsSleep = comp.dfCount.T['sleep']
labelsSymptom = comp.dfCount.T['symptom']
infoTable = aggr.getPariticpantsInfo()
labels = {'Passive data': labelsNoMissingness,
          'Active (Sleep Q.)': labelsSleep,
          'Active (Symptoms Q.)': labelsSymptom}
features = [
            'PANSS.general',
            'PANSS.negative',
            'PANSS.positive',
            'PANSS.total',
            'age',
            'durationIllness',
            'gender',
            'Clozapine',
            'No.of.Drugs'
            ]
igTable = InfoGainTable(infoTable[features], labels)
igTable.run()
igTable.exportLatexTable(aggr.pathPlot, orderedBy='Passive data', save=True)
print(igTable)
