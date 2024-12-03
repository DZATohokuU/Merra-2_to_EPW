import os
from getpass import getpass
import platform
import shutil
from subprocess import Popen
import requests
import xarray as xr
import pandas as pd
import re
import math
import numpy as np
import pvlib
from concurrent.futures import ThreadPoolExecutor

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### 1.Get authorization files for downloading MERRA-2 Data ###
# Code of this part is from NASA website:
# https://lb.gesdisc.eosdis.nasa.gov/meditor/notebookviewer/?notebookUrl=https://github.com/nasa/gesdisc-tutorials/blob/main/notebooks/How_to_Generate_Earthdata_Prerequisite_Files.ipynb
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_authorize_1():
    homeDir = os.path.expanduser("~") + os.sep

    # Create .urs_cookies and .dodsrc files
    with open(homeDir + '.urs_cookies', 'w') as file:
        file.write('')
        file.close()
    with open(homeDir + '.dodsrc', 'w') as file:
        file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
        file.write('HTTP.NETRC={}.netrc'.format(homeDir))
        file.close()

    print('Saved .urs_cookies and .dodsrc to:', homeDir)

    # Copy dodsrc to working directory in Windows
    if platform.system() == "Windows":  
        shutil.copy2(homeDir + '.dodsrc', os.getcwd())
        print('Copied .dodsrc to:', os.getcwd())

    urs = 'urs.earthdata.nasa.gov'    # Earthdata URL to call for authentication
    prompts = ['Enter NASA Earthdata Login Username \n(or create an account at urs.earthdata.nasa.gov): ',
            'Enter NASA Earthdata Login Password: ']

    with open(homeDir + '.netrc', 'w') as file:
        file.write('machine {} login {} password {}'.format(urs, getpass(prompt=prompts[0]), getpass(prompt=prompts[1])))
        file.close()

    print('Saved .netrc to:', homeDir)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### 2. Download Merra-2 weather data from NASA ###
# Befor downloading, please login your NASA account at link below:
# https://disc.gsfc.nasa.gov/datasets?keywords=Merra-2&page=1&temporalResolution=1%20hour
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Define the base directory where the ORIGINAL files will be saved
base_dir = "2_Weather_File/MERRA-2_Data/"
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

def get_data_2():
    # Set the path to your text file containing URLs
    wind_file = "2_Weather_File/URL/Wind/subset_M2T1NXSLV_5.12.4_20241016_025913_.txt"
    
     #   Wind data library: MERRA-2 tavg1_2d_slv_Nx
     #   Download Method: Get File Subsets using OPeNDAP
     #   Output format: netCDF
     #   Variable Description                                          Units
     #   -------- ---------------------------------------------------- --------
     #   t2m      2-meter_air_temperature                              K
     #   u2m      2-meter_eastward_wind                                m/s
     #   v2m      2-meter_northward_wind                               m/s
     #   QV2m     2-meter_specific_humidity                            -
     #   t10m     10-meter_air_temperature                             K
     #   u10m     10-meter_eastward_wind                               m/s
     #   v10m     10-meter_northward_wind                              m/s
     #   T2MDEW   dew_point_temperature_at_2_m                         K
     #   u50m     eastward_wind_at_50_meters                           m/s
     #   v50m     northward_wind_at_50_meters                          m/s
     #   ps       surface_pressure                                     Pa
     #   TQL      total_precipitable_liquid_water(for comparison)      kg/m²

    solar_file = "2_Weather_File/URL/Solar/subset_M2T1NXRAD_5.12.4_20241202_175141_.txt"

     #   Solar data library: MERRA-2 tavg1_2d_rad_Nx
     #   Download Method: Get File Subsets using OPeNDAP
     #   Output format: netCDF
     #   Variable Description                                          Units
     #   -------- ---------------------------------------------------- --------
     #   SWGDN    Surface Incoming Shortwave Flux                      W/m²
     #   CLDFRC   Total Cloud Area Fraction                            NaN

    snow_file = "2_Weather_File/URL/Snow/subset_M2T1NXLND_5.12.4_20241202_232409_.txt"

     #   Snow data library: MERRA-2 tavg1_2d_lnd_Nx
     #   Download Method: Get File Subsets using OPeNDAP
     #   Output format: netCDF
     #   Variable Description                                          Units
     #   -------- ---------------------------------------------------- --------
     #   SNODP    Snow_depth                                           m


    precipitation_file = "2_Weather_File/URL/Precipitation/subset_M2T1NXFLX_5.12.4_20241015_052857_.txt"

     #   Precipitation data library: MERRA-2 tavg1_2d_flx_Nx
     #   Download Method: Get File Subsets using OPeNDAP
     #   Output format: netCDF
     #   Variable Description                                          Units
     #   -------- ---------------------------------------------------- --------
     #   PRECTOT  total_precipitation                                  kg/m²/s

    # Create subdirectories for each type of data if they don't exist
    wind_dir = os.path.join(base_dir, "Wind")
    solar_dir = os.path.join(base_dir, "Solar")
    snow_dir = os.path.join(base_dir, "Snow")
    precipitation_dir = os.path.join(base_dir, "Precipitation")

    for directory in [wind_dir, solar_dir, snow_dir, precipitation_dir]:
        os.makedirs(directory, exist_ok=True)

    # A dictionary to map the file to its folder
    files_to_folders = {
        wind_file: wind_dir,
        solar_file: solar_dir,
        snow_file: snow_dir,
        precipitation_file: precipitation_dir
    }

    def download_file(url, target_dir):

        try:
            response = requests.get(url)
            response.raise_for_status()

            # For different structure of links
            match = re.search(r'tavg1_2d.{20}', url)
            filename = match.group(0) if match else os.path.basename(url)

            file_path = os.path.join(target_dir, filename)

            with open(file_path, 'wb') as file:
                file.write(response.content)

            print(f"File from {url} downloaded and saved as {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {url}: {e}")

    # Multi-threaded Download
    with ThreadPoolExecutor() as general_executor, ThreadPoolExecutor(max_workers=5) as snow_executor:
        for data_file, target_dir in files_to_folders.items():
            with open(data_file, 'r') as file:
                urls = file.read().splitlines()[1:]  # Read URL list and skip the first line

            if "Snow" in target_dir:  # Check if the data being downloaded is snow-related
                print(f"Using limited threads (max_workers=5) for Snow data in {target_dir}")
                for url in urls:
                    snow_executor.submit(download_file, url, target_dir)
            else:
                print(f"Using default thread pool for data in {target_dir}")
                for url in urls:
                    general_executor.submit(download_file, url, target_dir)

    # Checking files number in each folder
    for folder_name, folder_path in files_to_folders.items():
        num_files = len(os.listdir(folder_path))
        print(f"Folder '{folder_path}' contains {num_files} files.")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### 3. Read and process the original data (NC4) ###
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Define the directory where the PROCESSED files will be saved
base_output_folder = '2_Weather_File/MERRA-2_Data_Processed/'
if not os.path.exists(base_output_folder):
    os.makedirs(base_output_folder)

def read_NC4_3(folders):

    for folder_path in folders:
        # Get the category name from the folder path (e.g., 'Precipitation', 'Snow')
        folder_name = os.path.basename(os.path.normpath(folder_path))

        # Create an output folder specific to the current data category
        output_folder = os.path.join(base_output_folder, folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # Get all NC4 file paths in the current folder
        nc4_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.nc4')]
        
        if not nc4_files:
            print(f"No NC4 files found in {folder_path}.")
            continue  # Skip to the next folder if no NC4 files are found

        # Read all NC4 files
        datasets = [xr.open_dataset(file) for file in nc4_files]

        # Combine all datasets along the time dimension
        combined_ds = xr.concat(datasets, dim='time')

        # Convert to pandas DataFrame and reset the index
        df = combined_ds.to_dataframe().reset_index()

        # Extract unique latitude and longitude combinations
        unique_locs = df[['lat', 'lon']].drop_duplicates()

        # Process each unique latitude and longitude combination
        for _, loc in unique_locs.iterrows():
            lat = loc['lat']
            lon = loc['lon']
            # Filter data for the current latitude and longitude
            df_loc = df[(df['lat'] == lat) & (df['lon'] == lon)]
            # Generate a new filename with the current folder name and coordinates
            filename = f'{output_folder}/lat_{lat}_lon_{lon}.csv'
            # Save the filtered data to a CSV file
            df_loc.to_csv(filename, index=False)
            print(f"Saved data for lat: {lat}, lon: {lon} to {filename}")

# List of folder paths containing NC4 files
folder_list = [os.path.join(base_dir, folder) for folder in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, folder))]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### 4. Make the EPW file  ###
# Info about EPW please check the link below:
# https://climate.onebuilding.org/papers/EnergyPlus_Weather_File_Format.pdf
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def make_epw_4():

    latitude = 35.4
    longitude = 119.3
    solar_path = os.path.join(base_output_folder, "Solar")
    
    # Find the closest latitude and longitude pair
    def find_closest_file(solar_path, latitude, longitude):
        files = [f for f in os.listdir(solar_path) if f.endswith('.csv')]
        
        pattern = r"lat_([-+]?\d*\.\d+|\d+)_lon_([-+]?\d*\.\d+|\d+)"
        
        closest_file = None
        min_distance = float('inf')
        
        for file in files:
            match = re.search(pattern, file)
            if match:
                file_lat = float(match.group(1))
                file_lon = float(match.group(2))
                
                distance = math.sqrt((file_lat - latitude) ** 2 + (file_lon - longitude) ** 2)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_file = file
        
        return closest_file

    # Read CSV
    processed_folder_list = [os.path.join(base_output_folder, folder) for folder in os.listdir(base_output_folder) if os.path.isdir(os.path.join(base_output_folder, folder))]

    df_precipitation = None
    df_snow = None
    df_solar = None
    df_wind = None

    # Lat and lon you prefer
    target_filename = find_closest_file(solar_path, latitude, longitude)

    # Iterate through each folder and read the files
    for folder in processed_folder_list:
        file_path = os.path.join(folder, target_filename)
        
        # Check if the file exists
        if os.path.exists(file_path):
            # Store data in different df based on different folder names
            if 'Precipitation' in folder:
                df_precipitation = pd.read_csv(file_path)
                print(f"Loaded Precipitation data from {file_path}")
            elif 'Snow' in folder:
                df_snow = pd.read_csv(file_path)
                print(f"Loaded Snow data from {file_path}")
            elif 'Solar' in folder:
                df_solar = pd.read_csv(file_path)
                print(f"Loaded Solar data from {file_path}")
            elif 'Wind' in folder:
                df_wind = pd.read_csv(file_path)
                print(f"Loaded Wind data from {file_path}")
        else:
            print(f"File not found: {file_path}")

    # Check for successful reads
    print("##DataFrames loaded successfully:##")
    print("Precipitation DataFrame:", df_precipitation is not None)
    print("Snow DataFrame:", df_snow is not None)
    print("Solar DataFrame:", df_solar is not None)
    print("Wind DataFrame:", df_wind is not None)
    
    # Calculate DNI, DHI from GHI
    df_solar['pd_time'] = pd.to_datetime(df_solar['time'])
    solar_position = pvlib.solarposition.get_solarposition(time=df_solar['pd_time'], latitude=latitude, longitude=longitude, pressure=df_wind['PS'], temperature=(df_wind['T2M']-273.15))
    df_solar['solar_zenith'] = solar_position['zenith'].values
    df_solar['day_of_year'] = df_solar['pd_time'].dt.dayofyear
    dni= pvlib.irradiance.disc(ghi=df_solar['SWGDN'].values, solar_zenith=df_solar['solar_zenith'].values, datetime_or_doy=df_solar['day_of_year'], pressure=df_wind['PS'].values)
    df_solar['DNI'] = dni['dni']
    df_solar['DHI'] = df_solar['SWGDN'] - df_solar['DNI'] * np.cos(np.radians(df_solar['solar_zenith']))
    scaleing_factor = 0.8985

    # Calculate relative humidity
    df_wind['e'] = (df_wind['QV2M'] * df_wind['PS']) / ( 0.622 + df_wind['QV2M'])
    df_wind['e_s'] = 6.112 * np.exp((17.67 *( df_wind['T2M']- 273.15)) / (df_wind['T2M'] - 273.15 + 243.5)) * 100
    df_wind['Relative Humidity'] = (df_wind['e'] / df_wind['e_s']) * 100  
    df_wind['Relative Humidity'] = df_wind['Relative Humidity'].clip(upper=110)

    # Calculate wind spead and direction
    df_wind['wind_speed'] = np.sqrt(df_wind['U2M']**2 + df_wind['V2M']**2)
    df_wind['wind_direction'] = np.degrees(np.arctan2(df_wind['U2M'], df_wind['V2M']))
    df_wind['wind_direction'] = (df_wind['wind_direction'] + 360) % 360
    
    # Analysis period (reset time zone from UTC to your research area)
    date_range = pd.date_range(start='2023-01-01 00:30:00', end='2023-12-31 23:30:00', freq='H', tz='Asia/Shanghai')

    def process_data(df):
        # Time zone, from UTC to China time
        df['time'] = pd.to_datetime(df['time']).dt.tz_localize('UTC')
        df['time'] = df['time'].dt.tz_convert('Asia/Shanghai')
        
        df_filtered = df[df['time'].isin(date_range)]
        return df_filtered

    df_wind_filtered = process_data(df_wind)
    df_solar_filtered = process_data(df_solar)
    df_snow_filtered = process_data(df_snow)
    df_precipitation_filtered = process_data(df_precipitation)

    epw_data = {
        'Year': date_range.year,
        'Month': date_range.month,
        'Day': date_range.day,
        'Hour': date_range.hour + 1,  # The time in EnergyPlus starts from 1.
        'Minute': [30] * len(date_range),
        'Data Source and Uncertainty Flags': ['?9?9?9?9E0?9?9?9?9*9?9?9?9?9?9?9?9?9*9*9?9*9'] * len(date_range),
        'Dry Bulb Temperature': df_wind_filtered['T2M'] - 273.15,
        'Dew Point Temperature': df_wind_filtered['T2MDEW'] - 273.15,
        'Relative Humidity': df_wind_filtered['Relative Humidity'],
        'Atmospheric Station Pressure': df_wind_filtered['PS'],
        'Extraterrestrial Horizontal Radiation': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Extraterrestrial Direct Normal Radiation': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Horizontal Infrared Radiation Intensity': [9999] * len(date_range), # Automaticly calculate from Dry Bulb Temperature, Dew Point Temperature and Opaque Sky Cover.
        'Global Horizontal Radiation': df_solar_filtered['SWGDN'] * scaleing_factor,
        'Direct Normal Radiation': df_solar_filtered['DNI'] * scaleing_factor,
        'Diffuse Horizontal Radiation': df_solar_filtered['DHI'] * scaleing_factor,
        'Global Horizontal Illuminance': [999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Direct Normal Illuminance': [999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Diffuse Horizontal Illuminance': [999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Zenith Luminance': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Wind Direction': df_wind_filtered['wind_direction'],
        'Wind Speed': df_wind_filtered['wind_speed'],
        'Total Sky Cover': (df_solar_filtered['CLDTOT'] * 10).round(),
        'Opaque Sky Cover': (df_solar_filtered['CLDTOT'] * 10).round(),
        'Visibility': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Ceiling Height': [99999] * len(date_range), # It is not currently used in EnergyPlus.
        'Present Weather Observation': [9] * len(date_range), # It is not currently used in EnergyPlus.
        'Present Weather Codes': [999999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Precipitable Water': [999] * len(date_range), # It is not currently used in EnergyPlus.
        'Aerosol Optical Depth': [0.999] * len(date_range), # It is not currently used in EnergyPlus.
        'Snow Depth': df_snow_filtered['SNODP'] * 100,  # m to cm
        'Days Since Last Snowfall': [99] * len(date_range), # It is not currently used in EnergyPlus.
        'Albedo': [0.99] * len(date_range), # It is not currently used in EnergyPlus.
        'Liquid Precipitation Depth': df_precipitation_filtered['PRECTOT'] * 3600,
        'Liquid Precipitation Quantity': [0] * len(date_range) # It is not currently used in EnergyPlus.
    }

    df_epw = pd.DataFrame(epw_data)

    # Path to the intermediate file, which will be deleted after the execution of Merra_to_EPW_2.py
    output_folder = '2_Weather_File/EPW/'
    os.makedirs(output_folder, exist_ok=True)
    df_epw.to_csv('2_Weather_File/EPW/hourly_data_2023.csv', index=False) 

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



get_authorize_1()
get_data_2()
read_NC4_3(folder_list)
make_epw_4()



