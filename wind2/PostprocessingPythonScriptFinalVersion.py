#!/usr/bin/env python
# coding: utf-8

# In[9]:


#standard imports
import numpy as np
import pandas as pd
import functools
import matplotlib.pyplot as plt
import math
import os
import scipy
from scipy import signal
from scipy.signal import savgol_filter

#folder path to save it to
save_folder_path = '/Users/anton/Desktop/SaveFolderWTMT'#CHANGE1

#reading the two folder paths and creating master df
wind_folder_path = '/Users/anton/Desktop/WindCSVs'#CHANGE2
rpm_folder_path =  '/Users/anton/Desktop/RPMCSVs'#CHANGE3

wind_list = os.listdir(wind_folder_path)
rpm_list = os.listdir(rpm_folder_path)

wind_df = pd.DataFrame({'Wind CSV File Name': wind_list})
rpm_df = pd.DataFrame({'RPM CSV File Name': rpm_list})

def extract_substring(string):
    parts = string.split('_')
    return '_'.join(parts[:-1])

wind_df['Experiment Code'] = wind_df['Wind CSV File Name'].apply(extract_substring)
rpm_df['Experiment Code'] = rpm_df['RPM CSV File Name'].apply(extract_substring)

master_df = pd.merge(wind_df, rpm_df, on='Experiment Code')

master_df[['Date YYMMDD', 'Research Group', 'Rotor Type', 'Yaw Angle', 'Fan RPM', 'Experiment Number']] = master_df['Experiment Code'].str.split('_', expand=True)

#creating folders for results to be saved in later

parent_directory = save_folder_path

# Iterate over the DataFrame rows
for index, row in master_df.iterrows():
    folder_name = row['Experiment Code']
    folder_path = os.path.join(parent_directory, folder_name)
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# add empty columns for the values that are calculated in the versuchsanalyse() program
master_df['mean_vwind'] = None
master_df['median_vwind'] = None
master_df['max_vwind'] = None
master_df['max_cp'] = None
master_df['max_cp_rpm'] = None 
master_df['max_rpm'] = None

master_df.head()

def allcalculations(wind_csv, rpm_csv):
    wind_csv['t_v'] = wind_csv['# Time in s']
    wind_csv['volt'] = wind_csv['Differential pressure voltage as digital value in -']
    wind_csv['pabs'] = wind_csv['Static pressure in hPa']
    wind_csv['temp'] = wind_csv['Temperature in C']
    
    wind_csv['dp'] = wind_csv['volt']*2*5*10/1023
    Rs = 287.058
    wind_csv['rho'] = (wind_csv['pabs'] * 100) / (Rs * (wind_csv['temp'] + 273.15))
    wind_csv['v'] = np.sqrt(2 * wind_csv['dp'] / wind_csv['rho'])
    wind_csv['t_v'] = wind_csv['t_v'].astype(float)# / 10 ** 6
    
    rpm_csv['t'] = rpm_csv['# Time in s']
    rpm_csv['n'] = rpm_csv['Angular velocity in rad/s']
    rpm_csv['n_rpm'] = rpm_csv['Angular velocity in rad/s']*60/(2*math.pi)
    
    t = (rpm_csv['t'] - rpm_csv['t'].iloc[0])# / 10 ** 6
    dt = (t.iloc[-1] - t.iloc[0]) / len(t)
    fl = 25
    omega = signal.savgol_filter(rpm_csv['n'].astype(float) * 2 * np.pi / 60, window_length=fl, polyorder=3, deriv=0, delta=dt, mode='interp')
    opkt = signal.savgol_filter(rpm_csv['n'].astype(float) * 2 * np.pi / 60, window_length=fl, polyorder=3, deriv=1, delta=dt, mode='interp')
    theta = 0.4 #CHANGE4
    M = theta * opkt
    P = M * omega
    rpm_csv['t'] = t
    rpm_csv['opkt'] = opkt
    rpm_csv['M'] = M
    rpm_csv['P'] = P
    rpm_csv['omega'] = omega

    v_fit = scipy.interpolate.interp1d(wind_csv['t_v'], wind_csv['v'], kind='slinear', bounds_error=False, fill_value=1)
    p_fit = scipy.interpolate.interp1d(wind_csv['t_v'], wind_csv['pabs'], kind='slinear', bounds_error=False, fill_value=1)
    temp_fit = scipy.interpolate.interp1d(wind_csv['t_v'], wind_csv['temp'], kind='slinear', bounds_error=False, fill_value=1)

    Rs = 287.058
    rho = (p_fit(rpm_csv['t']) * 100) / (Rs * (temp_fit(rpm_csv['t']) + 273.15))
    R = 1 #CHANGE5
    A = R**2 * np.pi
    cp = (2 * rpm_csv['P']) / (A * rho * (v_fit(rpm_csv['t']))**3)
    rpm_csv['cp'] = cp
    
    return wind_csv, rpm_csv

def versuchsanalyse(experiment_code, wind_csv_filepath, rpm_csv_filepath):
    
    experiment_path = os.path.join(save_folder_path, experiment_code)
    
    wind_csv = pd.read_csv(wind_csv_filepath, sep=';')
    rpm_csv = pd.read_csv(rpm_csv_filepath, sep=';')

    
    wind_csv_calc, rpm_csv_calc = allcalculations(wind_csv, rpm_csv)

    
#values of interest
    mean_vwind = wind_csv_calc['v'].mean()
    median_vwind = wind_csv_calc['v'].median()
    max_vwind = wind_csv_calc['v'].max()
    
    max_cp = rpm_csv_calc['cp'].max()
   
    max_cp_rpm = rpm_csv_calc.loc[rpm_csv_calc['cp'].idxmax(), 'n_rpm']
    
    max_rpm = rpm_csv['n_rpm'].max()
    
    


    #generate diagrams
    plt.figure(figsize=(10, 6))
    x1 = rpm_csv_calc['n_rpm']
    y1 = rpm_csv_calc['cp']
    plt.plot(x1, y1, label = "cp", color='red', linestyle='solid', marker='s', markerfacecolor='blue', markersize=2)

    plt.xlabel('N_rpm')
    plt.ylabel('cp')
    plt.title('cp as a function of rpm')
    
    diagram1 = 'cp.png'
    
    diagram_path1 = os.path.join(experiment_path, diagram1)
    
    plt.savefig(diagram_path1)
    
    ###
    
    plt.figure(figsize=(10, 6))
    x2 = rpm_csv_calc['t']
    y2 = rpm_csv_calc['n_rpm']
    plt.plot(x2, y2, label = "cp", color='red', linestyle='solid', marker='s', markerfacecolor='blue', markersize=2)

    plt.xlabel('Time in s')
    plt.ylabel('Rotor rpm')
    plt.title('Rotor rpm over time')
    
    diagram2 = 'n_rpm.png'
    
    diagram_path2 = os.path.join(experiment_path, diagram2)
    
    plt.savefig(diagram_path2)
    
    #save diagrams and csvs
    
    wind_csv_end = 'wind_processed.csv'
    wind_excel_end = 'wind_processed.xlsx' 
    rpm_csv_end = 'rpm_processed.csv'
    rpm_excel_end = 'rpm_processed.xlsx' 
    
    
    wind_csv_path = os.path.join(experiment_path, wind_csv_end)
    wind_csv.to_csv(wind_csv_path, index=False)
    
    wind_excel_path = os.path.join(experiment_path, wind_excel_end)
    wind_csv.to_excel(wind_excel_path, index=False)
    
    rpm_csv_path = os.path.join(experiment_path, rpm_csv_end)
    rpm_csv.to_csv(rpm_csv_path, index=False)
    
    rpm_excel_path = os.path.join(experiment_path, rpm_excel_end)
    rpm_csv.to_excel(rpm_excel_path, index=False)
    
    return mean_vwind, median_vwind, max_vwind, max_cp, max_cp_rpm, max_rpm

for index, row in master_df.iterrows():
    experiment_code = row['Experiment Code']
    wind_csv_file = row['Wind CSV File Name']
    rpm_csv_file = row['RPM CSV File Name']
    
    wind_csv_filepath = os.path.join(wind_folder_path, wind_csv_file)
    rpm_csv_filepath = os.path.join(rpm_folder_path, rpm_csv_file)
    
    mean_vwind, median_vwind, max_vwind, max_cp, max_cp_rpm, max_rpm = versuchsanalyse(experiment_code, wind_csv_filepath, rpm_csv_filepath)

    
    master_df.at[index, 'mean_vwind'] = mean_vwind
    master_df.at[index, 'median_vwind'] = median_vwind
    master_df.at[index, 'max_vwind'] = max_vwind
    
    master_df.at[index, 'max_cp'] = max_cp 
    master_df.at[index, 'max_cp_rpm'] = max_cp_rpm
    master_df.at[index, 'max_rpm'] = max_rpm

    
#create summary scatter plot with max cp values
# Assuming you have three DataFrames: df_x, df_y, df_color

# Set up the figure and axes
fig, ax = plt.subplots()

# Extract the column values
x_values = master_df['max_cp_rpm']
y_values = master_df['max_cp']
color_values = master_df['max_vwind']

# Calculate the color scale range
color_min = min(color_values)
color_max = max(color_values)

# Create the scatter plot
scatter = ax.scatter(x_values, y_values, c=color_values, cmap='viridis')

# Set the colorbar
cbar = plt.colorbar(scatter)
cbar.set_label('Max wind speed during experiment')

# Set the limits and labels for the x and y axes
#ax.set_xlim(x_min, x_max)
#ax.set_ylim(y_min, y_max)
ax.set_xlabel('RPM at cp_max')
ax.set_ylabel('cp_max')

summary_diagram = 'cp_all_experiments.png'
    
summary_diagram_path = os.path.join(save_folder_path, summary_diagram)
    
plt.savefig(summary_diagram_path)


    
#save master df as csv and xlsx

master_df_csv_end = 'results_overview.csv'
master_df_excel_end = 'results_overview.xlsx' 

master_df_csv_path = os.path.join(save_folder_path, master_df_csv_end)
master_df.to_csv(master_df_csv_path, index=False)

master_df_excel_path = os.path.join(save_folder_path, master_df_excel_end)
master_df.to_excel(master_df_excel_path, index=False)

master_df.head()


# In[ ]:





# In[ ]:




