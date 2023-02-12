[Reserved for doi badge]
[Reserved for view count badge]
# Orbit drift effect on time series of MODIS snow albedo (MOD10A1)

This is part of a manuscript that will be under review (hopefully).

## Albedo Extraction
- [gee/randomSampleBuffer.js](gee/randomSampleBuffer.js)
- [gee/randomAlbedoExtraction.js](gee/randomAlbedoExtraction.js)

Albedo data include MOD10A1.006, MYD10A1.006, Harmonized Satellite Albedo, Sentinel -3 bare ice albedo were extracted at randomly generated sampling sites over the entire Greenland Ice Sheet. 
Functions for random sampling with buffer were made by Noel Gorelick and were modfied to adapt to our methodology. Ref: https://medium.com/google-earth/random-samples-with-buffering-6c8737384f8c

Due to memeory limitations on GEE and S3 albedo is not yet available on GEE, HSA and S3 albedo were extracted separately using the scripts below. 
- [analysis/randomAlbedoExtraction.py](analysis/randomAlbedoExtraction.py)
- [analysis/randomAlbedoExtractionS3.m](analysis/randomAlbedoExtractionS3.m)

The random sampling sites and PROMICE AWS data url links are all available in the shp folder. PROMICE AWS edition 4 data were batch downloaded and processed for analysis.
- [analysis/promiceawsV4.m](analysis/promiceawsV4.m)

## Orbit Drift Effect
- [analysis/modisViewTime.py](analysis/modisViewTime.py)
The view time of MODIS image can be extracted using the python api of GEE. 
Then the orbit drift effect can be quantified using the following scripts:
- [analysis/orbitDriftEffectMYD.py](analysis/orbitDriftEffectMYD.py)
- [analysis/orbitDriftEffectHSA.py](analysis/orbitDriftEffectHSA.py)
- [analysis/orbitDriftEffectS3.py](analysis/orbitDriftEffectS3.py)
- [analysis/orbitDriftEffect.py](analysis/orbitDriftEffect.py)

## Web Application
- [gee/MOD-orbit-drift-viewer.js](gee/MOD-orbit-drift-viewer.js)
- [gee/MOD-orbit-drift.js](gee/MOD-orbit-drift.js)

An EE web applicaiton ([MOD-orbit-drift-viewer, in test mode now](https://code.earthengine.google.com/fa48799ddc29c10f2fb931098f024941)) is available for users to interactively view the orbit drift effect, and extract time series of summer albedo (June-August) and orbidt drift effect at point of interest. 
It calculates the orbit drift (d(t)) at pixel level and adjusts the $median\Delta\alpha(t)$ for each pixel individually. 
The change is made to enable users to do a quick assessement of the d(t) globally. 
The area of interest covers the entire Greenland Ice Sheet and glaciers recorded in the GLIMS database. 
<!-- Due to limitations of GEE, the map tile projection cannot be changed. A better visulization is available in a separate web map ([MOD-orbit-drift](https://code.earthengine.google.com/6a1271c481952c663a6a3a4e54ae06c2), EPSG:3411). -->



```
+---analysis
|   |   modisViewTime.py
|   |   orbitDriftEffect.py      
|   |   orbitDriftEffectHSA.py   
|   |   orbitDriftEffectMYD.py   
|   |   orbitDriftEffectS3.py    
|   |   poicoord.csv
|   |   promiceawsV3.m
|   |   promiceawsV4.m
|   |   promiceCloud4.csv
|   |   randomAlbedoExtraction.py
|   |   randomAlbedoExtractionS3.m
|   |   stat.xlsx
|   |   untitled.m
|   |
|   \---print
|
+---archive
|       albedoMODISheatmap.py
|       solarZenithLatitudinalLandsat.py
|       solarZenithLatitudinalMODIS.py
|       viewTimeLatitudinalMODIS.py
|
+---gee
|       changeDetection.js
|       MOD-orbit-drift-viewer.js
|       MOD-orbit-drift.js
|       randomAlbedoExtraction.js
|       randomSampleBuffer.js
|
\---shp
        AWS_station_locationsV4.csv
        data_urls.csv
        data_urls_edition3.csv
        data_urls_edition4.csv
        poicoord.csv
        poiOrbitDrift.cpg
        poiOrbitDrift.dbf
        poiOrbitDrift.fix
        poiOrbitDrift.prj
        poiOrbitDrift.shp
        poiOrbitDrift.shx
```