import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import nidaqmx.constants as nc
from vendor import atsapi as ats
import os

from InstrumentControl import PulseParams
import Plot1d

import Plot1d

class GUITextElement(tk.StringVar):
    def __init__(self,
                 root : tk.Tk,
                 master : ttk.Frame,
                 elementType : tuple,
                 name : str,
                 updateCallback : callable,
                 contentType=str):

        self.root = root
        self.wName = name
        tk.StringVar.__init__(self, master)

        if elementType[0] == "Entry":
            self.guiElement = ttk.Entry(master, textvariable=self, name=name)
            self.guiElement.insert(tk.END, elementType[1])
        if elementType[0] == "OptionMenu":
            self.guiElement = ttk.OptionMenu(master, self, elementType[1][elementType[2]], *elementType[1])

        self.contentType = contentType

        self.trace_add("write", self.checkUpdate)

        self.updateCallback = updateCallback

        self.lastValue = self.get()
        self.updateTriggered = False

    def checkUpdate(self, name, index, mode):
        if self.updateTriggered == False:
            self.updateTriggered = True
            self.root.after(500, self.checkLastValue)

    def checkLastValue(self):
        if self.lastValue != self.get():
            self.lastValue = self.get()
            self.root.after(500, self.checkLastValue)
        else:
            self.updateTriggered = False
            self.updateCallback()

    def GridElement(self, row, column, rowspan=1, columnspan=1):
        self.guiElement.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def ReturnValue(self):
        if not self.get():
            if (self.contentType == int):
                return self.contentType(0)
            if (self.contentType == float):
                return self.contentType(0.0)
            if (self.contentType == str):
                return self.contentType("")
        if self.get().lower().replace(" ", "") == "auto":
            return self.get().lower().replace(" ", "")
        else:
            return self.contentType(self.get())

class Plot1dGUI:
    def __init__(self,
                 root : tk.Tk,
                 parentContainer : ttk.Frame,
                 name : str,
                 xPlotOptions : tuple,
                 yPlotOptions : tuple,
                 defaults : dict,
                 data):

        self.root = root
        self.containerFrame = ttk.Frame(parentContainer, name=name.lower().replace(" ","_"))
        self.containerFrame["borderwidth"] = 5
        self.containerFrame["relief"] = "sunken"
        self.plot = Plot1d.Plot1d(root, name, self.toggleShow)

        self.data = data

        self.name = ttk.Label(self.containerFrame, text=name)
        self.binned = False
        if type(xPlotOptions[0]) == list:
            self.xAxis = GUITextElement(self.root, self.containerFrame, ("OptionMenu", xPlotOptions[0], xPlotOptions[1]), "xaxis", self.updateData)
            if xPlotOptions[2] == True:
                self.xAxisBinSize = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["xAxisBin"]), "xaxisbin", self.updateData, contentType=float)
                self.binned = True
            else:
                self.xAxisBinSize = ttk.Label(self.containerFrame, text="N/A")
        elif type(xPlotOptions[0]) == str:
            self.xAxis = ttk.Label(self.containerFrame, text=xPlotOptions[0])
            if xPlotOptions[1] == True:
                self.xAxisBinSize = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["xAxisBin"]), "xaxisbin", self.updateData, contentType=float)
                self.binned = True
            else:
                self.xAxisBinSize = ttk.Label(self.containerFrame, text="N/A")

        if type(yPlotOptions[0]) == list:
            self.yAxis = GUITextElement(self.root, self.containerFrame, ("OptionMenu", yPlotOptions[0], yPlotOptions[1]), "yaxis", self.updateData)
            if yPlotOptions[2] == True:
                self.yAxisBinSize = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["yAxisBin"]), "yaxisbin", self.updateData, contentType=float)
                self.binned = True
            else:
                self.yAxisBinSize = ttk.Label(self.containerFrame, text="N/A")
        elif type(yPlotOptions[0]) == str:
            self.yAxis = ttk.Label(self.containerFrame, text=yPlotOptions[0])
            if yPlotOptions[1] == True:
                self.yAxisBinSize = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["yAxisBin"]), "yaxisbin", self.updateData, contentType=float)
                self.binned = True
            else:
                self.yAxisBinSize = ttk.Label(self.containerFrame, text="N/A")

        self.xAxisLow = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["xAxisLow"]), "xaxislow", self.updatePlot, contentType=float)
        self.yAxisLow = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["yAxisLow"]), "yaxislow", self.updatePlot, contentType=float)

        self.xAxisHigh = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["xAxisHigh"]), "xaxishigh", self.updatePlot, contentType=float)
        self.yAxisHigh = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["yAxisHigh"]), "yaxishigh", self.updatePlot, contentType=float)

        self.xTickSpacing = GUITextElement(self.root, self.containerFrame, ("Entry", "Auto"), "xticks", self.updatePlot, contentType=float)
        self.yTickSpacing = GUITextElement(self.root, self.containerFrame, ("Entry", "Auto"), "yticks", self.updatePlot, contentType=float)

        self.xMinorTicks = GUITextElement(self.root, self.containerFrame, ("Entry", "Auto"), "xminorticks", self.updatePlot, contentType=int)
        self.yMinorTicks = GUITextElement(self.root, self.containerFrame, ("Entry", "Auto"), "yminorticks", self.updatePlot, contentType=int)

        self.xTickCanon = GUITextElement(self.root, self.containerFrame, ("Entry", "Auto"), "xtickcanon", self.updatePlot, contentType=float)
        self.yTickCanon = GUITextElement(self.root, self.containerFrame, ("Entry", "Auto"), "ytickcanon", self.updatePlot, contentType=float)

        self.xAxisLabel = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["xAxisLabel"]), "xaxislabel", self.updatePlot, contentType=str)
        self.yAxisLabel = GUITextElement(self.root, self.containerFrame, ("Entry", defaults["yAxisLabel"]), "yaxislabel", self.updatePlot, contentType=str)

        self.plotLabel = GUITextElement(self.root, self.containerFrame, ("Entry", name), "plottitle", self.updatePlot)

        self.visibility = ttk.Button(self.containerFrame, text="Show", command=self.toggleShow)

    def GridElements(self, row, column, rowspan=1, columnspan=1):
        rowCount = 0

        self.name.grid(row=rowCount, column=0, rowspan=1, columnspan=3, padx=2, pady=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Axis").grid(row=rowCount, column=0)
        ttk.Label(self.containerFrame, text="Horizontal").grid(row=rowCount, column=1)
        ttk.Label(self.containerFrame, text="Vertical").grid(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Variable").grid(row=rowCount, column=0)
        if type(self.xAxis) == GUITextElement:
            self.xAxis.GridElement(row=rowCount, column=1)
        elif type(self.xAxis) == ttk.Label:
            self.xAxis.grid(row=rowCount, column=1)

        if type(self.yAxis) == tk.StringVar:
            self.yAxis.GridElement(row=rowCount, column=2)
        elif type(self.yAxis) == ttk.Label:
            self.yAxis.grid(row=rowCount, column=2)
        rowCount += 1

        if self.binned == True:
            ttk.Label(self.containerFrame, text="Bin size").grid(row=rowCount, column=0)
            if type(self.xAxisBinSize) == GUITextElement:
                self.xAxisBinSize.GridElement(row=rowCount, column=1)
            elif type(self.xAxisBinSize) == ttk.Label:
                self.xAxisBinSize.grid(row=rowCount, column=1)

            if type(self.yAxisBinSize) == GUITextElement:
                self.yAxisBinSize.GridElement(row=rowCount, column=2)
            elif type(self.yAxisBinSize) == ttk.Label:
                self.yAxisBinSize.grid(row=rowCount, column=2)
            rowCount += 1

        ttk.Label(self.containerFrame, text="Axis low-end limit").grid(row=rowCount, column=0)
        self.xAxisLow.GridElement(row=rowCount, column=1)
        self.yAxisLow.GridElement(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Axis high-end limit").grid(row=rowCount, column=0)
        self.xAxisHigh.GridElement(row=rowCount, column=1)
        self.yAxisHigh.GridElement(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Tick spacing").grid(row=rowCount, column=0)
        self.xTickSpacing.GridElement(row=rowCount, column=1)
        self.yTickSpacing.GridElement(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Canonical tick").grid(row=rowCount, column=0)
        self.xTickCanon.GridElement(row=rowCount, column=1)
        self.yTickCanon.GridElement(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Number of minor ticks").grid(row=rowCount, column=0)
        self.xMinorTicks.GridElement(row=rowCount, column=1)
        self.yMinorTicks.GridElement(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Axis label").grid(row=rowCount, column=0)
        self.xAxisLabel.GridElement(row=rowCount, column=1)
        self.yAxisLabel.GridElement(row=rowCount, column=2)
        rowCount += 1

        ttk.Label(self.containerFrame, text="Plot label").grid(row=rowCount, column=0)
        self.plotLabel.GridElement(row=rowCount, column=1)
        rowCount += 1

        self.visibility.grid(row=rowCount, column=2)

        self.containerFrame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def toggleShow(self):
        if self.visibility["text"] == "Show":
            self.plot.deiconify()
            newState = "Hide"

        if self.visibility["text"] == "Hide":
            self.plot.withdraw()
            newState = "Show"

        self.visibility["text"] = newState

    def updatePlot(self):
        xRange = [self.xAxisLow.ReturnValue(), self.xAxisHigh.ReturnValue()]
        xTicks = [self.xTickSpacing.ReturnValue(), self.xTickCanon.ReturnValue(), self.xMinorTicks.ReturnValue()]
        yRange = [self.yAxisLow.ReturnValue(), self.yAxisHigh.ReturnValue()]
        yTicks = [self.yTickSpacing.ReturnValue(), self.yTickCanon.ReturnValue(), self.yMinorTicks.ReturnValue()]
        labels = [self.xAxisLabel.ReturnValue(), self.yAxisLabel.ReturnValue(), self.plotLabel.ReturnValue()]
        self.plot.AlterAxis(xRange, xTicks, yRange, yTicks, labels)

    def updateData(self):
        key = self.xAxis.ReturnValue()
        dataRange = [self.xAxisLow.ReturnValue(), self.xAxisHigh.ReturnValue()]
        binSize = self.xAxisBinSize.ReturnValue()
        histX, counts = self.data.GetData(key, dataRange, binSize)
        self.plot.PlotData(histX, counts)

class TimingParent:
    def __init__(self, root : tk.Toplevel, names : list, clockOptions : list):
        self.container = ttk.Frame(root)
        self.container["borderwidth"] = 5
        self.container["relief"] = "sunken"
        self.timings = []
        for i in range(0, len(names)):
            self.timings.append(TimingParams(names[i], self.container, clockOptions))

    def SetDefaults(self, defaults):
        for i in range(0, len(self.timings)):
            self.timings[i].SetDefaults(defaults[i])

    def GridElements(self, row, column, rowspan=1, columnspan=1):
        ttk.Label(self.container, text="Pulsing Parameters").grid(row=0, column=0, rowspan=1, columnspan=7, padx=2, pady=2)

        ttk.Label(self.container, text="Pulse delay (s)").grid(row=1, column=1)
        ttk.Label(self.container, text="Low time (s)").grid(row=1, column=2)
        ttk.Label(self.container, text="High time (s)").grid(row=1, column=3)
        ttk.Label(self.container, text="Idle state").grid(row=1, column=4)
        ttk.Label(self.container, text="Clock").grid(row=1, column=5)
        ttk.Label(self.container, text="Active?").grid(row=1, column=6)

        for i in range(0, len(self.timings)):
            self.timings[i].GridElements(i+2, 0)

        self.container.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def GetTimings(self):
        activeTimings = []
        for i in range(0, len(self.timings)):
            if self.timings[i].GetState():
                activeTimings.append(self.timings[i].ReturnPulseParams())
        return activeTimings

class TimingParams:
    def __init__(self, name : str, root : tk.Toplevel, clockOptions : list):
        self.name = ttk.Label(root, text=name)
        self.delay = ttk.Entry(root)
        self.lowTime = ttk.Entry(root)
        self.highTime = ttk.Entry(root)
        idleStateOptions = ["Low", "High"]
        self.idleState = tk.StringVar(root)
        self.idleStateOptionMenu = ttk.OptionMenu(root, self.idleState, idleStateOptions[0], idleStateOptions)
        self.clock = tk.StringVar(root)
        self.clockOptionMenu = ttk.OptionMenu(root, self.clock, clockOptions[0], *clockOptions)
        self.isActive = tk.IntVar(root)
        self.isActiveButton = ttk.Checkbutton(root, variable=self.isActive, onvalue=1, offvalue=0)

    def SetDefaults(self, defaults : dict):
        self.delay.insert(tk.END, defaults["delay"])
        self.lowTime.insert(tk.END, defaults["low time"])
        self.highTime.insert(tk.END, defaults["high time"])
        self.idleState.set(defaults["idle"])
        self.clock.set(defaults["clock"])
        self.isActive.set(defaults["is active"])

    def GridElements(self, row, column):
        self.name.grid(row=row, column=column)
        self.delay.grid(row=row, column=column+1)
        self.lowTime.grid(row=row, column=column+2)
        self.highTime.grid(row=row, column=column+3)
        self.idleStateOptionMenu.grid(row=row, column=column+4)
        self.clockOptionMenu.grid(row=row, column=column+5)
        self.isActiveButton.grid(row=row, column=column+6)

    def ReturnPulseParams(self):
        clock = self.clock.get()
        if self.idleState.get() == "Low":
            idle = nc.Level.LOW
        elif self.idleState.get() == "High":
            idle = nc.Level.HIGH
        delay = round(float(self.delay.get()), 7)
        low = round(float(self.lowTime.get()), 7)
        high = round(float(self.highTime.get()), 7)

        p = PulseParams(clock, idleState=idle, delay=delay, lowTime=low, highTime=high)

        return p

    def GetState(self):
        if self.isActive.get() == 1:
            return True
        if self.isActive.get() == 0:
            return False

class DigitizerParams:
    def __init__(self, root : tk.Toplevel, freqOptions : list, inputRangeOptions : list, inputImpedanceOptions : list):
        frameWidth = 200

        self.acqFrame = ttk.Frame(root)
        self.acqFrame.configure(width=frameWidth)
        self.acqFrame["borderwidth"] = 5
        self.acqFrame["relief"] = "sunken"

        self.sampFreq = tk.StringVar(self.acqFrame)
        self.sampFreqOptionMenu = ttk.OptionMenu(self.acqFrame, self.sampFreq, freqOptions[0], *freqOptions)
        self.preTrigSamps = ttk.Entry(self.acqFrame)
        self.postTrigSamps = ttk.Entry(self.acqFrame)
        self.nDMABuffers = ttk.Entry(self.acqFrame)
        self.acqTimeout = ttk.Entry(self.acqFrame)

        self.channelFrame = ttk.Frame(root)
        self.channelFrame.configure(width=frameWidth)
        self.channelFrame["borderwidth"] = 5
        self.channelFrame["relief"] = "sunken"

        couplingOptions = ["AC coupled", "DC coupled"]
        self.chanACoupling = tk.StringVar(self.channelFrame)
        self.chanACouplingOptionMenu = ttk.OptionMenu(self.channelFrame, self.chanACoupling, couplingOptions[1], *couplingOptions)
        self.chanBCoupling = tk.StringVar(self.channelFrame)
        self.chanBCouplingOptionMenu = ttk.OptionMenu(self.channelFrame, self.chanBCoupling, couplingOptions[1], *couplingOptions)

        self.chanARange = tk.StringVar(self.channelFrame)
        self.chanARangeOptionMenu = ttk.OptionMenu(self.channelFrame, self.chanARange, inputRangeOptions[0], *inputRangeOptions)
        self.chanBRange = tk.StringVar(self.channelFrame)
        self.chanBRangeOptionMenu = ttk.OptionMenu(self.channelFrame, self.chanBRange, inputRangeOptions[0], *inputRangeOptions)

        self.chanAImpedance = tk.StringVar(self.channelFrame)
        self.chanAImpedanceOptionMenu = ttk.OptionMenu(self.channelFrame, self.chanAImpedance, inputImpedanceOptions[0], *inputImpedanceOptions)
        self.chanBImpedance = tk.StringVar(self.channelFrame)
        self.chanBImpedanceOptionMenu = ttk.OptionMenu(self.channelFrame, self.chanBImpedance, inputImpedanceOptions[0], *inputImpedanceOptions)

        self.chanABandwidth = ttk.Entry(self.channelFrame)
        self.chanBBandwidth = ttk.Entry(self.channelFrame)

        self.chanAisActive = tk.IntVar(self.channelFrame)
        self.chanAisActiveButton = ttk.Checkbutton(self.channelFrame, variable=self.chanAisActive, onvalue=1, offvalue=0)
        self.chanBisActive = tk.IntVar(self.channelFrame)
        self.chanBisActiveButton = ttk.Checkbutton(self.channelFrame, variable=self.chanBisActive, onvalue=1, offvalue=0)

        self.trigFrame = ttk.Frame(root)
        self.trigFrame.configure(width=frameWidth)
        self.trigFrame["borderwidth"] = 5
        self.trigFrame["relief"] = "sunken"

        trigActionOptions = ["Trigger on J", "Trigger on K", "Trigger on J or K"]
        self.trigAction = tk.StringVar(self.trigFrame)
        self.trigActionOptionMenu = ttk.OptionMenu(self.trigFrame, self.trigAction, trigActionOptions[0], *trigActionOptions)

        self.trigJisActive = tk.IntVar(self.trigFrame)
        self.trigJisActiveButton = ttk.Checkbutton(self.trigFrame, variable=self.trigJisActive, onvalue=1, offvalue=0)
        self.trigKisActive = tk.IntVar(self.trigFrame)
        self.trigKisActiveButton = ttk.Checkbutton(self.trigFrame, variable=self.trigKisActive, onvalue=1, offvalue=0)

        trigSources = ["Channel A", "Channel B", "External Trig in"]
        self.trigJSource = tk.StringVar(self.trigFrame)
        self.trigJSourceOptionMenu = ttk.OptionMenu(self.trigFrame, self.trigJSource, trigSources[0], *trigSources)
        self.trigKSource = tk.StringVar(self.trigFrame)
        self.trigKSourceOptionMenu = ttk.OptionMenu(self.trigFrame, self.trigJSource, trigSources[0], *trigSources)

        slopeOptions = ["Negative", "Positive"]
        self.trigJSlope = tk.StringVar(self.trigFrame)
        self.trigJSlopeOptionMenu = ttk.OptionMenu(self.trigFrame, self.trigJSlope, slopeOptions[1], *slopeOptions)
        self.trigKSlope = tk.StringVar(self.trigFrame)
        self.trigKSlopeOptionMenu = ttk.OptionMenu(self.trigFrame, self.trigKSlope, slopeOptions[1], *slopeOptions)

        self.trigJLevel = ttk.Entry(self.trigFrame, width=10)
        self.trigKLevel = ttk.Entry(self.trigFrame, width=10)

        extTrigOptions = ["+/- 5V, 50 Ohm"]
        self.extTrigRange = tk.StringVar(self.trigFrame)
        self.extTrigRangeOptionMenu = ttk.OptionMenu(self.trigFrame, self.extTrigRange, extTrigOptions[0], *extTrigOptions)

    def GridAcqElements(self, row, column, rowspan=1, columnspan=1):
        ttk.Label(self.acqFrame, text="Acquistion Parameters").grid(row=0, column=0, rowspan=1, columnspan=2, padx=2, pady=2)

        ttk.Label(self.acqFrame, text="Sampling frequency").grid(row=1, column=0)
        self.sampFreqOptionMenu.grid(row=1, column=1)

        ttk.Label(self.acqFrame, text="Pre trigger samples").grid(row=2, column=0)
        self.preTrigSamps.grid(row=2, column=1)

        ttk.Label(self.acqFrame, text="Post trigger samples").grid(row=3, column=0)
        self.postTrigSamps.grid(row=3, column=1)

        ttk.Label(self.acqFrame, text="Number of DMA buffers").grid(row=4, column=0)
        self.nDMABuffers.grid(row=4, column=1)

        ttk.Label(self.acqFrame, text="Buffer fill timeout (ms)").grid(row=5, column=0)
        self.acqTimeout.grid(row=5, column=1)

        self.acqFrame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def GridChannelElements(self, row, column, rowspan=1, columnspan=1):
        ttk.Label(self.channelFrame, text="Channel Parameters").grid(row=0, column=0, rowspan=1, columnspan=3, padx=2, pady=2)

        ttk.Label(self.channelFrame, text="Channel").grid(row=1, column=0)
        ttk.Label(self.channelFrame, text="A").grid(row=1, column=1)
        ttk.Label(self.channelFrame, text="B").grid(row=1, column=2)

        ttk.Label(self.channelFrame, text="Coupling").grid(row=2, column=0)
        self.chanACouplingOptionMenu.grid(row=2, column=1)
        self.chanBCouplingOptionMenu.grid(row=2, column=2)

        ttk.Label(self.channelFrame, text="Input range").grid(row=3, column=0)
        self.chanARangeOptionMenu.grid(row=3, column=1)
        self.chanBRangeOptionMenu.grid(row=3, column=2)

        ttk.Label(self.channelFrame, text="Input impedance").grid(row=4, column=0)
        self.chanAImpedanceOptionMenu.grid(row=4, column=1)
        self.chanBImpedanceOptionMenu.grid(row=4, column=2)

        ttk.Label(self.channelFrame, text="Bandwidth limit").grid(row=5, column=0)
        self.chanABandwidth.grid(row=5, column=1)
        self.chanBBandwidth.grid(row=5, column=2)

        ttk.Label(self.channelFrame, text="Active?").grid(row=6, column=0)
        self.chanAisActiveButton.grid(row=6, column=1)
        self.chanBisActiveButton.grid(row=6, column=2)

        self.channelFrame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def GridTriggerElements(self, row, column, rowspan=1, columnspan=1):
        ttk.Label(self.trigFrame, text="Trigger Parameters").grid(row=0, column=0, rowspan=1, columnspan=3, padx=2, pady=2)

        ttk.Label(self.trigFrame, text="Trigger action:").grid(row=1, column=0)
        self.trigActionOptionMenu.grid(row=1, column=1, columnspan=2)

        ttk.Label(self.trigFrame, text="Engine").grid(row=2, column=0)
        ttk.Label(self.trigFrame, text="J").grid(row=2, column=1)
        ttk.Label(self.trigFrame, text="K").grid(row=2, column=2)

        ttk.Label(self.trigFrame, text="Active?").grid(row=3, column=0)
        self.trigJisActiveButton.grid(row=3, column=1)
        self.trigKisActiveButton.grid(row=3, column=2)

        ttk.Label(self.trigFrame, text="Source").grid(row=4, column=0)
        self.trigJSourceOptionMenu.grid(row=4, column=1)
        self.trigKSourceOptionMenu.grid(row=4, column=2)

        ttk.Label(self.trigFrame, text="Slope").grid(row=5, column=0)
        self.trigJSlopeOptionMenu.grid(row=5, column=1)
        self.trigKSlopeOptionMenu.grid(row=5, column=2)

        ttk.Label(self.trigFrame, text="Level (V)").grid(row=6, column=0)
        self.trigJLevel.grid(row=6, column=1)
        self.trigKLevel.grid(row=6, column=2)

        ttk.Label(self.trigFrame, text="Ext. trigger settings").grid(row=7, column=0)
        self.extTrigRangeOptionMenu.grid(row=7, column=1, columnspan=2)

        self.trigFrame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def BuildParamObjects(self):
        pass

class DigitizierChannel:
    def __init__(self, name, coupling, inRange, impedance, bandwidth, isActive):
        self.name = name
        self.coupling = coupling
        self.inRange = inRange
        self.impedance = impedance
        self.bandwidth = bandwidth
        self.isActive = isActive

    def ReturnParams(self):
        pass

class MainControlGUI:
    def __init__(self, root : tk.Tk, runFunc : callable, newDirFunc : callable, pulsingChild : tk.Toplevel, digitizerChild : tk.Toplevel, plottingChild : tk.Toplevel):
        self.experimentSetupFrame = ttk.Frame(root)
        self.experimentSetupFrame["borderwidth"] = 5
        self.experimentSetupFrame["relief"] = "sunken"

        self.saveDirectory = ttk.Entry(self.experimentSetupFrame, width=50)
        self.date = ttk.Entry(self.experimentSetupFrame)
        self.experimentTitle = ttk.Entry(self.experimentSetupFrame, width=50)
        self.timeout = ttk.Entry(self.experimentSetupFrame)
        self.runState = ttk.Button(self.experimentSetupFrame, text="Run", command=runFunc)
        self.newDir = ttk.Button(self.experimentSetupFrame, text="New scan", command=newDirFunc)

        self.expInitialized = False
        self.scanCounter = 0

        self.childVisibilityFrame = ttk.Frame(root)
        self.childVisibilityFrame["borderwidth"] = 5
        self.childVisibilityFrame["relief"] = "sunken"

        self.pulsingChild = pulsingChild
        self.digitizerChild = digitizerChild
        self.plottingChild = plottingChild
        self.pulsingVisibility = ttk.Button(self.childVisibilityFrame, text="Show pulsing controls", command=self.togglePulsingVisibility)
        self.digitizerVisibility = ttk.Button(self.childVisibilityFrame, text="Show digitizer controls", command=self.toggleDigitizerVisibility)
        self.plottingVisibility = ttk.Button(self.childVisibilityFrame, text="Show plotting controls", command=self.togglePlottingVisibility)

        self.analysisControlsFrame = ttk.Frame(root)
        self.analysisControlsFrame["borderwidth"] = 5
        self.analysisControlsFrame["relief"] = "sunken"

    def GetButtonRefs(self):
        return [self.pulsingVisibility, self.digitizerVisibility, self.plottingVisibility]

    def SetDefaults(self, defaults : dict):
        self.saveDirectory.insert(tk.END, defaults["Save Dir"])
        self.date.insert(tk.END, defaults["Date"])
        self.timeout.insert(tk.END, defaults["Timeout"])

    def togglePulsingVisibility(self):
        if self.pulsingVisibility["text"] == "Show pulsing controls":
            self.pulsingChild.Show()
            newState = "Hide pulsing controls"

        if self.pulsingVisibility["text"] == "Hide pulsing controls":
            self.pulsingChild.withdraw()
            newState = "Show pulsing controls"

        self.pulsingVisibility["text"] = newState

    def toggleDigitizerVisibility(self):
        if self.digitizerVisibility["text"] == "Show digitizer controls":
            self.digitizerChild.Show()
            newState = "Hide digitizer controls"

        if self.digitizerVisibility["text"] == "Hide digitizer controls":
            self.digitizerChild.withdraw()
            newState = "Show digitizer controls"

        self.digitizerVisibility["text"] = newState

    def togglePlottingVisibility(self):
        if self.plottingVisibility["text"] == "Show plotting controls":
            self.plottingChild.Show()
            newState = "Hide plotting controls"

        if self.plottingVisibility["text"] == "Hide plotting controls":
            self.plottingChild.withdraw()
            newState = "Show plotting controls"

        self.plottingVisibility["text"] = newState

    def GridExpSetup(self, row, column, rowspan=1, columnspan=1):
        ttk.Label(self.experimentSetupFrame, text="Experiment setup").grid(row=0, column=0, rowspan=1, columnspan=5, padx=2, pady=2)
        ttk.Label(self.experimentSetupFrame, text="Save directory").grid(row=1, column=0)
        self.saveDirectory.grid(row=1, column=1, rowspan=1, columnspan=3)
        ttk.Button(self.experimentSetupFrame, text="Browse", command=self.browseDataFilePath).grid(row=1, column=4)

        ttk.Label(self.experimentSetupFrame, text="Date").grid(row=2, column=0)
        self.date.grid(row=2, column=1, sticky="W")

        ttk.Label(self.experimentSetupFrame, text="Title").grid(row=3, column=0)
        self.experimentTitle.grid(row=3, column=1, rowspan=1, columnspan=3)

        ttk.Label(self.experimentSetupFrame, text="Timeout (m)").grid(row=4, column=0)
        self.timeout.grid(row=4, column=1, sticky="W")

        self.newDir.grid(row=5, column=3, sticky="E")
        self.runState.grid(row=5, column=4)

        self.experimentSetupFrame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def GridVisibility(self, row, column, rowspan=1, columnspan=1):
        ttk.Label(self.childVisibilityFrame, text="Control panels").grid(row=0, column=0, rowspan=1, columnspan=5, padx=2, pady=2)
        self.pulsingVisibility.grid(row=1, column=0)
        self.digitizerVisibility.grid(row=2, column=0)
        self.plottingVisibility.grid(row=3, column=0)

        self.childVisibilityFrame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)

    def browseDataFilePath(self):
        folder = filedialog.askdirectory()
        if folder != "":
            self.saveDirectory.delete(0, tk.END)
            self.saveDirectory.insert(tk.END, folder)

    def GetRunState(self):
        return self.runState["text"]

    def UpdateRunState(self, newState : str):
        self.runState["text"] = newState

    def GetPaths(self):
        top = self.saveDirectory.get() + "/" + self.date.get()
        experiment = top + "/" + self.experimentTitle.get()
        return [top, experiment]

    def run(self):
        if self.runState["text"] == "Run":
            self.experimentPath = self.saveDirectory.get() + "/" + self.date.get()
            if not os.path.isdir(self.experimentPath):
                os.mkdir(self.experimentPath)

            while os.path.isdir(self.experimentPath + "/scan-" + str(self.scanCounter)):
                self.scanCounter += 1
            os.mkdir(self.experimentPath + "/scan-" + str(self.scanCounter))
            self.currentDataDir = self.experimentPath + "/scan-" + str(self.scanCounter)
            self.expInitialized = True
            print(self.currentDataDir)

            newState = "Stop"
        if self.runState["text"] == "Stop":
            newState = "Run"

        self.runState["text"] = newState



class ControlWindowManager:
    def __init__(self,
                 pulsingChild : tk.Toplevel,
                 pulsingVisibility : ttk.Button,
                 digitizerChild : tk.Toplevel,
                 digitizerVisibility : ttk.Button,
                 plottingChild : tk.Toplevel,
                 plottingVisibilty : ttk.Button):

        self.pulsingChild = pulsingChild
        self.pulsingVisibility = pulsingVisibility
        self.digitizerChild = digitizerChild
        self.digitizerVisibility = digitizerVisibility
        self.plottingChild = plottingChild
        self.plottingVisibility = plottingVisibilty

    def CheckPulsingVisibility(self):
        update = False
        if self.pulsingChild.winfo_viewable() and ("Show" in self.pulsingVisibility["text"]):
            update = True
            oldState = "Show"
            newState = "Hide"

        if not self.pulsingChild.winfo_viewable() and ("Hide" in self.pulsingVisibility["text"]):
            update = True
            oldState = "Hide"
            newState = "Show"

        if update:
            self.pulsingVisibility["text"] = self.pulsingVisibility["text"].replace(oldState, newState)

    def CheckDigitizerVisibility(self):
        update = False
        if self.digitizerChild.winfo_viewable() and ("Show" in self.digitizerVisibility["text"]):
            update = True
            oldState = "Show"
            newState = "Hide"

        if not self.digitizerChild.winfo_viewable() and ("Hide" in self.digitizerVisibility["text"]):
            update = True
            oldState = "Hide"
            newState = "Show"

        if update:
            self.digitizerVisibility["text"] = self.digitizerVisibility["text"].replace(oldState, newState)

    def CheckPlottingVisibility(self):
        update = False
        if self.plottingChild.winfo_viewable() and ("Show" in self.plottingVisibility["text"]):
            update = True
            oldState = "Show"
            newState = "Hide"

        if not self.plottingChild.winfo_viewable() and ("Hide" in self.plottingVisibility["text"]):
            update = True
            oldState = "Hide"
            newState = "Show"

        if update:
            self.plottingVisibility["text"] = self.plottingVisibility["text"].replace(oldState, newState)


