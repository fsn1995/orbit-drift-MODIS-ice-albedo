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


# %% get the solar zenith angle profile

def get_view_time_transect(img_col, scale, transect):
    """
    This is to extract solar zenith angle along the transect.
    img_col: the image collection
    scale: in meters
    transect: vector defined by ee.LineString
    """
    colFilter = ee.Filter.And(
        ee.Filter.geometry(transect), # filterbounds not available on python api https://github.com/google/earthengine-api/issues/83
        ee.Filter.date(date_start, date_end),
        ee.Filter.dayOfYear(173, 173) # June 22 near summer solstice
    )    
    img_col = img_col.filter(colFilter)

    col_size = img_col.size().getInfo()
    view_time = np.ones((col_size, 1))
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
        view_time[i] = pd.DataFrame(extractTransect.getInfo()).mean()
        img_time[i] = img.get('system:time_start').getInfo()
        df = pd.DataFrame(data=np.column_stack([img_time, view_time / 10]), columns=['timestamp', 'ViewTime'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

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

# df_arctic_circle.to_csv("sza_Arctic_Circle_Terra.csv", mode="w")
# df_arctic_circle.to_csv("sza_Arctic_Circle_Aqua.csv", mode="w")

# %%
fig, ax = plt.subplots(figsize=(8,5))
plt.axvline(x=pd.to_datetime("2020-02-27"), linestyle="--", color="k") # Terra
plt.axvline(x=pd.to_datetime("2002-07-01"), linestyle="--", color="k") # Terra
# plt.axvline(x=pd.to_datetime("2021-03-18"), linestyle="--", color="k") # Aqua

sns.lineplot(
    data=df_arctic_circle[df_arctic_circle.datetime > pd.to_datetime("2002-01-01")],
    x="datetime",
    y="ViewTime",
    label="Arctic Circle (66.5$^\circ$N)",
    markers=True,
    marker="o"
)
sns.scatterplot(data=df_arctic_circle, x="datetime",  y="ViewTime")
sns.lineplot(
    data=df_zermatt[df_zermatt.datetime > pd.to_datetime("2002-01-01")],
    x="datetime",
    y="ViewTime",
    label="Mt. Zermatt (46.0207$^\circ$N)",
    markers=True,
    marker="o"
)
sns.scatterplot(data=df_zermatt, x="datetime", y="ViewTime")
sns.lineplot(
    data=df_everest[df_everest.datetime > pd.to_datetime("2002-01-01")],
    x="datetime",
    y="ViewTime",
    label="Mt. Everest (27.9881$^\circ$N)",
    markers=True,
    marker="o"
)
sns.scatterplot(data=df_everest, x="datetime", y="ViewTime")
ax.set(
    xlabel="",
    ylabel="Local Solar Time"
);
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 0.75))
plt.xlim(pd.to_datetime("2000-01-01"), pd.to_datetime("2022-12-31"));
plt.yticks([11.0, 11.5, 12.0], ['11:00', '11:30', '12:00']);  # Set text labels.

fig.savefig("print/view_time_terra.png", dpi=300, bbox_inches="tight")
fig.savefig("print/view_time_terra.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/view_time_aqua.png", dpi=300, bbox_inches="tight")
# fig.savefig("print/view_time_aqua.pdf", dpi=300, bbox_inches="tight")
# %%

test = df_arctic_circle
test["test"] = pd.to_datetime(test.ViewTime* 60 * 60, unit="s").dt.strftime('%H:%M:%S')
# %%
