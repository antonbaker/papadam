##########################################################################################################################################################
#   
#   Institut für Kunststoffverarbeitung an der RWTH-Aachen
#   Research group: Fatigue, Acoustic, CAE, 
#   hakan.celik@ikv.rwth-aachen.de 
#   
#   
#   This is a postprocessing script to locally evaluate the fatigue data generated with the VHF7 testing machine with the Zwick Control
#
#   Author: Timur Goenuel
#   Version: 0.2.1
#   
#
##########################################################################################################################################################
# TODO
# -Downsampling



import os
import pandas as pd
from datetime import datetime  
from datetime import timedelta
import json
import matplotlib as mlt
import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import fatigue_read_data as frd
import fatigue_process_data as fpd
import sensor

def main_function(MainPath,SavePath,year,month,day,hour,minute,second,mikrosecond,offsetIR,offsetUSB,usedSensor,usedSensorplug,area,cycle_downsampling,decimal_separator):
##########################################################################################################################################################
# import config information
##########################################################################################################################################################

    with open("config_DB.json") as f:
        config_DB = json.load(f)

    databaseTables      = config_DB["databaseTables"]

    # name of the databases
    databaseZwick       = "mech_measurement"
    databaseInfrared    = "mech_infrared"
    databaseUSB         = "mech_usb"
    databaseCyclic      = "mech_cyclic"
    databaseCyclic100   = "mech_cyclic100"

    if(os.path.exists(MainPath+"\\time.txt")):
        with open("time.txt","r") as f:
            f.write("Something")


##########################################################################################################################################################
# import measurement data
##########################################################################################################################################################

    #initialising filenames to the data
    filenameDataZwick       = "NoFile"
    filenameDataInfrared    = "NoFile"
    filenameDataUSB         = "NoFile"

    #initialising the exist bool for the dataframes
    for table in databaseTables:
        databaseTables[table]["localDataExists"] = False

    #searching for the name of each file in the given path 
    if(os.path.exists(MainPath)): 
        for filename in os.listdir(MainPath):
            if(filename.split("_")[0] == "Probe" and filename.split("_")[2] == "Messwerte.csv"):
                filenameDataZwick    = filename
                
            # if(filename.split(".")[0] == "USBTemp" or filename.split(".")[0] == "Temp" or filename.split(".")[0] == "temp"):
            #     filenameDataUSB      = filename
            
            if(filename.split(".")[0] == "infrared" or filename.split(".")[0] == "Infrared" or filename.split(".")[0] == "infrarot" or filename.split(".")[0] == "Infrarot"):
                filenameDataInfrared = filename
        

        if(os.path.exists(MainPath + r"\\Zeit.txt")):
            with open(MainPath + r"\\Zeit.txt") as f:
                time_txt_exists = True
                for line in f:
                    line = line.replace("\n","").split("\t")
                    lineTime = line[2].split(":")
                    lineDate = line[0].split(".")
                    time0 = datetime(int(lineDate[2]), int(lineDate[1]), int(lineDate[0]), int(lineTime[0]), int(lineTime[1]), int(lineTime[2]), 0)
        else:
            time0 = datetime(year, month, day, hour, minute, second, mikrosecond)


        print("Reading")
        
        databaseTables[databaseZwick]["dataframe"]   , databaseTables[databaseZwick]["localDataExists"]    = fpd.processRawData(MainPath + '\\' + filenameDataZwick, databaseTables[databaseZwick]["originalName"], usedSensorplug, usedSensor)
        
        totalSecondsMeasured = databaseTables[databaseZwick]["dataframe"]["Time [s]"].iloc[-1]

        databaseTables[databaseInfrared]["dataframe"], databaseTables[databaseInfrared]["localDataExists"] = fpd.processInfraredData(MainPath + '\\' + filenameDataInfrared, databaseTables[databaseInfrared]["originalName"], time0, offsetIR, totalSecondsMeasured)
        databaseTables[databaseUSB]["dataframe"]     , databaseTables[databaseUSB]["localDataExists"]      = fpd.processUSBData(MainPath + '\\' + filenameDataUSB, databaseTables[databaseUSB]["originalName"], time0, offsetUSB, totalSecondsMeasured)


    # getting needed parameter to calculate cyclic data
        print("Processing")
        
        databaseTables[databaseCyclic]["dataframe"], databaseTables[databaseCyclic100]["dataframe"] = fpd.processDataCyclic(databaseTables, databaseZwick, databaseInfrared, databaseUSB, area,  usedSensorplug, usedSensor, cycle_downsampling)
        databaseTables[databaseCyclic]["localDataExists"]    = True
        databaseTables[databaseCyclic100]["localDataExists"] = True


    #TODO
    #calculating correct timeformat for export as date
    
    else:
        with open("warnings.txt", "w+") as f:
            f.write("Given path is wrong") 



###################################################################################################################################################
# Temp section to check with csv
###################################################################################################################################################

    if not os.path.exists(SavePath):
        os.makedirs(SavePath)

    print("Exporting CSVs")

    if databaseTables[databaseZwick]["localDataExists"]:
        databaseTables[databaseZwick]["dataframe"].to_csv(SavePath+"corrected_zwick.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        databaseTables[databaseCyclic]["dataframe"].to_csv(SavePath+"processed_cyclic.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        databaseTables[databaseCyclic100]["dataframe"].to_csv(SavePath+"processed_cyclic100.csv",encoding="latin1",sep=";",decimal=decimal_separator)

        databaseTables[databaseCyclic]["dataframe"][["Cycle_number [-]","Time [s]","Stress_Max [N/mm^2]","Stress_Min [N/mm^2]","Stress_Mean [N/mm^2]",]].to_csv(SavePath+"processed_Stress.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        databaseTables[databaseCyclic]["dataframe"][["Cycle_number [-]","Time [s]","Strain_Max [%]","Strain_Min [%]","Strain_Mean [%]","Strain_rate [%]"]].to_csv(SavePath+"processed_Strain.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        databaseTables[databaseCyclic]["dataframe"][["Cycle_number [-]","Time [s]","Dissipated_Energy [kJ/m^3]","Stored_Energy [kJ/m^3]","Cumulated_Dissipated_Energy [kJ/m^3]","Cumulated_Stored_Energy [kJ/m^3]"]].to_csv(SavePath+"processed_Energy.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        # databaseTables[databaseCyclic]["dataframe"][["Cycle_number [-]","Time [s]","E_Dyn [N/mm^2]","d(E_Dyn)/dN [N/mm^2]","Storage_Modulus [N/mm^2]","Loss_Modulus [N/mm^2]","tan_DELTA [-]"]].to_csv(SavePath+"processed_ViscoElastic.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        databaseTables[databaseCyclic]["dataframe"][["Cycle_number [-]","Time [s]","Surfacetemp_of_Specimen [°C]","Temp_IR_intern_chamber [°C]"]].to_csv(SavePath+"processed_Temperature_IR.csv",encoding="latin1",sep=";",decimal=decimal_separator)
        databaseTables[databaseCyclic]["dataframe"][["Cycle_number [-]","Time [s]","E_Dyn [N/mm^2]","d(E_Dyn)/dN [N/mm^2]","Damage D [-]"]].to_csv(SavePath+"processed_dynamic_Stiffness.csv",encoding="latin1",sep=";",decimal=decimal_separator)
    else:
        print("Zwick data is missing")


###################################################################################################################################################
# Temp section to export point values
###################################################################################################################################################

    if databaseTables[databaseZwick]["localDataExists"]:
        strainAtFailure         = (databaseTables[databaseCyclic]["dataframe"]["Strain_Mean [%]"].iloc[-1]+databaseTables[databaseCyclic]["dataframe"]["Strain_Mean [%]"].iloc[-2]+databaseTables[databaseCyclic]["dataframe"]["Strain_Mean [%]"].iloc[-3])/3
        CyclesUntilFailure      = databaseTables[databaseZwick]["dataframe"]["Cycle_Number [-]"].iloc[-1]
        CumDissEnergyAtFailure  = databaseTables[databaseCyclic]["dataframe"]["Cumulated_Dissipated_Energy [kJ/m^3]"].iloc[-1]
        CumStorEnergyAtFailure  = databaseTables[databaseCyclic]["dataframe"]["Cumulated_Stored_Energy [kJ/m^3]"].iloc[-1]

        AverageMaxStress    = 0
        AverageMinStress    = 0
        AverageMaxStrain    = 0
        AverageMinStrain    = 0
        AverageStrainrate   = 0
        AverageTemperature  = 0
        AverageDissEnergy   = 0
        AverageStorEnergy   = 0
        
        for index, row in databaseTables[databaseCyclic]["dataframe"].iterrows():
            leng = index + 1
            AverageMaxStress    += row["Stress_Max [N/mm^2]"]
            AverageMinStress    += row["Stress_Min [N/mm^2]"]
            AverageMaxStrain    += row["Strain_Max [%]"]
            AverageMinStrain    += row["Strain_Min [%]"]
            AverageStrainrate   += row["Strain_rate [%]"]
            AverageTemperature  += row["Surfacetemp_of_Specimen [\u00b0C]"]
            AverageDissEnergy   += row["Dissipated_Energy [kJ/m^3]"]
            AverageStorEnergy   += row["Stored_Energy [kJ/m^3]"]

        AverageMaxStress    = AverageMaxStress   / leng
        AverageMinStress    = AverageMinStress   / leng
        AverageMaxStrain    = AverageMaxStrain   / leng
        AverageMinStrain    = AverageMinStrain   / leng
        AverageStrainrate   = AverageStrainrate  / leng
        AverageTemperature  = AverageTemperature / leng
        AverageDissEnergy   = AverageDissEnergy  / leng
        AverageStorEnergy   = AverageStorEnergy  / leng
        
        outputColumns = ["Strain at Failure [%]","Cycles until Failure [-]","Average Stress_Max [N/mm^2]","Average Stress_Min [N/mm^2]","Average Strain_Max [%]","Average Strain_Min [%]","Average Strain rate [%]","Average Surfacetemp_of_Specimen [\u00b0C]","Average Dissipated_Energy [kJ/m^3]","Average Stored_Energy [kJ/m^3]","Cumulated_Dissipated_Energy [kJ/m^3]","Cumulated_Stored_Energy [kJ/m^3]"]
        outputList = [[strainAtFailure,CyclesUntilFailure,AverageMaxStress,AverageMinStress,AverageMaxStrain,AverageMinStrain,AverageStrainrate,AverageTemperature,AverageDissEnergy,AverageStorEnergy,CumDissEnergyAtFailure,CumStorEnergyAtFailure]]
        
        outputCSV = pd.DataFrame(outputList, columns = outputColumns)
        outputCSV.to_csv(SavePath+"onePoint.csv",encoding="latin1",sep=";",decimal=decimal_separator)

###################################################################################################################################################
# Temp section to export plots
###################################################################################################################################################

    print("Exporting Plots")

    if databaseTables[databaseZwick]["localDataExists"]:
        # Stress over cycles
        fig, ax = plt.subplots()
        cycles = databaseTables[databaseCyclic]["dataframe"]["Cycle_number [-]"].values
        stressMaxs = databaseTables[databaseCyclic]["dataframe"]["Stress_Max [N/mm^2]"].values
        stressMins = databaseTables[databaseCyclic]["dataframe"]["Stress_Min [N/mm^2]"].values
        stressMeans = databaseTables[databaseCyclic]["dataframe"]["Stress_Mean [N/mm^2]"].values

        ax.plot(cycles, stressMaxs, color="#ff0000", linewidth=2, label = "Stress_Max")
        ax.plot(cycles, stressMeans, color="#ff9900", linewidth=2, label = "Stress_Mean")
        ax.plot(cycles, stressMins, color="#00AC5B", linewidth=2, label = "Stress_Min")
        
        ax.set_xlabel("Cycle_number [-]")
        ax.set_ylabel("Stress [N/mm^2]")
        ax.set_xscale(value = "log")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
            fancybox=True, shadow=True, ncol=5)
        ax.set_title('Stress over cycles')

        fig.savefig(SavePath+'plot_stress.pdf')

        # Strain over cycles
        fig, ax = plt.subplots()
        cycles = databaseTables[databaseCyclic]["dataframe"]["Cycle_number [-]"].values
        strainMaxs = databaseTables[databaseCyclic]["dataframe"]["Strain_Max [%]"].values
        strainMins = databaseTables[databaseCyclic]["dataframe"]["Strain_Min [%]"].values
        strainMeans = databaseTables[databaseCyclic]["dataframe"]["Strain_Mean [%]"].values
        strainrates = databaseTables[databaseCyclic]["dataframe"]["Strain_rate [%]"].values

        ax.plot(cycles, strainMaxs, color="#ff0000", linewidth=2, label = "Strain_Max")
        ax.plot(cycles, strainMeans, color="#ff9900", linewidth=2, label = "Strain_Mean")
        ax.plot(cycles, strainMins, color="#00AC5B", linewidth=2, label = "Strain_Min")
        
        ax.set_xlabel("Cycle_number [-]")
        ax.set_ylabel("Strain [%]")
        ax.set_xscale(value = "log")

        ax2 = ax.twinx()
        ax2.set_ylabel("Strain rate [%]")
        ax2.plot(cycles, strainrates, color="#ff00ff", linewidth=0.5, label = "Strain_rate")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.33, -0.15),
            fancybox=True, shadow=True, ncol=5)
        ax2.legend(loc='upper center', bbox_to_anchor=(1, -0.15),
        fancybox=True, shadow=True, ncol=5)
        ax.set_title("Strain over cycles")

        
        fig.savefig(SavePath+'plot_strain.pdf')

        # Temperature over cycles
        fig, ax = plt.subplots()
        cycles = databaseTables[databaseCyclic]["dataframe"]["Cycle_number [-]"].values
        surfaceTemps = databaseTables[databaseCyclic]["dataframe"]["Surfacetemp_of_Specimen [\u00b0C]"].values
        internTemps = databaseTables[databaseCyclic]["dataframe"]["Temp_IR_intern_chamber [\u00b0C]"].values
        
        ax.plot(cycles, surfaceTemps, color="#ff9900", linewidth=2, label = "Surfacetemp_of_Specimen")
        ax.plot(cycles, internTemps, color="#00AC5B", linewidth=2, label = "Temp_IR_intern_chamber")
        
        ax.set_xlabel("Cycle_number [-]")
        ax.set_ylabel("[\u00b0C]")
        ax.set_xscale(value = "log")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
            fancybox=True, shadow=True, ncol=5)
        ax.set_title("Temperature over cycles")

        fig.savefig(SavePath+'plot_temperature.pdf')

        # Hystereses over cycles
        fig, ax = plt.subplots()
        cycles = []
        cycles.append(1)
        for i in range(1,10):
            cycle = CyclesUntilFailure * (i /10)
            cycles.append(cycle - cycle%10 + 1)
        cycles.append(CyclesUntilFailure - CyclesUntilFailure%10 + 1)

        Cyclic100 = databaseTables[databaseCyclic100]["dataframe"]
        
        stresses = []
        strains  = []

        for cycle in cycles:
            temp = Cyclic100[Cyclic100["Cycle_number [-]"] == cycle]
            line_stresses = temp["Stress [N/mm^2]"].values
            line_strains  = temp["Strain [%]"].values
            stresses.append(line_stresses)
            strains.append(line_strains)
        
        viridis = cm.get_cmap('viridis', 100)

        for i in range(0,len(stresses)):
            ax.plot(strains[i], stresses[i], color=viridis(i/len(stresses)), linewidth=2, label = cycles[i])
        
        ax.set_xlabel("Strain [%]")
        ax.set_ylabel("Stress [N/mm^2]")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.2,
                        box.width, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
            fancybox=True, shadow=True, ncol=5)
        # ax.set_title("Hystereses over cycles")

        fig.savefig(SavePath+'plot_hystereses.pdf')

        # Dynamic Stiffness over cycles
        fig, ax = plt.subplots()
        cycles = databaseTables[databaseCyclic]["dataframe"]["Cycle_number [-]"].values
        EDyns  = databaseTables[databaseCyclic]["dataframe"]["E_Dyn [N/mm^2]"].values
        dEDyns = databaseTables[databaseCyclic]["dataframe"]["d(E_Dyn)/dN [N/mm^2]"].values

        ax.plot(cycles, EDyns, color="#00AC5B", linewidth=2, label = "E_Dyn")
        
        ax.set_xlabel("Cycle_number [-]")
        ax.set_ylabel("E_Dyn [N/mm^2]")
        ax.set_xscale(value = "log")

        ax2 = ax.twinx()
        ax2.set_ylabel("d(E_Dyn)/dN [N/mm^2]")
        ax2.plot(cycles, dEDyns, color="#ff9900", linewidth=2, label = "d(E_Dyn)/dN [N/mm^2]")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.25, -0.15),
            fancybox=True, shadow=True, ncol=5)
        ax2.legend(loc='upper center', bbox_to_anchor=(0.75, -0.15),
        fancybox=True, shadow=True, ncol=5)

        fig.savefig(SavePath+'plot_dynStiff.pdf')

        # Dissipated Energy over cycles
        fig, ax = plt.subplots()
        cycles = databaseTables[databaseCyclic]["dataframe"]["Cycle_number [-]"].values
        dissEnergys = databaseTables[databaseCyclic]["dataframe"]["Dissipated_Energy [kJ/m^3]"].values
        cumDissEnergys = databaseTables[databaseCyclic]["dataframe"]["Cumulated_Dissipated_Energy [kJ/m^3]"].values
    
        ax.plot(cycles, dissEnergys, color="#00AC5B", linewidth=2, label = "Dissipated_Energy")
        
        ax.set_xlabel("Cycle_number [-]")
        ax.set_ylabel("Dissipated_Energy [kJ/m^3]")
        ax.set_xscale(value = "log")

        ax2 = ax.twinx()
        ax2.set_ylabel("Cumulated_Dissipated_Energy [kJ/m^3]")
        ax2.plot(cycles, cumDissEnergys, color="#ff9900", linewidth=2, label = "Cumulated_Dissipated_Energy")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.25, -0.15),
            fancybox=True, shadow=True, ncol=5)
        ax2.legend(loc='upper center', bbox_to_anchor=(0.75, -0.15),
        fancybox=True, shadow=True, ncol=5)
        ax.set_title("Dissipated Energy over cycles")

        fig.savefig(SavePath+'plot_dissEnergy.pdf')

        # Stored Energy over cycles
        fig, ax = plt.subplots()
        cycles = databaseTables[databaseCyclic]["dataframe"]["Cycle_number [-]"].values
        storEnergys = databaseTables[databaseCyclic]["dataframe"]["Stored_Energy [kJ/m^3]"].values
        cumStorEnergys = databaseTables[databaseCyclic]["dataframe"]["Cumulated_Stored_Energy [kJ/m^3]"].values
    
        ax.plot(cycles, storEnergys, color="#00AC5B", linewidth=2, label = "Stored_Energy")
        
        ax.set_xlabel("Cycle_number [-]")
        ax.set_ylabel("Stored_Energy [kJ/m^3]")
        ax.set_xscale(value = "log")

        ax2 = ax.twinx()
        ax2.set_ylabel("Cumulated_Stored_Energy [kJ/m^3]")
        ax2.plot(cycles, cumStorEnergys, color="#ff9900", linewidth=2, label = "Cumulated_Stored_Energy")

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])
        ax2.set_position([box.x0, box.y0 + box.height * 0.1,
                        box.width * 0.9, box.height * 0.9])

        # Put a legend below current axis
        ax.legend(loc='upper center', bbox_to_anchor=(0.25, -0.15),
            fancybox=True, shadow=True, ncol=5)
        ax2.legend(loc='upper center', bbox_to_anchor=(0.75, -0.15),
        fancybox=True, shadow=True, ncol=5)
        ax.set_title("Stored Energy over cycles")

        fig.savefig(SavePath+'plot_storEnergy.pdf')






    print("Finished")