# Merra-2_to_epw
Generate EPW weather files using the MERRA-2 database.

## ⬇️Installation
Download the file package to the location where you want to run the program.

## 0️⃣ Data Preparation
1. Create a folder named: **2_Weather_File**, and a sub-folder **URL**.
2. Visit the NASA MERRA-2 website and click on “Login” in the top-right corner. (If you don’t have a NASA account, please register one.)
   https://disc.gsfc.nasa.gov/datasets?keywords=Merra-2&page=1&temporalResolution=1%20hour
3. Click the “**Subset / Get Data**” button for any database. (Refer to lines **63–110** of the Python file “**Merra_to_EPW.py**” for the required data content.)
 -  Download Method: Get File Subsets using OPeNDAP
 -  Method Options: Please set your research time range and region
 -  Select Variables: Refer to lines **63–110** of the Python file “**Merra_to_EPW.py**” for the required data content.
 -  Output Format: netCDF

    Then click “**Get Data**” and wait for the server to filter the data (approximately 30 seconds). After that, click “**Download Links List**” and save the downloaded   .txt file in the **URL** folder.

## 1️⃣ Code Preparation
1.All files will be saved in **2_Weather_File**. If you want to change the save path, please modify the code as follows:
 -  The storage path for downloading the **original** MERRA-2 files.(line 57)
 -  The paths of the four .txt files downloaded in the previous step.(line 63,83,93,103)
 -  The storage path for downloading the **processed** MERRA-2 files.(line 173)
 -  The path of EPW output folder.(line 374)
2. Modify the analysis period, follow the format below(line 318), and the time zone in line **323** as well.
```
date_range = pd.date_range(start='2023-01-01', end='2023-12-31 23:00:00', freq='H', tz='Asia/Shanghai')
```

3. Select a latitude and longitude combination, and enter it into line 229 and 230, following the format below:
```
target_filename = "lat_35.5_lon_119.375.csv"
```
## 2️⃣ EPW Generation
 -  Maintain the login status on the NASA MERRA-2 website **(mandatory)** and run the **Merra2_to_EPW.py**. Follow the prompts to enter your NASA website username and password to generate the certificate.
 -  The program will automatically download, read, process the MERRA-2 data, and generate the EPW file. You can grab a cup of coffee☕️ during this time; the entire process will take about 10 minutes (depending on your computer’s performance).

## 3️⃣ Annotation
Lines 380 to 387 in the code represent the header section of the EPW file. This section only records metadata information and will not be used during the simulation. Here, the weather data header is based on the weather data from Qingdao International Airport in Shandong Province, China. Unless there are other specific requirements, this part does not need to be modified.

