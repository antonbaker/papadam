"""
Created on 04.12.2019
@author: Timur Goenuel
Version: 0.1
File to 

Functions:
    getAdjustmentFactor

important:
    
"""
class Sensor:
    def __init__(self, sensornumber, sensitivity, measureRangeMax, measureRangeMin, measureBase):
        self.sensornumber    = sensornumber     
        self.sensitivity     = sensitivity          # mV/V
        self.measureRangeMax = measureRangeMax      # mm
        self.measureRangeMin = measureRangeMin      # mm
        self.measureBase     = measureBase          # mm

    
sensorlist = []
# Sensor(SensorID on the clip-on extensometer [-],    sensor sensitivity[mv/V],positive measuring  displacement [mm], negative measuring  displacement [mm], gauge length L0[mm]
sensorlist.append(Sensor("1369",           1.581, 1.25, -1.25, 19.980))     
sensorlist.append(Sensor("1880",           1.602, 1.25, -1.25, 19.920))
sensorlist.append(Sensor("2181",           1.592, 5.00, -5.00, 19.920))
"""TODO measure base berechen"""
sensorlist.append(Sensor("2181modL0_18mm", 1.592, 5.00, -5.00, 18.000))



def getAdjustmentFactor(usedSensorplugNumber, usedSensorNumber):
    usedSensorplug  = list(filter(lambda sen: sen.sensornumber == usedSensorplugNumber, sensorlist))[0]
    usedSensor      = list(filter(lambda sen: sen.sensornumber == usedSensorNumber, sensorlist))[0]
    return ((usedSensor.measureRangeMax*usedSensorplug.sensitivity)/(usedSensor.sensitivity*usedSensorplug.measureRangeMax))


def getL0(usedSensorNumber):
    usedSensor      = list(filter(lambda sen: sen.sensornumber == usedSensorNumber, sensorlist))[0]
    return usedSensor.measureBase