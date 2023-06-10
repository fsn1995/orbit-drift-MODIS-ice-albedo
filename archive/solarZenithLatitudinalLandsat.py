# %% 
import geemap
import ee
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
# %%
Map = geemap.Map()
Map

# %%
"""
Extract the solar zenith angle along different latitudes
"""
date_start = "2013-03-18"
date_end   = "2014-12-31"
# poi = ee.Geometry.Point(-37.38, 72.58) # GRIP

arctic_circle_transect = ee.Geometry.LineString(
    [[-180, 66.5], [180, 66.5]], proj="EPSG:4326", geodesic=False
)
Map.addLayer(arctic_circle_transect, {}, 'Arctic Circle')
everest_transect = ee.Geometry.LineString(
    [[-180, 27.9881], [180, 27.9881]], proj="EPSG:4326", geodesic=False
)
Map.addLayer(everest_transect, {}, 'Mt. Everest')
zermatt_transect = ee.Geometry.LineString(
    [[-180, 46.0207], [180, 46.0207]], proj="EPSG:4326", geodesic=False
)
Map.addLayer(zermatt_transect, {}, 'Mt. Zermatt')

dataset = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA").select("SZA") 

# %% get the solar zenith angle profile

def get_solar_zenith_angle_transect(img_col, scale, transect):
    """
    This is to extract solar zenith angle along the transect.
    img_col: the image collection
    scale: in meters
    transect: vector defined by ee.LineString
    """
    colFilter = ee.Filter.And(
        ee.Filter.geometry(transect), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
        ee.Filter.date(date_start, date_end),
        ee.Filter.dayOfYear(173, 173) # doy 173+-8 June 22 near summer solstice
    )    
    img_col = img_col.filter(colFilter)

    col_size = img_col.size().getInfo()
    solar_zenith_angle = np.ones((col_size, 1))
    img_time = np.ones((col_size, 1))
    imgList = img_col.toList(col_size)
    print("%.d images in this img collection" % col_size)

    for i in range(col_size):
        img = ee.Image(imgList.get(i))
        extractTransect = img.reduceRegion(**{
            'reducer': ee.Reducer.toList(),
            'geometry': transect,
            'scale': scale,
            'tileScale': 6
        })
        solar_zenith_angle[i] = pd.DataFrame(extractTransect.getInfo()).mean()
        img_time[i] = img.get('system:time_start').getInfo()
        df = pd.DataFrame(data=np.column_stack([img_time, solar_zenith_angle / 100]), columns=['timestamp', 'SolarZenith'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# %%

df_arctic_ciricle = get_solar_zenith_angle_transect(
    img_col=dataset,
    scale=500,
    transect=arctic_circle_transect
)
# df_everest = get_solar_zenith_angle_transect(
#     img_col=dataset,
#     scale=500,
#     transect=everest_transect
# )
# df_zermatt = get_solar_zenith_angle_transect(
#     img_col=dataset,
#     scale=500,
#     transect=zermatt_transect
# )

# df_arctic_ciricle.to_csv("sza_Arctic_Circle_Terra.csv", mode="w")
# df_arctic_ciricle.to_csv("sza_Arctic_Circle_Aqua.csv", mode="w")

# %%
fig, ax = plt.subplots(figsize=(8,5))

sns.lineplot(
    data=df_arctic_ciricle,
    x="datetime",
    y="SolarZenith",
    label="Arctic Circle (66.5$^\circ$N)",
    markers=True,
    marker="o"
)
sns.lineplot(
    data=df_zermatt,
    x="datetime",
    y="SolarZenith",
    label="Mt. Zermatt (46.0207$^\circ$N)",
    markers=True,
    marker="o"
)
sns.lineplot(
    data=df_everest,
    x="datetime",
    y="SolarZenith",
    label="Mt. Everest (27.9881$^\circ$N)",
    markers=True,
    marker="o"
)
plt.axvline(x=pd.to_datetime("2020-02-27"), linestyle="--", color="k") # Terra
# plt.axvline(x=pd.to_datetime("2021-03-18"), linestyle="--", color="k") # Aqua
ax.set(
    xlabel="",
    ylabel="Solar Zenith Angle ($^\circ$)"
);
plt.xlim(pd.to_datetime("2000-01-01"), pd.to_datetime("2022-12-31"))

fig.savefig("print/solar_zenith_angle_terra.png", dpi=300, bbox_inches="tight")
fig.savefig("print/solar_zenith_angle_terra.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/solar_zenith_angle_aqua.png", dpi=300, bbox_inches="tight")
# fig.savefig("print/solar_zenith_angle_aqua.pdf", dpi=300, bbox_inches="tight")
# %%

# df = pd.read_csv("sza_Arctic_Circle_Terra.csv")
# df["datetime"] = pd.to_datetime(df.datetime)
# df["biasSZA"] =  df.SolarZenith - df.SolarZenith.mean()

# sns.lineplot(
#     data=df,
#     x="datetime",
#     y="biasSZA"
# )
# %%
