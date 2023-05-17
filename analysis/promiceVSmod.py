# %% [markdown]
# This notebook first displays the location of PROMICE AWSs and calculated the annual velocity based on the GPS record.
# Then it will extract the satellite pixel values and MODIS albedo prodcut at each AWS site.
# Results will be saved in csv files under the promice folder. 
# 
# 
# Users should change the size of spatial window when extracting the pixel values. 

# %%
import geemap
import ee
import pandas as pd
# import utm
import numpy as np
# import plotly.express as px

# %% [markdown]
# # PROMICE

# %%
df = pd.read_csv('promiceAlbedo.csv')
stations = df.aws.unique()
df.time = pd.to_datetime(df.time)
df = df[df.time>pd.to_datetime("2019-01-01")]
# %% [markdown]
# # GEE

# %%
Map = geemap.Map()
Map
# %%
# https://developers.google.com/earth-engine/tutorials/community/intro-to-python-api-guiattard by https://github.com/guiattard
def ee_array_to_df(arr, list_of_bands):
    """Transforms client-side ee.Image.getRegion array to pandas.DataFrame."""
    df = pd.DataFrame(arr)

    # Rearrange the header.
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)

    # Remove rows without data inside.
    df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

    # Convert the data to numeric values.
    for band in list_of_bands:
        df[band] = pd.to_numeric(df[band], errors='coerce')

    # Convert the time field into a datetime.
    df['datetime'] = pd.to_datetime(df['time'], unit='ms')

    # Keep the columns of interest.
    df = df[['time','datetime',  *list_of_bands]]

    return df

# %%
for i in range(len(stations)):
    stationName = stations[i]
    dfs = df[df.aws == stationName]
    dfs["Year"] = dfs.time.dt.year
    dfs["Month"] = dfs.time.dt.month
    # utmx, utmy, utmzoneNum, utmzoneLetter = utm.from_latlon(dfs.lat.values, dfs.lon.values)
    # dist = np.sqrt((utmx[0] - utmx[-1])**2 + (utmy[0] - utmy[-1])**2) / (dfs.Year.tail(1).values - dfs.Year.head(1).values)

    print('The station is: %s' % stationName)
    print('start from: %s end on: %s' % (dfs.time.head(1).values, dfs.time.tail(1).values))
    # print("the annual average ice flow rate is %.2f m\N{DOT OPERATOR}a\u207B\N{SUPERSCRIPT ONE}" %dist)
    if dfs.time.dt.year.min()>2020:
      print("skipping because year range is in sufficient")
      continue
    elif dfs.time.dt.year.max()<2022:
      print("skipping because year range is in sufficient")
      continue

    dfsYear = dfs.groupby(['Year']).mean() 
    dfsYear.reset_index(inplace=True)
    
    '''
    This part could help examine the annual ice velocity calculated from promice data.
    '''
    # for j in range(len(dfsYear)):
    #     # aoi = ee.Geometry.Point([dfsYear.lon[i], dfsYear.lat[i]]).buffer(300)
    #     # Map.addLayer(aoi, {}, str(dfsYear.Year[i]))
    #     utmx, utmy, utmzoneNum, utmzoneLetter = utm.from_latlon(dfsYear.lat[j], dfsYear.lon[j])
    #     dist = np.sqrt((utmx - utmx)**2 + (utmy - utmy)**2) / (dfsYear.Year.tail(1).values - dfs.Year.head(1).values)
    #     print('year: %d, coordinates:(%f, %f)' %(dfsYear.Year[j], dfsYear.lon[j], dfsYear.lat[j]))
    #     print("the average ice flow rate is %.2f m\N{DOT OPERATOR}a\u207B\N{SUPERSCRIPT ONE}" %dist)

    for j in range(len(dfsYear)):
        aoi = ee.Geometry.Point([dfsYear.gps_lon[j], dfsYear.gps_lat[j]])
        Map.addLayer(aoi, {}, str(dfsYear.Year[j]))
        date_start = str(dfsYear.Year[j]) + '-' + str(6) + '-' + str(1) 
        date_end = str(dfsYear.Year[j]) + '-' + str(8) + '-' + str(31) 
        # print(date_start)
        
        colFilter = ee.Filter.And(
            # ee.Filter.bounds(aoi),
            # ee.Filter.intersects('.geo', aoi),
            ee.Filter.geometry(aoi),
            ee.Filter.date(date_start, date_end)
        )

        modisCol = ee.ImageCollection('MODIS/006/MOD10A1').select(['Snow_Albedo_Daily_Tile', 'Snow_Albedo_Daily_Tile_Class']) \
            .filter(colFilter)#.map(maskMODIS)
        
        # if multiSat.size().getInfo()==0:
        #     continue

        pointValue = modisCol.getRegion(aoi, 500).getInfo() # 300 is the buffer radius
        dfpoint = ee_array_to_df(pointValue, ['Snow_Albedo_Daily_Tile'])
        pointValueFile = 'modis/' + stationName.replace("*", "-") + '.csv'
        # if os.path.exists(pointValueFile):
        if j==0:
            dfpoint.to_csv(pointValueFile, mode='w', index=False)
        else:
            dfpoint.to_csv(pointValueFile, mode='a', index=False, header=False)

# %%
