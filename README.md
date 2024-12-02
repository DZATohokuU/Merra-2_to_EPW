# Merra-2_to_epw
Generate EPW weather files using the MERRA-2 database.

## ⬇️Installation
Download the file package to the location where you want to run the program.

## 0️⃣ Preparation
1. Create 4 folders named: **EPW**, **MERRA-2_Data**, **MERRA-2_Data_Processed**, and **URL**.
2. Visit the NASA MERRA-2 website and click on “Login” in the top-right corner. (If you don’t have a NASA account, please register one.)
   https://disc.gsfc.nasa.gov/datasets?keywords=Merra-2&page=1&temporalResolution=1%20hour
3. Click the “**Subset / Get Data**” button for any database. (Refer to lines **58–106** of the Python file “**Merra_to_EPW_1.py**” for the required data content.)
 -  Download Method: Get File Subsets using OPeNDAP
 -  Method Options: Please set your research time range and region
 -  Select Variables: Refer to lines **58–106** of the Python file “**Merra_to_EPW_1.py**” for the required data content.
 -  Output Format: netCDF

    Then click “**Get Data**” and wait for the server to filter the data (approximately 30 seconds). After that, click “**Download Links List**” and save the downloaded   .txt file in the **URL** folder.
## 1️⃣ Merra2_to_EPW_1 (Generate all weather data except for GHI, DHI, and DNI）
1.Please modify the file save path in the code:
 -  The storage path for downloading the **original** MERRA-2 files.(line 54)
 -  The paths of the four .txt files downloaded in the previous step.(line 58,78,89,99)
 -  The storage path for downloading the **processed** MERRA-2 files.(line 164)
 -  The storage path for the CSV file used to run **Merra2_to_EPW_2**.(line 307,309)
2. Modify the analysis period, follow the format below(line 218)
```
date_range = pd.date_range(start='2023-01-01', end='2023-12-31 23:00:00', freq='H')
```
3. Comment out line **315**, and then run the program.(so that the program runs only the first to third parts)
4. Open any subfile under **MERRA-2_Data_Processed**, select a latitude and longitude combination, and enter it into line 229, following the format below:
```
target_filename = "lat_35.5_lon_119.375.csv"
```
Uncomment line **315** and commend out line **312-314**, then run the program again.(so that the program runs only the forth parts)
## 2️⃣ Generate GHI, DHI, and DNI
1. Download SIREN software from the link: https://sourceforge.net/projects/sensiren/
2. 
