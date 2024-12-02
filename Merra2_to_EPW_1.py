import os
from getpass import getpass
import platform
import shutil
from subprocess import Popen
import requests
import xarray as xr
import pandas as pd
import re
import numpy as np

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### 1.Get authorization files for downloading MERRA-2 Data ###
# Code of this part is from NASA website:
# https://lb.gesdisc.eosdis.nasa.gov/meditor/notebookviewer/?notebookUrl=https://github.com/nasa/gesdisc-tutorials/blob/main/notebooks/How_to_Generate_Earthdata_Prerequisite_Files.ipynb
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_authorize():
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
# https://disc.gsfc.nasa.gov/datasets？keywords=merra2&page=1&temporalResolution=1%20hour
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Define the base directory where the ORIGINAL files will be saved
base_dir = "2_Weather_File/MERRA-2_Data/"

def get_data():
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

    solar_file = "2_Weather_File/URL/Solar/subset_M2T1NXRAD_5.12.4_20241015_030951_.txt"

     #   Solar data library: MERRA-2 tavg1_2d_rad_Nx
     #   Download Method: Get File Subsets using OPeNDAP
     #   Output format: netCDF
     #   Variable Description                                          Units
     #   -------- ---------------------------------------------------- --------
     #   SWGDN    Surface Incoming Shortwave Flux                      W/m²
     #   SWGNT    Surface Net Downward Longwave Flux                   W/m²
     #   CLDFRC   Total Cloud Area Fraction                            NaN

    snow_file = "2_Weather_File/URL/Snow/subset_M2T1NXLND_5.12.4_20241015_052026_.txt"

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

    # Iterate through each file and download the contents into the correct folder
    for data_file, target_dir in files_to_folders.items():
        with open(data_file, 'r') as file:
            urls = file.read().splitlines()[1:]

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()

                # Wind data's file name is different with others
                match = re.search(r'tavg1_2d.{20}', url)

                filename = match.group(0)

                file_path = os.path.join(target_dir, filename)

                # Save files to folder
                with open(file_path, 'wb') as file:
                    file.write(response.content)

                print(f"File from {url} downloaded and saved as {file_path}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")
    # Check files number in each folder
    for folder_name, folder_path in files_to_folders.items():
        num_files = len(os.listdir(folder_path))
        print(f"Folder '{folder_path}' contains {num_files} files.")
    # Clean variables
    local_vars = locals().copy()  
    for var in local_vars:
        if var != "local_vars" or var != "base_dir": 
            del locals()[var]     

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
### 3. Read and process the original data (NC4) ###
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Define the directory where the PROCESSED files will be saved
base_output_folder = '2_Weather_File/MERRA-2_Data_Processed/'

def read_NC4(folders):

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

def make_epw():
    # Analysis period
    date_range = pd.date_range(start='2023-01-01', end='2023-12-31 23:00:00', freq='H')

    # Read CSV
    processed_folder_list = [os.path.join(base_output_folder, folder) for folder in os.listdir(base_output_folder) if os.path.isdir(os.path.join(base_output_folder, folder))]

    df_precipitation = None
    df_snow = None
    df_solar = None
    df_wind = None

    # Lat and lon you prefer
    target_filename = "lat_35.5_lon_119.375.csv"

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

    # Calculate relative humidity
    df_wind['e'] = (df_wind['QV2M'] * df_wind['PS']) / ( 0.622 + df_wind['QV2M'])
    df_wind['e_s'] = 6.112 * np.exp((17.67 *( df_wind['T2M']- 273.15)) / (df_wind['T2M'] - 273.15 + 243.5)) * 100
    df_wind['Relative Humidity'] = (df_wind['e'] / df_wind['e_s']) * 100  
    df_wind['Relative Humidity'] = df_wind['Relative Humidity'].clip(upper=110)

    epw_data = {
        'Year': date_range.year,
        'Month': date_range.month,
        'Day':date_range.day,
        'Hour': date_range.hour + 1,
        'Minute': [30] * len(date_range),
        'Data Source and Uncertainty Flags':['?9?9?9?9E0?9?9?9?9*9?9?9?9?9?9?9?9?9*9*9?9*9'] * len(date_range),
        'Dry Bulb Temperature':df_wind['T2M'].iloc[25:8785] - 273.15,
        'Dew Point Temperature':df_wind['T2MDEW'].iloc[25:8785] - 273.15,
        'Relative Humidity':df_wind['Relative Humidity'].iloc[25:8785],
        'Atmospheric Station Pressure':df_wind['PS'].iloc[25:8785],
        'Extraterrestrial Horizontal Radiation': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Extraterrestrial Direct Normal Radiation': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Horizontal Infrared Radiation Intensity': [9999] * len(date_range), # Automaticly calculate from Dry Bulb Temperature, Dew Point Temperature and Opaque Sky Cover.
        'Global Horizontal Radiation': None,
        'Direct Normal Radiation': None,
        'Diffuse Horizontal Radiation': None,
        'Global Horizontal Illuminance': [999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Direct Normal Illuminance': [999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Diffuse Horizontal Illuminance': [999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Zenith Luminance': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Wind Direction': None,
        'Wind Speed': None,
        'Total Sky Cover':((df_solar['CLDTOT'].iloc[25:8785]) * 10).round(),
        'Opaque Sky Cover':((df_solar['CLDTOT'].iloc[25:8785]) * 10).round(),
        'Visibility': [9999] * len(date_range), # It is not currently used in EnergyPlus.
        'Ceiling Height': [99999] * len(date_range), # It is not currently used in EnergyPlus.
        'Present Weather Observation': [9] * len(date_range), # It is not currently used in EnergyPlus.
        'Present Weather Codes': [999999999] * len(date_range), # It is not currently used in EnergyPlus.
        'Precipitable Water': [999] * len(date_range), # It is not currently used in EnergyPlus.
        'Aerosol Optical Depth': [0.999] * len(date_range), # It is not currently used in EnergyPlus.
        'Snow Depth':df_snow['SNODP'].iloc[25:8785] * 100, # m to cm
        'Days Since Last Snowfall': [99] * len(date_range), # It is not currently used in EnergyPlus.
        'Albedo': [0.99] * len(date_range), # It is not currently used in EnergyPlus.
        'Liquid Precipitation Depth':df_precipitation['PRECTOT'].iloc[25:8785] * 3600,
        'Liquid Precipitation Quantity':[0] * len(date_range) # It is not currently used in EnergyPlus.
    }

    df_epw = pd.DataFrame(epw_data)

    # Path to the intermediate file, which will be deleted after the execution of Merra_to_EPW_2.py
    output_folder = '2_Weather_File/EPW/'
    os.makedirs(output_folder, exist_ok=True)
    df_epw.to_csv('2_Weather_File/EPW/hourly_data_2023.csv', index=False) 


#get_authorize()
#get_data()
#read_NC4(folder_list)
make_epw()



