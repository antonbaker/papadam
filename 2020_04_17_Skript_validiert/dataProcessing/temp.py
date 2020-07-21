#USB
    if(databaseTables[databaseUSB]["localDataExists"]):
        dataTempUSB  = dataUSB[dataUSB["Time"] >= offsetUSB]
        usbTemps     = []
        usbHumiditys = []
        dataTemp = dataZwick[dataZwick["Cycle_Number [-]"] == 1]
        time1 = dataTemp.iloc[0]["Time [s]"]
        time2 = time1 + offsetUSB
        dataTemp = dataZwick[dataZwick["Time [s]"] > time1]
        dataTemp = dataTemp[dataTemp["Time [s]"] <= time2]
        dataTempUSB.iloc[0]["Temperature_Chamber"] = dataTempUSB.iloc[0]["Temperature_Chamber"] + (dataTempUSB.iloc[1]["Temperature_Chamber"]-dataTempUSB.iloc[0]["Temperature_Chamber"]) * (offsetUSB/60)
        dataTempUSB.iloc[0]["Humidity_Chamber"]    = dataTempUSB.iloc[0]["Humidity_Chamber"] + (dataTempUSB.iloc[1]["Humidity_Chamber"]-dataTempUSB.iloc[0]["Humidity_Chamber"]) * (offsetUSB/60)

        size = dataTempUSB.shape[0]
        for i in range(0,size):
            
            steps = int(dataTemp["Time [s]"].shape[0]/101)
            print(steps)
            time1 = time2
            time2 = time1 + 60
            dataTemp = dataZwick[dataZwick["Time [s]"] > time1]
            dataTemp = dataTemp[dataTemp["Time [s]"] <= time2]
            startTemp = dataTempUSB.iloc[i]["Temperature_Chamber"]
            startHum  = dataTempUSB.iloc[i]["Humidity_Chamber"]
            if i + 1 < size and int(dataTemp["Time [s]"].shape[0]/101) > 0:
                endTemp = dataTempUSB.iloc[i+1]["Temperature_Chamber"]
                endHum = dataTempUSB.iloc[i+1]["Humidity_Chamber"]
            else:
                endTemp = startTemp
                endHum = startHum
            for j in range(0,steps):
                if  endTemp == startTemp:
                    usbTemps.append(startTemp)
                else:
                    temp = startTemp + ((endTemp - startTemp) / steps) * j
                    usbTemps.append(temp)

                if endHum == startHum:
                    usbHumiditys.append(startHum)
                else:
                    hum = startHum + ((endHum - startHum) / steps) * j
                    usbHumiditys.append(hum)
####################################################################################################
#IR
irSurface = []
        irInt     = []

        freqIR = dataInfrared["Time"].iloc[1] - dataInfrared["Time"].iloc[0]
        lasttime = dataZwick[dataZwick["Cycle_Number [-]"] == CyclesUntilFailure].iloc[0]["Time [s]"]

        startCycle = 1
        starttimeIR = dataZwick[dataZwick["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
        
        endtimeIR = starttimeIR + dataInfrared[dataInfrared["Time"] >= 0]["Time"].iloc[0]
        endCycle = dataZwick[dataZwick["Time [s]"] >= endtimeIR].iloc[0]["Cycle_Number [-]"]
        
        startSurf = dataInfrared[dataInfrared["Time"] <= 0]["Surfacetemp_of_Specimen"].iloc[-1]
        endSurf   = dataInfrared[dataInfrared["Time"] >= 0]["Surfacetemp_of_Specimen"].iloc[0]
        startInt  = dataInfrared[dataInfrared["Time"] <= 0]["Temp_IR"].iloc[-1]
        endInt    = dataInfrared[dataInfrared["Time"] >= 0]["Temp_IR"].iloc[0]

        irSurface.append(startSurf)
        irInt.append(startInt)
        
        steps = (endCycle - startCycle)/10
        for i in range (0, int((endCycle - startCycle)/10)):
            if  endSurf == startSurf:
                irSurface.append(startSurf)
            else:
                temp = startSurf + ((endSurf - startSurf) / steps) * i
                irSurface.append(temp)

            if endInt == startInt:
                irInt.append(startInt)
            else:
                hum = startInt + ((endInt - startInt) / steps) * i
                irInt.append(hum)
        
        startCycle = endCycle
        starttimeIR = dataZwick[dataZwick["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
        endtimeIR = starttimeIR + freqIR
        if endtimeIR < lasttime:
            endCycle = dataZwick[dataZwick["Time [s]"] >= endtimeIR].iloc[0]["Cycle_Number [-]"]
        else:
            endCycle = CyclesUntilFailure

        while startCycle < CyclesUntilFailure:
            if((startCycle-1)%1000 == 0):
                print(str(round(startCycle/CyclesUntilFailure,2)*100) + "%")
            startSurf = endSurf
            endSurf   = dataInfrared[dataInfrared["Time"] >= endtimeIR]["Surfacetemp_of_Specimen"].iloc[0]
            startInt  = endInt
            endInt    = dataInfrared[dataInfrared["Time"] >= endtimeIR]["Temp_IR"].iloc[0]
            
            steps = (endCycle - startCycle)/10
            for i in range (0, int((endCycle - startCycle)/10)):
                if  endSurf == startSurf:
                        irSurface.append(startSurf)
                else:
                    temp = startSurf + ((endSurf - startSurf) / steps) * i
                    irSurface.append(temp)

                if endInt == startInt:
                    irInt.append(startInt)
                else:
                    hum = startInt + ((endInt - startInt) / steps) * i
                    irInt.append(hum)
                

            startCycle = endCycle
            starttimeIR = dataZwick[dataZwick["Cycle_Number [-]"] == startCycle].iloc[0]["Time [s]"]
            endtimeIR = starttimeIR + freqIR
            if endtimeIR < lasttime:
                endCycle = dataZwick[dataZwick["Time [s]"] >= endtimeIR].iloc[0]["Cycle_Number [-]"]
            else:
                endCycle = CyclesUntilFailure