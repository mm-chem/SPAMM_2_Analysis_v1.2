import numpy as np

import matplotlib.pyplot as plt

class DataBuffer:
    def __init__(self):
        self.data = {"Indices" : np.asarray([]),
                     "Buffer" : np.asarray([])
                     }
        self.bufferUpdated = False

    def PushNewBuffer(self, buffer : np.ndarray, acqForceQuit):
        if not acqForceQuit:
            self.data["Indices"] = np.arange(0, len(buffer), 1, dtype=int)
            self.data["Buffer"] = buffer
            self.bufferUpdated = True

    def SaveBuffer(self, path, name):
        self.data["Buffer"].tofile(path + "/" + name, sep="")

    def BufferUpdated(self):
        return self.bufferUpdated

    def ResetBufferState(self):
        self.bufferUpdated = False

    def GetData(self, xKey, yKey):
        if xKey == "Indices" and yKey == "Buffer":
            return self.data[xKey], self.data[yKey]
        else:
            return np.asarray([]), np.asarray([])

class IonStorage:
    def __init__(self):
        self.data = {"Mass (kDa)" : [],
                     "Mass (MDa)" : [],
                     "Charge" : [],
                     }