import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import date
from datetime import datetime
import os

import nidaqmx.system as ns
import nidaqmx.task as nt
import nidaqmx.constants as nc
import nidaqmx as ni
from vendor import atsapi as ats

import numpy as np
from scipy.fft import fft

import GUIDataStructs as gds
import InstrumentControl as ic
import DigitizerBoard as db
import Data as da
import Plot1d as p1d
import ChildWindow as cw

class RootWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.onClose)

        self.title("SPAMM 2.0 Acquisition")

        self.activeTasks = []

        self.buffer = da.DataBuffer()
        self.updateCounter = 0
        self.after(1, self.checkBufferStatus)

        self.topDir = ""
        self.expDir = ""
        self.scanDir = ""
        self.scanCounter = 1


    def onClose(self):
        if len(self.activeTasks) > 0:
            for i in range(0, len(self.activeTasks)):
                self.activeTasks[i].close()
            self.activeTasks = []

        self.quit()
        self.destroy()

    def checkBufferStatus(self):
        if self.buffer.BufferUpdated() == True:
            self.updatePlots()
            timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
            self.buffer.SaveBuffer(self.scanDir, timestamp + "_" + str(self.updateCounter) + ".B.txt")
            self.buffer.ResetBufferState()
        self.after(1, self.checkBufferStatus)

    def updatePlots(self):
        self.updateCounter += 1
        print("nUpdates: " + str(self.updateCounter))
        if self.transientPlot.plot.winfo_viewable() or self.fDomainPlot.plot.winfo_viewable():
            x, y = self.buffer.GetData("Indices", "Buffer")
            y = (0.2 / 66536) * 2 * y - 0.2
            if self.transientPlot.plot.winfo_viewable():
                print("Updating transient plot")
                self.transientPlot.plot.PlotData(x, y)
                self.transientPlot.updatePlot()
            if self.fDomainPlot.plot.winfo_viewable():
                print("Updating FT plot")
                ft = np.abs(fft(y[5000:105000] - np.mean(y[5000:105000]), norm="forward"))
                ft = ft[0:(int(len(ft)/2))+1] * 682500
                ft_late = np.abs(fft(y[805000:905000] - np.mean(y[805000:905000]), norm="forward"))
                ft_late = ft_late[0:(int(len(ft_late) / 2)) + 1] * 682500
                df = 10
                f = np.arange(0, len(ft)*df, df)
                self.fDomainPlot.plot.PlotData(f, ft)
                self.fDomainPlot.plot.PlotData(f, ft_late, style="r-", reset=False)
                self.fDomainPlot.updatePlot()


    def PulsingChild(self):
        self.pulsingChild = cw.ChildWindow(self, name="")
        clockOptions = ["/Dev1/ctr" + str(x) for x in range(0, 8)]
        pulseNames = ["Exit lens", "Trap", "Digitizier"]
        exitlenseDefaults = {"delay": 0.0000,
                             "low time": 1.0010,
                             "high time": 0.0005,
                             "clock": "/Dev1/ctr0",
                             "idle": "Low",
                             "is active": 1}
        trapDefaults = {"delay": 0.0007,
                        "low time": 1.0005,
                        "high time": 0.0010,
                        "clock": "/Dev1/ctr1",
                        "idle": "Low",
                        "is active": 1}
        digitizerDefaults = {"delay": 0.0005,
                             "low time": 1.0014,
                             "high time": 0.0001,
                             "clock": "/Dev1/ctr2",
                             "idle": "Low",
                             "is active": 1}
        self.timings = gds.TimingParent(self.pulsingChild, pulseNames, clockOptions)
        self.timings.SetDefaults([exitlenseDefaults, trapDefaults, digitizerDefaults])
        self.timings.GridElements(row=0, column=0)

        return self

    def DigitizerChild(self):
        self.digitizerChild = cw.ChildWindow(self, name="")
        sampFreqOptions = ["500 MS/s",
                           "200 MS/s",
                           "100 MS/s",
                           "50 MS/s",
                           "20 MS/s",
                           "10 MS/s",
                           "5 MS/s",
                           "2 MS/s",
                           "1 MS/s",
                           "500 kS/s",
                           "200 kS/s",
                           "100 kS/s"]

        sampFreqAPIOptions = {"500 MS/s" : ats.SAMPLE_RATE_500MSPS,
                              "200 MS/s" : ats.SAMPLE_RATE_200MSPS,
                              "100 MS/s" : ats.SAMPLE_RATE_100MSPS,
                              "50 MS/s" : ats.SAMPLE_RATE_50MSPS,
                              "20 MS/s" : ats.SAMPLE_RATE_20MSPS,
                              "10 MS/s" : ats.SAMPLE_RATE_10MSPS,
                              "5 MS/s" : ats.SAMPLE_RATE_5MSPS,
                              "2 MS/s" : ats.SAMPLE_RATE_2MSPS,
                              "1 MS/s" : ats.SAMPLE_RATE_1MSPS,
                              "500 kS/s" : ats.SAMPLE_RATE_500KSPS,
                              "200 kS/s" : ats.SAMPLE_RATE_200KSPS,
                              "100 kS/s" : ats.SAMPLE_RATE_100KSPS}

        inputRangeOptions = ["+/- 200mV", "+/- 400mV", "+/- 800mV", "+/- 1V", "+/- 2V", "+/- 4V"]
        inputImpedanceOptions = ["50 Ohms"]

        self.DigitizerConfig = gds.DigitizerParams(self.digitizerChild, sampFreqOptions, inputRangeOptions, inputImpedanceOptions)
        self.DigitizerConfig.GridAcqElements(row=0, column=0)
        self.DigitizerConfig.GridChannelElements(row=1, column=0)
        self.DigitizerConfig.GridTriggerElements(row=2, column=0)

        return self

    def PlottingChild(self):
        self.plottingChild = cw.ChildWindow(self, name="")

        transientPlotXOptions = "Points"
        transientPlotYOptions = "Volts"
        transientPlotDefaults = {"xAxis": transientPlotXOptions,
                             "yAxis": transientPlotYOptions,
                             "xAxisLow": 0,
                             "yAxisLow": -0.2,
                             "xAxisHigh": 1000,
                             "yAxisHigh": 0.2,
                             "xAxisLabel": transientPlotXOptions,
                             "yAxisLabel": transientPlotYOptions}

        fDomainPlotXOptions = "Frequency (Hz)"
        fDomainPlotYOptions = "Magnitude"
        fDomainPlotDefaults = {"xAxis": fDomainPlotXOptions,
                               "yAxis": fDomainPlotYOptions,
                               "xAxisLow": 10000,
                               "yAxisLow": 0,
                               "xAxisHigh": 30000,
                               "yAxisHigh": 200,
                               "xAxisLabel": fDomainPlotXOptions,
                               "yAxisLabel": fDomainPlotYOptions}

        self.transientPlot = gds.Plot1dGUI(self, self.plottingChild, "Transient", (transientPlotXOptions, False), (transientPlotYOptions, False), transientPlotDefaults, self.buffer)
        self.fDomainPlot = gds.Plot1dGUI(self, self.plottingChild, "Fourier transform", (fDomainPlotXOptions, False), (fDomainPlotYOptions, False), fDomainPlotDefaults, self.buffer)

        self.transientPlot.GridElements(row=0, column=0, rowspan=1, columnspan=1)
        self.fDomainPlot.GridElements(row=1, column=0, rowspan=1, columnspan=1)

        return self

    def RunFrame(self):
        mainDefaults = {"Save Dir" : "C:/Users/SPAMM 2.0/Documents/Data 2022",
                        "Date" : date.today().strftime("%m-%d"),
                        "Timeout" : 60}

        self.MainControls = gds.MainControlGUI(self,
                                               self.Run,
                                               self.NewScan,
                                               self.pulsingChild,
                                               self.digitizerChild,
                                               self.plottingChild)
        self.MainControls.SetDefaults(mainDefaults)
        visibilityRefs = self.MainControls.GetButtonRefs()
        self.MainControls.GridExpSetup(0, 0)
        self.MainControls.GridVisibility(0, 1)

        self.ChildManager = gds.ControlWindowManager(self.pulsingChild,
                                                     visibilityRefs[0],
                                                     self.digitizerChild,
                                                     visibilityRefs[1],
                                                     self.plottingChild,
                                                     visibilityRefs[2])

        return self

    def NewScan(self):
        if self.scanDir != "":
            self.updateCounter = 0
            self.scanCounter += 1
            self.scanDir = self.expDir + "/scan-" + str(self.scanCounter)
            os.mkdir(self.scanDir)
            print(self.scanDir)

    def Run(self):
        if self.MainControls.GetRunState() == "Run":
            self.topDir, self.expDir = self.MainControls.GetPaths()
            if not os.path.isdir(self.topDir):
                os.mkdir(self.topDir)
            if not os.path.isdir(self.expDir):
                self.updateCounter = 0
                self.scanCounter = 1
                os.mkdir(self.expDir)
            while os.path.isdir(self.expDir + "/scan-" + str(self.scanCounter)):
                self.scanCounter += 1
            self.scanDir = self.expDir + "/scan-" + str(self.scanCounter)
            os.mkdir(self.scanDir)
            activePulses = self.timings.GetTimings()
            totalTimes = []
            for i in range(0, len(activePulses)):
                totalTimes.append(round(activePulses[i].lowTime + activePulses[i].highTime, 7))
            if totalTimes.count(totalTimes[0]) != len(totalTimes):
                print("Pulsing error: Timings are not equal for some or all of elements")
                print("Timings: " + str(totalTimes))
                return
            else:
                nSamples = int(float(int(self.MainControls.timeout.get())*60) / (totalTimes[0]))
            for i in range(0, len(activePulses)):
                activePulses[i].nSamples = nSamples

            task = ic.PulseTask(activePulses)
            self.digitizer = db.Digitizer(self.buffer)
            self.digitizer.Configure(nSamples)
            self.digitizer.AsyncAcquisition()
            time.sleep(1)
            task.start()
            self.activeTasks.append(task)
            newState = "Stop"
            self.internalResetState = self.after(int(float(self.MainControls.timeout.get())*1000*60), self.Run)

        if self.MainControls.GetRunState() == "Stop":
            self.after_cancel(self.internalResetState)
            for i in range(0, len(self.activeTasks)):
                self.activeTasks[i].close()
            self.activeTasks = []
            if self.digitizer.board.busy():
                self.digitizer.forceQuitAcq = True
            newState = "Run"

        self.MainControls.UpdateRunState(newState)


