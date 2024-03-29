[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8040445.svg)](https://doi.org/10.5281/zenodo.8040445)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Ffsn1995%2Forbit-drift-MODIS-ice-albedo&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
# Orbital drift effect on time series of MODIS snow albedo (MOD10A1)

This repository contains code used in a manuscript that is submitted for peer review. The code extracts albedo data from various sources, including MOD10A1.006, MYD10A1.006, Harmonized Satellite Albedo, and Sentinel-3 bare ice albedo. The data is extracted at randomly generated sampling sites over the entire Greenland Ice Sheet.

Feng, S., Wehrlé, A., Cook, J.M., Anesio, A.M., Box, J.E., Benning, L.G., Tranter, M., 2024. The apparent effect of orbital drift on time series of MODIS MOD10A1 albedo on the Greenland ice sheet. Sci. Remote Sens. 9, 100116. https://doi.org/10.1016/j.srs.2023.100116


## Albedo Extraction
- [gee/randomSampleBuffer.js](gee/randomSampleBuffer.js)
- [gee/randomAlbedoExtraction.js](gee/randomAlbedoExtraction.js)

Albedo data include MOD10A1.006, MYD10A1.006, Harmonized Satellite Albedo, Sentinel-3 bare ice albedo were extracted at randomly generated sampling sites over the entire Greenland Ice Sheet. 
Functions for random sampling with buffer were made by Noel Gorelick and were modfied to adapt to our methodology. Ref: https://medium.com/google-earth/random-samples-with-buffering-6c8737384f8c
Run the script in GEE code editor and the albedo data will be exported to your Google Drive.

Due to memeory limitations on GEE and S3 albedo is not yet available on GEE, HSA and S3 albedo were extracted separately using the scripts below. 
- [analysis/randomAlbedoExtraction.py](analysis/randomAlbedoExtraction.py), using GEE python api. 
- [analysis/randomAlbedoExtractionS3.m](analysis/randomAlbedoExtractionS3.m), using [geotiffinterp](https://www.mathworks.com/matlabcentral/fileexchange/47899-geotiffinterp) made by [Chad Greene](https://github.com/chadagreene). 

The random sampling sites and PROMICE AWS data url links are all available in the shp folder. PROMICE AWS edition 4 data were batch downloaded and processed for analysis.
Point scale albeod data are extracted using the scripts in the [development and validation of harmonized satellite albedo](https://github.com/fsn1995/Remote-Sensing-of-Albedo)
- [analysis/promiceawsV4.m](analysis/promiceawsV4.m)

## Orbital Drift Effect
- [analysis/modisViewTime.py](analysis/modisViewTime.py)
The view time of MODIS image can be extracted using the python api of GEE. 
Then the orbital drift effect can be quantified using the following scripts:
- [analysis/orbitDriftEffectMYD.py](analysis/orbitDriftEffectMYD.py)
- [analysis/orbitDriftEffectHSA.py](analysis/orbitDriftEffectHSA.py)
- [analysis/orbitDriftEffectS3.py](analysis/orbitDriftEffectS3.py)
- [analysis/orbitDriftEffect.py](analysis/orbitDriftEffect.py)
- [analysis/dtmapping.m](analysis/dtmapping.m), using the [Arctic Mapping Tools](https://se.mathworks.com/matlabcentral/fileexchange/63324-arctic-mapping-tools) made by [Chad Greene](https://github.com/chadagreene).

Those scripts will produce the figures in the manuscript. 

## Web Application
- [gee/MOD-orbit-drift-viewer.js](gee/MOD-orbit-drift-viewer.js)
- [gee/MOD-orbit-drift.js](gee/MOD-orbit-drift.js)

An EE web applicaiton ([MOD-orbit-drift-viewer](https://fsn1995.users.earthengine.app/view/modis-orbit-drift-viewer)) is available for users to interactively view the orbital drift effect, and extract time series of summer albedo (June-August) and orbidt drift effect at point of interest. 
It calculates the orbital drift (d(t)) at pixel level and adjusts the $median\Delta\alpha(t)$ for each pixel individually. 
The change is made to enable users to do a quick assessement of the d(t) globally. 
The area of interest covers the entire Greenland Ice Sheet and glaciers recorded in the GLIMS database. 
It's updated to MOD10A1.061 and MYD10A1.061 now.
<!-- Due to limitations of GEE, the map tile projection cannot be changed. A better visulization is available in a separate web map ([MOD-orbit-drift](https://code.earthengine.google.com/6a1271c481952c663a6a3a4e54ae06c2), EPSG:3411). -->

# citation
```
@article{FENG2024100116,
title = {The apparent effect of orbital drift on time series of MODIS MOD10A1 albedo on the Greenland ice sheet},
journal = {Science of Remote Sensing},
volume = {9},
pages = {100116},
year = {2024},
issn = {2666-0172},
doi = {https://doi.org/10.1016/j.srs.2023.100116},
url = {https://www.sciencedirect.com/science/article/pii/S266601722300041X},
author = {Shunan Feng and Adrien Wehrlé and Joseph Mitchell Cook and Alexandre Magno Anesio and Jason Eric Box and Liane G. Benning and Martyn Tranter},
keywords = {Orbit drift, MODIS, Albedo, Greenland ice sheet, Time series, Google Earth Engine}}
```

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
|   |   dtmapping.m
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
