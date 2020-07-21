import pandas as pd
import numpy 
import os
from datetime import datetime  
from datetime import timedelta
import time
import math

import fatigue_read_data as frd
import sensor


##########################################################################################################################################################
# process raw Data
##########################################################################################################################################################


def processRawData(pathData, originalName, usedSensorplug, usedSensor):
#it may be that used sensor plug does not belong to used sensor, therefor adjustmentfactor is needed to get correct data
# Plug sensitivity and sensor sensitivity can differ
# this function corrects delta_l measured with the SANDNER clip-on extensometer (in zwick called absolute strain wrongly)
    adjustmentFactor = sensor.getAdjustmentFactor(usedSensorplug, usedSensor)
    if(os.path.exists(pathData)):
        return frd.readDataZwick(pathData, adjustmentFactor, originalName), True
    else:
        return " ", False

def processInfraredData(pathData, originalName, time0, offsetIR, totalSecondsMeasuredZwick):
    if(os.path.exists(pathData)):
        dataIR = frd.readDataInfrared(pathData, originalName)
        counter = 0 
        with open(pathData) as f:
            for line in f:
                if counter == 3:
                    break
                elif counter == 2:
                    irTime = line.split("\t")[1].split("\n")[0]
                elif counter == 1:
                    irDate = line.split("\t")[1].split("\n")[0]
                counter += 1

        irTime = irTime.split(":")
        irDate = irDate.split(".")
        timeIR = datetime(int(irDate[2]), int(irDate[1]), int(irDate[0]), int(irTime[0]), int(irTime[1]), int(irTime[2]), 0)
        offset = (time0 - timeIR).total_seconds()
        dataIR["Time"] = dataIR["Time"] + offset - offsetIR
        totalSecondsMeasuredInfrared = dataIR["Time"].iloc[-1]
        upper_limit = totalSecondsMeasuredInfrared - totalSecondsMeasuredZwick
        lower_limit = dataIR["Time"].iloc[0]
        if(lower_limit > 0 and upper_limit > 0):
            #lower_limit breached
            if(upper_limit + lower_limit > 0):
                print("Zero point shifted by " + str(-lower_limit))
                dataIR["Time"] = dataIR["Time"] - lower_limit
            else:
                print("IR data incomplete")
                return " ", False
        elif(lower_limit < 0 and upper_limit < 0):
            #upper_limit breached
            if(upper_limit - lower_limit > 0):
                print("Zero point shifted by " + str(upper_limit))
                dataIR["Time"] = dataIR["Time"] - upper_limit
            else:
                print("IR data incomplete")
                return " ", False
        elif(lower_limit > 0 and upper_limit < 0):
            #lower_limit breached and upper_limit breached
            print("IR data incomplete")
            return " ", False

        return dataIR, True
    else:
        return " ", False


def processUSBData(pathData, originalName, time0, offsetUSB, totalSecondsMeasuredZwick):
    if(os.path.exists(pathData)):
        dataUSB, timeUSB = frd.readDataUSB(pathData, originalName)
        temp = timeUSB.split(" ")
        tUSBdate = temp[0].split("-")
        tUSBtime = temp[1].split(":")
        timeUSB = datetime(int(tUSBdate[0]), int(tUSBdate[1]), int(tUSBdate[2]), int(tUSBtime[0]), int(tUSBtime[1]), int(tUSBtime[2]), 0)
        offset = (time0 - timeUSB).total_seconds()
        dataUSB["Time"] = dataUSB["Time"] + offset - offsetUSB
        return dataUSB, True
    else:
        return " ", False



##########################################################################################################################################################
# process Data to get Cyclic-Data
##########################################################################################################################################################

def processDataCyclic(databaseTables, databaseZwick, databaseInfrared, databaseUSB, area, usedSensorPlug, usedSensor, cycle_downsampling):
    dataZwick    = databaseTables[databaseZwick]["dataframe"]
    dataInfrared = databaseTables[databaseInfrared]["dataframe"]
    dataUSB      = databaseTables[databaseUSB]["dataframe"]
    
    listDataCycles = []; listDataCycles100 = []
    CyclesUntilFailure = dataZwick["Cycle_Number [-]"].max()

    # Since the clip-on extensometer is applied manually, the base distance L0 differs  important for strain calculation=> eps = delta_L/L0 
    # Here is a correction of L0 applied 
    sensorL0            = sensor.getL0(usedSensor)                          # get sensor gauge length L0 according to the sensor specification
    L0 = sensorL0 + dataZwick.iloc[0]["Absolute Clip-On Displacement [mm]"]                    # calculate gauge length for the applied 
    dataZwick['Specimen_strain'] = (dataZwick['Absolute Clip-On Displacement [mm]'] - dataZwick.iloc[0]['Absolute Clip-On Displacement [mm]']) / L0 # Specimen strain is calculated [-]
    

    #print(CyclesUntilFailure/cycle_downsampling)


##########################################################################################################################################################
# interpolating USB data
##########################################################################################################################################################

    print("Interpolating USB")
    
    if(databaseTables[databaseUSB]["localDataExists"]):
        usbTemps     = []
        usbHumiditys = []

        freqUSB = dataUSB["Time"].iloc[1] - dataUSB["Time"].iloc[0]
        lasttime = dataZwick[dataZwick["Cycle_Number [-]"] == CyclesUntilFailure].iloc[0]["Time [s]"]

        startCycle = 1
        starttimeUSB = dataZwick[dataZwick["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
        
        endtimeUSB = starttimeUSB + dataUSB[dataUSB["Time"] >= 0]["Time"].iloc[0]
        endCycle = dataZwick[dataZwick["Time [s]"] >= endtimeUSB].iloc[0]["Cycle_Number [-]"]
        
        startTemp = dataUSB[dataUSB["Time"] <= 0]["Temperature_Chamber"].iloc[-1]
        endTemp   = dataUSB[dataUSB["Time"] >= 0]["Temperature_Chamber"].iloc[0]
        startHum  = dataUSB[dataUSB["Time"] <= 0]["Humidity_Chamber"].iloc[-1]
        endHum    = dataUSB[dataUSB["Time"] >= 0]["Humidity_Chamber"].iloc[0]

        usbTemps.append(startTemp)
        usbHumiditys.append(startHum)
        
        steps = (endCycle - startCycle)/10
        for i in range (0, int((endCycle - startCycle)/10)):
            if  endTemp == startTemp:
                usbTemps.append(startTemp)
            else:
                temp = startTemp + ((endTemp - startTemp) / steps) * i
                usbTemps.append(temp)

            if endHum == startHum:
                usbHumiditys.append(startHum)
            else:
                hum = startHum + ((endHum - startHum) / steps) * i
                usbHumiditys.append(hum)
        
        startCycle = endCycle
        starttimeUSB = dataZwick[dataZwick["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
        endtimeUSB = starttimeUSB + freqUSB
        if endtimeUSB < lasttime:
            endCycle = dataZwick[dataZwick["Time [s]"] >= endtimeUSB].iloc[0]["Cycle_Number [-]"]
        else:
            endCycle = CyclesUntilFailure

        while startCycle < CyclesUntilFailure:
            if((startCycle-1)%1000 == 0):
                print(str(round(startCycle/CyclesUntilFailure,2)*100) + "%")
            startTemp = endTemp
            endTemp   = dataUSB[dataUSB["Time"] >= endtimeUSB]["Temperature_Chamber"].iloc[0]
            startHum  = endHum
            endHum    = dataUSB[dataUSB["Time"] >= endtimeUSB]["Humidity_Chamber"].iloc[0]
            
            steps = (endCycle - startCycle)/10
            for i in range (0, int((endCycle - startCycle)/10)):
                if  endTemp == startTemp:
                        usbTemps.append(startTemp)
                else:
                    temp = startTemp + ((endTemp - startTemp) / steps) * i
                    usbTemps.append(temp)

                if endHum == startHum:
                    usbHumiditys.append(startHum)
                else:
                    hum = startHum + ((endHum - startHum) / steps) * i
                    usbHumiditys.append(hum)
                

            startCycle = endCycle
            starttimeUSB = dataZwick[dataZwick["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
            endtimeUSB = starttimeUSB + freqUSB
            if endtimeUSB < lasttime:
                endCycle = dataZwick[dataZwick["Time [s]"] >= endtimeUSB].iloc[0]["Cycle_Number [-]"]
            else:
                endCycle = CyclesUntilFailure

        print(len(usbTemps))
        print(len(usbHumiditys))    	


##########################################################################################################################################################
# interpolating IR data
##########################################################################################################################################################
        
    print("Interpolating IR")

    if databaseTables[databaseInfrared]["localDataExists"]:
        # irSurface   = [0] * int(CyclesUntilFailure/10 + 1)
        # irInt       = [0] * int(CyclesUntilFailure/10 + 1)
        irSurface = []
        irChamber = []
        dataZwickTemp = dataZwick[["Cycle_Number [-]","Time [s]"]]
        prev = 0
        prevTimeIR = 0
        printer = True
        k = 0 
        i = 0
        timeges = 0 
        start1 = 0
        start4 = 0
        start2 = 0
        start3 = 0
        for row in dataZwickTemp.itertuples(index = True, name="Pandas"):
            start = time.process_time()
            next = row[1]
            nextTimeIR = prevTimeIR
            if row[1] != prev:
                if((next-1)%1000 == 0) and printer:
                    print(str(round(next/CyclesUntilFailure,2)*100) + "%")
                    # print(timeges/k*101)
                    # print((start2-start1)*1000)
                    # print((start3-start2)*1000)
                    # print((start4-start3)*1000)
                
                start1 = time.process_time()
                timeZwick = row[2]
                while nextTimeIR < timeZwick:
                    i += 1
                    prevTimeIR = nextTimeIR
                    nextTimeIR = dataInfrared["Time"].iloc[i]
                start2 = time.process_time()
                # tempSurface = dataInfrared[dataInfrared["Time"] >= timeZwick]["Surfacetemp_of_Specimen"].iloc[0]
                # tempChamber = dataInfrared[dataInfrared["Time"] >= timeZwick]["Temp_IR_intern_chamber"].iloc[0]
                tempSurface = dataInfrared["Surfacetemp_of_Specimen"].iloc[i]
                tempChamber = dataInfrared["Temp_IR_intern_chamber"].iloc[i]
                start3 = time.process_time()
                irSurface.append(tempSurface)
                irChamber.append(tempChamber)
                start4 = time.process_time()
                
            prev = next
            k += 1
            timeges += time.process_time() - start
           
        # dataZwickTemp = dataZwick[["Cycle_Number [-]","Time [s]"]]
        # # dataZwickTemp = dataZwick
        # steps = int(CyclesUntilFailure/10)+1
        
        # irSurface   = [0] * int(CyclesUntilFailure/10 + 1)
        # irInt       = [0] * int(CyclesUntilFailure/10 + 1)

        # freqIR = dataInfrared["Time"].iloc[1] - dataInfrared["Time"].iloc[0]
        # lasttimeIR = dataZwickTemp[dataZwickTemp["Cycle_Number [-]"] == CyclesUntilFailure].iloc[0]["Time [s]"]

        # startCycle = 1
        # starttimeIR = dataZwickTemp[dataZwickTemp["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
        
        # endtimeIR = starttimeIR + dataInfrared[dataInfrared["Time"] >= 0]["Time"].iloc[0]
        # endCycle = dataZwickTemp[dataZwickTemp["Time [s]"] >= endtimeIR].iloc[0]["Cycle_Number [-]"]

        
        # i = 0
        # n = 0
        # k = 0
        # timeges = 0
        # while startCycle < CyclesUntilFailure:
        #     start = time.process_time()
        #     tempSurf = dataInfrared[dataInfrared["Time"] <= starttimeIR]["Surfacetemp_of_Specimen"].iloc[-1]
        #     tempChamber = dataInfrared[dataInfrared["Time"] <= starttimeIR]["Temp_IR_intern_chamber"].iloc[-1]
        #     for j in range(0,int((endCycle - startCycle)/10)):
        #         irSurface[j+i] = tempSurf
        #         irInt[j+i]     = tempChamber
        #         n = j + 1
        #     i += n
        #     # TODO +10?
        #     print(time.process_time()-start)
        #     startCycle = endCycle
        #     # dataZwickTemp = dataZwickTemp[dataZwickTemp["Cycle_Number [-]"] >= startCycle]
        #     starttimeIR = dataZwickTemp[dataZwickTemp["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
        #     endtimeIR = starttimeIR + freqIR
        #     if endtimeIR < lasttimeIR:
        #         endCycle = dataZwickTemp[dataZwickTemp["Time [s]"] >= endtimeIR].iloc[0]["Cycle_Number [-]"]
        #     else:
        #         endCycle = CyclesUntilFailure
            
        #     # print(str(steps) + " " + str(i))
        #     k += 1
        #     end = time.process_time()
        #     timeges += (end - start)
        #     print(startCycle, timeges/k)
        #     if startCycle >= 1000:
        #         print(timeges)
        
        # tempSurf = dataInfrared[dataInfrared["Time"] <= starttimeIR + freqIR]["Surfacetemp_of_Specimen"].iloc[-1]
        # tempChamber = dataInfrared[dataInfrared["Time"] <= starttimeIR +freqIR]["Temp_IR_intern_chamber"].iloc[-1]
        # irSurface[-1] = tempSurf
        # irInt[-1]     = tempChamber
        
##########################################################################################################################################################
# Filling dataframe for export
##########################################################################################################################################################

    print("Filling dataframe for export")
    i = 1
    k = 0
    cumDissipatedEnergy = 0
    cumStoredEnergy = 0
    
    stressMax       = dataZwick[dataZwick["Cycle_Number [-]"] == CyclesUntilFailure - CyclesUntilFailure%10 + 1]["Force [N]"].max() / area
    stressMin       = dataZwick[dataZwick["Cycle_Number [-]"] == CyclesUntilFailure - CyclesUntilFailure%10 + 1]["Force [N]"].min() / area
    strainMax       = dataZwick[dataZwick["Cycle_Number [-]"] == CyclesUntilFailure - CyclesUntilFailure%10 + 1]["Specimen_strain"].max()
    strainMin       = dataZwick[dataZwick["Cycle_Number [-]"] == CyclesUntilFailure - CyclesUntilFailure%10 + 1]["Specimen_strain"].min()
    EDynAtFailure   = (stressMax-stressMin) / (strainMax-strainMin)
    
    stressMax       = dataZwick[dataZwick["Cycle_Number [-]"] == 1]["Force [N]"].max() / area
    stressMin       = dataZwick[dataZwick["Cycle_Number [-]"] == 1]["Force [N]"].min() / area
    strainMax       = dataZwick[dataZwick["Cycle_Number [-]"] == 1]["Specimen_strain"].max()
    strainMin       = dataZwick[dataZwick["Cycle_Number [-]"] == 1]["Specimen_strain"].min()
    EDynAt0         = (stressMax-stressMin) / (strainMax-strainMin)
    
    
    while i <= CyclesUntilFailure:
        if((i-1)%1000 == 0):
            print(str(round(i/CyclesUntilFailure,2)*100) + "%")

        lineDataCycle = []
        dataTemp = dataZwick[dataZwick["Cycle_Number [-]"] == i]
        lineDataCycle.append(i)
        
        lineDataCycle.append(dataTemp["Time [s]"].values[0])

        if(databaseTables[databaseInfrared]["localDataExists"]):
            #Surfacetemp of Specimen
            lineDataCycle.append(irSurface[k])
            #Temp IR
            lineDataCycle.append(irChamber[k])
        else:
            #Surfacetemp of Specimen
            lineDataCycle.append(float("nan"))
            #Temp IR
            lineDataCycle.append(float("nan"))
        

        if(databaseTables[databaseUSB]["localDataExists"]):
            #Temperature Chamber
            lineDataCycle.append(usbTemps[k])
            #HumidityChamber
            lineDataCycle.append(usbHumiditys[k])
        else:
            #Temperature Chamber
            lineDataCycle.append(float("nan"))
            #HumidityChamber
            lineDataCycle.append(float("nan"))


        #Force
        stressMax  = dataTemp["Force [N]"].max() / area
        stressMin  = dataTemp["Force [N]"].min() / area
        stressMean = (stressMax + stressMin) / 2
        stresses    = dataTemp["Force [N]"].values / area


        #Stress
        lineDataCycle.append(stressMax)
        lineDataCycle.append(stressMin)
        lineDataCycle.append(stressMean)


        #Strain
        strainMax  = dataTemp['Specimen_strain'].max()
        strainMin  = dataTemp['Specimen_strain'].min()
        strainMean = (strainMax + strainMin) / 2
        strains    = dataTemp['Specimen_strain'].values #* L0 TO DO TIMUR Keyword Trabzonspor *nicht mit der Basis multiplizieren

        
        

        #Dynamic Stiffness
        EDyn_n = (stressMax-stressMin) / (strainMax-strainMin)

        strainMax  = strainMax * 100
        strainMin  = strainMin * 100
        strainMean = strainMean * 100

        lineDataCycle.append(strainMax)
        lineDataCycle.append(strainMin)
        lineDataCycle.append(strainMean)

        lineDataCycle.append(EDyn_n)


        #DissipatedEnergy and StoredEnergy
        DissipatedEnergy = 0
        StoredEnergy = 0
        
        PrevFVal = stresses[-2] 
        PrevDVal = strains[-2]
        for j in range(0,stresses.size-1):
            FVal = stresses[j]
            DVal = strains[j]
            SliceArea = ((FVal + PrevFVal) / 2) * (DVal - PrevDVal)
            DissipatedEnergy += SliceArea
            if SliceArea > 0:
                StoredEnergy += SliceArea
            
            PrevFVal = FVal
            PrevDVal = DVal
            

        StoredEnergy -= DissipatedEnergy
        
        # J/mm^3 to kJ/m^3
        DissipatedEnergy *= 1000
        StoredEnergy     *= 1000

        cumDissipatedEnergy += DissipatedEnergy * 10 
        cumStoredEnergy     += StoredEnergy     * 10
        
        lineDataCycle.append(DissipatedEnergy)
        lineDataCycle.append(StoredEnergy)
        lineDataCycle.append(cumDissipatedEnergy)
        lineDataCycle.append(cumStoredEnergy)


        # tan_DELTA
        # tanDelta = (1/(2*math.pi))*(DissipatedEnergy/StoredEnergy)
        
        # lineDataCycle.append(tanDelta)
        lineDataCycle.append(0)

        
        # Damage D
        damage = (EDynAt0 - EDyn_n)/(EDynAt0 - EDynAtFailure)
        
        lineDataCycle.append(damage)

        # Strain rate
        lineDataCycle.append(0)
        
        
        # Storage Modulus
        # lineDataCycle.append(EDyn_n*math.sin(math.atan(tanDelta)))
        lineDataCycle.append(0)
        
        
        # Loss Modulus
        # lineDataCycle.append(EDyn_n*math.cos(math.atan(tanDelta)))
        lineDataCycle.append(0)


        # d(E_Dyn)/dN
        lineDataCycle.append(0)


        # Damping
        lineDataCycle.append(DissipatedEnergy/StoredEnergy)
        
        # For every cycle 100 data points are measured, so the material hysteresis can be caluclated
        # Stresses and Displacement100
        for j in range(0,stresses.size):
            line = []
            line.append(i)
            line.append(dataTemp["Time [s]"].values[j])     # Time              [s]
            line.append(stresses[j] / area)                 # Stress            [N/mm^2]
            line.append(strains[j] * 100)                   # Specimen strain   [%]
            listDataCycles100.append(line)

        listDataCycles.append(lineDataCycle)
        i += 10
        k += 1

    
    lenLDC = len(listDataCycles)
    # Strain rate
    listDataCycles[0][19]          = (listDataCycles[1][11] - listDataCycles[0][11]) / 10
    listDataCycles[lenLDC - 1][19] = (listDataCycles[lenLDC - 1][11] - listDataCycles[lenLDC - 2][11]) / 10
    # d(E_Dyn)/dN
    listDataCycles[0][22]          = (listDataCycles[1][12] - listDataCycles[0][12]) / 10
    listDataCycles[lenLDC - 1][22] = (listDataCycles[lenLDC - 1][12] - listDataCycles[lenLDC - 2][12]) / 10
    for i in range(1,lenLDC-1):
        # Strain rate
        listDataCycles[i][19]      = (listDataCycles[i + 1][11] - listDataCycles[i - 1][11]) / 20
        # d(E_Dyn)/dN
        listDataCycles[i][22]      = (listDataCycles[i + 1][12] - listDataCycles[i - 1][12]) / 20
    
    
    # print(len(listDataCycles))
    #Build Dataframe dataCyclic
    dataCyclic    = pd.DataFrame(listDataCycles , columns = list(databaseTables["mech_cyclic"]["columns"].keys())[1:])
    dataCyclic100 = pd.DataFrame(listDataCycles100 , columns = list(databaseTables["mech_cyclic100"]["columns"].keys())[1:])
    
    return dataCyclic, dataCyclic100