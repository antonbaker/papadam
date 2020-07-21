"""
Created on 04.12.2019
@author: Timur Goenuel
Version: 0.1
Script for reading the Measurement-Data and adjust if needed

Functions:
    readDataZwick   :   
    readDataInfrared:
    readDataUSB     :

important:
    
"""
import pandas as pd 
from time import process_time 
from datetime import date



##########################################################################################################################################################
# import Zwick-Data
##########################################################################################################################################################
def readDataZwick(FilePath, sensorAdjustFactor, translations):
    data_zwick = pd.read_csv(FilePath, sep = ';', encoding = "ISO-8859-1")
    
    for i in range(0,len(data_zwick.columns)):
        data_zwick[data_zwick.columns[i]] = data_zwick[data_zwick.columns[i]].replace(',','.',regex=True)
        
    """Remove unity"""
    data_zwick = data_zwick.drop(data_zwick.index[0])
    
    """STR to FLOAT"""
    data_zwick = data_zwick.astype(float)
    
    data_zwick = data_zwick.reset_index(drop=True)

    """Rename the Columns"""
    data_zwick.rename(columns=translations, inplace=True)
    
    # Unit conversion Zwick data [kN], required Data [N]
    #kN to N
    data_zwick["Force [N]"] = data_zwick["Force [N]"] * 1000
    data_zwick["Absolute_Force [N]"] = data_zwick["Absolute_Force [N]"] * 1000

    #adjust sensor sensitivity because used sensor uses plug of other sensor
    data_zwick['Absolute Clip-On Displacement [mm]'] = data_zwick['Absolute Clip-On Displacement [mm]'] * sensorAdjustFactor

    return data_zwick



##########################################################################################################################################################
# import Infrared-Data
##########################################################################################################################################################
def readDataInfrared(FilePath, originalName):
    data_infrared = pd.read_csv(FilePath, sep='\t', usecols = ['Time','TProc','TInt'], encoding = "ISO-8859-1", skiprows=8)
    
    for i in range(0,len(data_infrared.columns)):
        data_infrared[data_infrared.columns[i]] = data_infrared[data_infrared.columns[i]].replace(',','.',regex=True)
        

    """Remove unity"""
    #Delete the last two rows
    data_infrared = data_infrared.drop(data_infrared.index[-2])
    data_infrared = data_infrared.drop(data_infrared.index[-1])
    
    """STR to FLOAT"""
    #Convert time format to seconds
    data_infrared['Time']   = pd.to_timedelta(data_infrared['Time']).astype('timedelta64[s]').astype(float)
    data_infrared           = data_infrared.astype(float)

    """Rename the Columns"""
    data_infrared.rename(columns=originalName, inplace=True)
    
    return data_infrared


##########################################################################################################################################################
# import USB-Data
##########################################################################################################################################################
def readDataUSB(FilePath, originalName):
    data_USB = pd.read_csv(FilePath, sep=',', usecols = ['Time','Celsius(°C)','Humidity(%rh)'], encoding = "ISO-8859-1")

    #Convert time format to seconds
    def time_to_seconds(time_string):
        return int(time_string[0]) * 3600 + int(time_string[1]) *60 + int(time_string[2]) 
    
    def return_date(time_string):
        return date(int(time_string[0]),int(time_string[1]),int(time_string[2]))
        
    starttime = time_to_seconds(data_USB["Time"][1].split(" ")[1].split(":"))
    startday  = return_date(data_USB["Time"][1].split(" ")[0].split("-"))
    
    timeUSB = data_USB["Time"].iloc[0]
    
    data_USB["Time"] = data_USB["Time"].apply(lambda x: (time_to_seconds(x.split(" ")[1].split(":")) - starttime) + (return_date(x.split(" ")[0].split("-")) - startday).days * 86400 + 60)
    
    data_USB = data_USB.astype(float)
    
    data_USB.rename(columns=originalName, inplace=True)
    
    return data_USB, timeUSB