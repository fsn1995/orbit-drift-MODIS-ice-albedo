# %% 
import geemap
import ee
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# import numpy as np

sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
# %%
Map = geemap.Map()
Map

# %%
"""
Extract the time series of view time along different latitudes
"""
date_start = "2000-01-01"
date_end   = "2022-12-31"
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

dataset = ee.ImageCollection('MODIS/061/MOD11A1').select("Day_view_time") 

#%% get the view time
def get_view_time_transect(img_col, scale, transect):
    """
    This is to extract view time along the transect.
    img_col: the image collection
    scale: in meters
    transect: vector defined by ee.LineString
    """
    colFilter = ee.Filter.And(
        ee.Filter.geometry(transect), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
        ee.Filter.date(date_start, date_end),
        # ee.Filter.dayOfYear(173, 173) # June 22 near summer solstice
    )    
    img_col = img_col.filter(colFilter).toBands()
    extractTransect = img_col.reduceRegion(**{
        'reducer': ee.Reducer.mean(),
        'geometry': transect,
        'scale': scale,
        'tileScale': 6
    })
    view_time = pd.Series(extractTransect.getInfo()).to_frame('ViewTime')
    view_time["ViewTime"] = view_time.ViewTime / 10
    view_time["timestamp"] = view_time.index.str[:10]
    view_time["datetime"] = pd.to_datetime(view_time["timestamp"].replace('_', '-', regex=True))

    return view_time

# %%

df_arctic_circle = get_view_time_transect(
    img_col=dataset,
    scale=500,
    transect=arctic_circle_transect
)
df_everest = get_view_time_transect(
    img_col=dataset,
    scale=500,
    transect=everest_transect
)
df_zermatt = get_view_time_transect(
    img_col=dataset,
    scale=500,
    transect=zermatt_transect
)

# %%
fig, ax = plt.subplots(figsize=(12,5))
plt.axvline(x=pd.to_datetime("2020-02-27"), linestyle="--", color="k") # Terra
plt.axvline(x=pd.to_datetime("2002-07-01"), linestyle="--", color="k") # Terra
# plt.axvline(x=pd.to_datetime("2021-03-18"), linestyle="--", color="k") # Aqua

sns.lineplot(
    data=df_arctic_circle.resample('M', on='datetime').mean(),
    x="datetime",
    y="ViewTime",
    label="Arctic Circle (66.5$^\circ$N)",
)
sns.lineplot(
    data=df_zermatt.resample('M', on='datetime').mean(),
    x="datetime",
    y="ViewTime",
    label="Mt. Zermatt (46.0207$^\circ$N)",
)
sns.lineplot(
    data=df_everest.resample('M', on='datetime').mean(),
    x="datetime",
    y="ViewTime",
    label="Mt. Everest (27.9881$^\circ$N)",
)
ax.set(
    xlabel="",
    ylabel="Local Solar Time"
);
sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, 1.5))
plt.xlim(pd.to_datetime("2000-02-24"), pd.to_datetime("2022-12-31"));
# plt.ylim(10.4, 12.4)
plt.yticks([10.5, 11.0, 11.5, 12.0], ['10:30', '11:00', '11:30', '12:00']);  # Set text labels.
# plt.yticks([12.25, 12.5, 12.75, 13.0, 13.25], ['12:15', '12:30', '12:45', '13:00', '13:15']);  # Set text labels.

fig.savefig("print/view_time_daily_terra.png", dpi=300, bbox_inches="tight")
fig.savefig("print/view_time_daily_terra.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/view_time_daily_aqua.png", dpi=300, bbox_inches="tight")
# fig.savefig("print/view_time_daily_aqua.pdf", dpi=300, bbox_inches="tight")


# %%