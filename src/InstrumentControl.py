import nidaqmx.task as nt
import nidaqmx.constants as nc

class PulseParams():
    def __init__(self, clockID, units=nc.TimeUnits.SECONDS, idleState=nc.Level.LOW, delay=0.0, lowTime=1, highTime=1, nSamples=1):
        if type(clockID) == list:
            self.clockID = clockID

            if type(units) == list:
                self.units = units
            else:
                self.units = []
                for i in range(0, len(clockID)):
                    self.units.append(units)

            if type(idleState) == list:
                self.idleState = idleState
            else:
                self.idleState = []
                for i in range(0, len(clockID)):
                    self.idleState.append(idleState)

            if type(delay) == list:
                self.delay = delay
            else:
                self.delay = []
                for i in range(0, len(clockID)):
                    self.delay.append(delay)

            if type(lowTime) == list:
                self.lowTime = lowTime
            else:
                self.lowTime = []
                for i in range(0, len(clockID)):
                    self.lowTime.append(lowTime)

            if type(highTime) == list:
                self.highTime = highTime
            else:
                self.highTime = []
                for i in range(0, len(clockID)):
                    self.highTime.append(highTime)

            if type(nSamples) == list:
                self.nSamples = nSamples
            else:
                self.nSamples = []
                for i in range(0, len(clockID)):
                    self.nSamples.append(nSamples)

        else:
            self.clockID = clockID
            self.units = units
            self.idleState = idleState
            self.delay = delay
            self.lowTime = lowTime
            self.highTime = highTime
            self.nSamples = nSamples

class PulseTask(nt.Task):
    def __init__(self, p : PulseParams):
        nt.Task.__init__(self)
        if type(p) == list:
            for i in range(0, len(p)):
                self.co_channels.add_co_pulse_chan_time(p[i].clockID,
                                                        units=p[i].units,
                                                        idle_state=p[i].idleState,
                                                        initial_delay=p[i].delay,
                                                        low_time=p[i].lowTime,
                                                        high_time=p[i].highTime)
                self.timing.cfg_implicit_timing(samps_per_chan=p[i].nSamples)

        else:
            self.co_channels.add_co_pulse_chan_time(p.clockID,
                                                    units=p.units,
                                                    idle_state=p.idleState,
                                                    initial_delay=p.delay,
                                                    low_time=p.lowTime,
                                                    high_time=p.highTime)
            self.timing.cfg_implicit_timing(samps_per_chan=p.nSamples)





