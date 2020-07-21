from fatigue_main import main_function
#   mit MainPath geht ihr in den Ordner wo die Messdatei drin ist, die ihr untersuchen wollt. sollte nur eine drin sein  
#   corrected_zwick.csv sind die Messdaten mit angepasster Sensitivät
#   processed_cyclic.csv sind die zyklischen Messdaten mit angepasster Sensitivät mit den Temperaturen, aber nicht wirklich synchron
#   processed_cyclic100.csv sind hysterese daten für jeden zyklus mit angepasster Sensitivät

# Path where the rawdata of the specimen is going to be 
MainPath        = r"C:\Users\Celik\Desktop\Test_Data\2_Hz\PBTGF30_120_0°_2Hz_925N_Valid_3MB"

# Path where all the data is being saved
SavePath = MainPath + r"\Results\\"

#manual time of excel if no Zeit.txt is given
year            = 2020
month           = 2
day             = 20
hour            = 13
minute          = 25
second          = 30
mikrosecond     = 0

#manual offset for IR and USB
offsetIR        = 00
offsetUSB       = 0

# Sensor
#   Sensor Identification number
#   This script has a function to correct all strain data measured with the clip-on extensometer,
#   The plug we use for the VHF7 Testing machine is made for the sensor with the ID: 1369 
#   
#   Important! Just change the usedSensor according the used sensor during the test
#
#   The sensor ID is on each clip-on extensometer 
#   Comment date: 2020-March-26, by Hakan Celik
#
#1369 ist der Plug den wir die ganze Zeit verwenden
#2181 der lange Sensor (für PA?)
#1880 der kurze (für PBT?)
#wenn 2181 auf 18mm gestaucht wurde dann trotzdem 2181 eingeben, das Programm berechnet das automatisch
usedSensorplug  = "1369"
usedSensor      = "1369"

#Cross-section of the specimen
area            = 10            # [mm^2] Cross-section of the specimen. 10 mm^2 = 1BA Specimen according to DIN ISO 527       


#downsampling
cycle_downsampling = 10

#decimal_separator for exported csv's
decimal_separator = "."




main_function(MainPath,SavePath,year,month,day,hour,minute,second,mikrosecond,offsetIR,offsetUSB,usedSensor,usedSensorplug,area,cycle_downsampling,decimal_separator)