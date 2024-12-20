import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class Plot1d(tk.Toplevel):
    def __init__(self, root : tk.Tk, name : str, closeAction : callable):
        self.root = root
        tk.Toplevel.__init__(self, self.root)
        self.title(name)
        self.protocol("WM_DELETE_WINDOW", closeAction)

        self.withdraw()

        self.fig = Figure()
        self.ax = self.fig.add_subplot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

    def AlterAxis(self, xRange: list, xTicks: list, yRange: list, yTicks: list, labels: list):
        if "auto" not in xRange:
            if xTicks[0] != "auto":
                xTickMajor = []
                xTickMinor = []
                if xTicks[1] != "auto":
                    currentTick = xTicks[1]
                else:
                    currentTick = xRange[0]
                while currentTick >= xRange[0]:
                    currentTick -= xTicks[0]
                while currentTick <= xRange[1]:
                    xTickMajor.append(currentTick)
                    if xTicks[2] != "auto":
                        for i in range(0, xTicks[2]):
                            xTickMinor.append(currentTick + (xTicks[0] / (xTicks[2] + 1)) * (i + 1))
                    currentTick += xTicks[0]

                self.ax.set_xticks(xTickMajor, minor=False)
                self.ax.set_xticks(xTickMinor, minor=True)
            self.ax.set_xlim(xRange[0], xRange[1])
        else:
            self.ax.autoscale(enable=True, axis="x")

        if "auto" not in yRange:
            if yTicks[0] != "auto":
                yTickMajor = []
                yTickMinor = []
                if yTicks[1] != "auto":
                    currentTick = yTicks[1]
                else:
                    currentTick = yRange[0]
                while currentTick >= yRange[0]:
                    currentTick -= yTicks[0]
                while currentTick <= yRange[1]:
                    yTickMajor.append(currentTick)
                    if yTicks[2] != "auto":
                        for i in range(0, yTicks[2]):
                            yTickMinor.append(currentTick + (yTicks[0] / (yTicks[2] + 1)) * (i + 1))
                    currentTick += yTicks[0]

                self.ax.set_yticks(yTickMajor, minor=False)
                self.ax.set_yticks(yTickMinor, minor=True)
            self.ax.set_ylim(yRange[0], yRange[1])
        else:
            self.ax.autoscale(enable=True, axis="y")

        self.ax.set_xlabel(labels[0])
        self.ax.set_ylabel(labels[1])
        self.ax.set_title(labels[2])
        self.canvas.draw()

    def PlotData(self, dataX, dataY, style="k-", reset=True):
        if reset:
            self.ax.clear()
        self.ax.plot(dataX, dataY, style)
        self.canvas.draw()



