import pandas as pd
import numpy as np
import os

#Set your intermediate and Siren files path
ewp_file_path = '2_Weather_File/EPW/hourly_data_2023.csv'
siren_file_path = "2_Weather_File/MERRA-2_Data_Processed/Siren/solar_weather_35.5000_119.3750_2023.csv"

df_epw = pd.read_csv(ewp_file_path)
df_siren = pd.read_csv(siren_file_path, header=2)

# GHI, DNI, DHI and scaling
#  Some research found that Merra-2 data will over estimate the PV potential, thus, please confir with actual data and do the scaling
sum_GHI = df_siren['GHI'].sum() / 1000000
print(sum_GHI)

scaleing_factor = 0.8985
df_epw['Global Horizontal Radiation'] = df_siren['GHI'] * scaleing_factor
df_epw['Direct Normal Radiation'] = df_siren['DNI'] * scaleing_factor
df_epw['Diffuse Horizontal Radiation'] = df_siren['DHI'] * scaleing_factor

# Wind
df_epw['Wind Direction'] = df_siren['Wdir']
df_epw['Wind Speed'] = df_siren['Wspd']

pd.set_option('display.float_format', lambda x: '%.6f' % x)

# EPW file header ()
# The Header only records the main information of the weather data and is not involved in the calculation. Here the Header of Qingdao, China is used.
text = """LOCATION,Qingdao.Intl.AP,SD,CHN,SRC-TMYx,548570,35.5,119.375,8.0,10.1
DESIGN CONDITIONS,1,2021 ASHRAE Handbook -- Fundamentals - Chapter 14 Climatic Design Information,,Heating,1,-8.8,-6.9,-18.9,0.7,-1.4,-16.9,0.9,-0.9,11.4,-2.6,10.4,-2.2,2.7,340,0.487,Cooling,8,7.3,33.1,24.3,31.8,23.8,30.2,23.5,27.1,30.0,26.5,29.1,25.9,28.2,4.4,180,26.3,21.9,28.7,25.9,21.4,28.4,25.1,20.4,27.6,87.0,30.0,83.9,29.2,80.9,28.7,30.1,Extremes,10.2,9.0,7.9,-11.8,35.9,1.9,1.8,-13.1,37.2,-14.2,38.3,-15.2,39.3,-16.6,40.6
TYPICAL/EXTREME PERIODS,6,Summer - Week Nearest Max Temperature For Period,Extreme,7/27,8/ 2,Summer - Week Nearest Average Temperature For Period,Typical,6/29,7/ 5,Winter - Week Nearest Min Temperature For Period,Extreme,1/ 6,1/12,Winter - Week Nearest Average Temperature For Period,Typical,1/13,1/19,Autumn - Week Nearest Average Temperature For Period,Typical,10/20,10/26,Spring - Week Nearest Average Temperature For Period,Typical,4/12,4/18
GROUND TEMPERATURES,3,.5,,,,2.96,1.88,3.79,6.78,14.60,20.64,24.71,25.95,23.83,19.15,12.89,7.08,2,,,,6.92,5.00,5.39,6.98,12.21,16.94,20.73,22.76,22.33,19.67,15.36,10.78,4,,,,10.20,8.23,7.80,8.40,11.36,14.55,17.47,19.50,19.98,18.83,16.29,13.20
HOLIDAYS/DAYLIGHT SAVINGS,No,0,0,0
COMMENTS 1,""
COMMENTS 2,""
DATA PERIODS,1,1,Data,Sunday,1/ 1,12/31"""

with open('df_epwheader.txt', 'w') as f:
    f.write(text)

with open('df_epwheader.txt', 'r') as f:
    epwheader_content = f.read()

df_epw.to_csv('epw.txt', index=False, header=False)  

with open('epw.txt', 'r') as f:
    df_epw_content = f.read()

combined_content = epwheader_content + '\n' + df_epw_content

with open('2_Weather_File/EPW/EPW_from_Merra2.epw', 'w') as f:
    f.write(combined_content)

delete_list = ['epw.txt', 'df_epwheader.txt']
for delete in delete_list:
    if os.path.exists(delete):
        os.remove(delete)
        print(f"{delete} has been deleted")
    else:
        print(f"{delete} not exist")