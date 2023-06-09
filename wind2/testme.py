#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from pathlib import Path
from pandas import DataFrame
import functools
import pytest
import matplotlib.pyplot as plt
import math
import os
import scipy
from scipy import signal
from scipy.signal import savgol_filter


@pytest.fixture
def wind_csv_dataframe():
    HEREDIR = Path(__file__).resolve().parent
    return pd.read_csv(Path(HEREDIR) / '230607_R2_3D_0_400_a_wind.csv', sep=';')


@pytest.fixture
def rpm_csv_dataframe():
    HEREDIR = Path(__file__).resolve().parent
    return pd.read_csv(Path(HEREDIR) / '230607_R2_3D_0_400_a_rpm.csv', sep=';')


def allcalculations(wind_csv_df: DataFrame = None, rpm_csv_df: DataFrame = None) -> tuple:
    """
    This function takes in the wind and rpm csv files and returns the wind and
    rpm csv files with the calculated values appended to the end of the csv
    files

    Args:
        wind_csv_df (Pandas dataframe): Pandas dataframe of the wind csv file
        rpm_csv_df (Pandas dataframe): Pandas dataframe of the rpm csv file

    Returns:
        Tuple with wind_csv_df and rpm_csv_df, modified.
    """
    wind_csv_df['t_v'] = wind_csv_df['# Time in s']
    wind_csv_df['volt'] = wind_csv_df['Differential pressure voltage as digital value in -']
    wind_csv_df['pabs'] = wind_csv_df['Static pressure in hPa']
    wind_csv_df['temp'] = wind_csv_df['Temperature in C']
    
    wind_csv_df['dp'] = wind_csv_df['volt']*2*5*10/1023
    Rs = 287.058
    wind_csv_df['rho'] = (wind_csv_df['pabs'] * 100) / (Rs * (wind_csv_df['temp'] + 273.15))
    wind_csv_df['v'] = np.sqrt(2 * wind_csv_df['dp'] / wind_csv_df['rho'])
    wind_csv_df['t_v'] = wind_csv_df['t_v'].astype(float)# / 10 ** 6
    
    rpm_csv_df['t'] = rpm_csv_df['# Time in s']
    rpm_csv_df['n'] = rpm_csv_df['Angular velocity in rad/s']
    rpm_csv_df['n_rpm'] = rpm_csv_df['Angular velocity in rad/s']*60/(2*math.pi)
    
    t = (rpm_csv_df['t'] - rpm_csv_df['t'].iloc[0])# / 10 ** 6
    dt = (t.iloc[-1] - t.iloc[0]) / len(t)
    fl = 25
    omega = signal.savgol_filter(rpm_csv_df['n'].astype(float) * 2 * np.pi / 60, window_length=fl, polyorder=3, deriv=0, delta=dt, mode='interp')
    opkt = signal.savgol_filter(rpm_csv_df['n'].astype(float) * 2 * np.pi / 60, window_length=fl, polyorder=3, deriv=1, delta=dt, mode='interp')
    theta = 0.4 #CHANGE4
    M = theta * opkt
    P = M * omega
    rpm_csv_df['t'] = t
    rpm_csv_df['opkt'] = opkt
    rpm_csv_df['M'] = M
    rpm_csv_df['P'] = P
    rpm_csv_df['omega'] = omega

    v_fit = scipy.interpolate.interp1d(wind_csv_df['t_v'], wind_csv_df['v'], kind='slinear', bounds_error=False, fill_value=1)
    p_fit = scipy.interpolate.interp1d(wind_csv_df['t_v'], wind_csv_df['pabs'], kind='slinear', bounds_error=False, fill_value=1)
    temp_fit = scipy.interpolate.interp1d(wind_csv_df['t_v'], wind_csv_df['temp'], kind='slinear', bounds_error=False, fill_value=1)

    Rs = 287.058
    rho = (p_fit(rpm_csv_df['t']) * 100) / (Rs * (temp_fit(rpm_csv_df['t']) + 273.15))
    R = 1 #CHANGE5
    A = R**2 * np.pi
    cp = (2 * rpm_csv_df['P']) / (A * rho * (v_fit(rpm_csv_df['t']))**3)
    rpm_csv_df['cp'] = cp
    
    return wind_csv_df, rpm_csv_df

def test_wind_dataframe(capsys, wind_csv_dataframe, rpm_csv_dataframe):
    """@@@"""
    with capsys.disabled():
        print(wind_csv_dataframe)
        print(rpm_csv_dataframe)

