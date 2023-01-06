#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
import vaex as vx
import numpy as np
# from scipy import stats
# from pylr2.regress2 import regress2
from sklearn.metrics import mean_squared_error #, r2_score
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
# %%
'''MOD'''
dfmod = pd.read_csv("/data/shunan/data/orbit/poiMOD5km.csv")
dfmod["id"] = np.arange(0, len(dfmod))
coord = dfmod[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
coord = coord.str.rstrip(']}')
coord = coord.str.split(",", expand=True)
dfmod["lat"] = coord[1].astype(float).round(13)
dfmod["lon"] = coord[0].astype(float).round(13)

dfmod = dfmod.drop(columns=["count", "label", ".geo"]).melt(
    id_vars=["system:index" ,"lat", "lon", "id"], var_name="date", value_name="albedo"
)
dfmod["albedoMOD"] = dfmod.albedo / 100
dfmod["date"] = pd.to_datetime(dfmod.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
dfmod["year"] = dfmod.date.dt.year.astype(float)
dfmod["month"] = dfmod.date.dt.month.astype(float)
dfmod["day"] = dfmod.date.dt.day.astype(float)
#%%
'''HSA'''
dfhsa = pd.read_csv("/data/shunan/data/orbit/poiHSA500m.csv").rename(
    columns={"longitude": "lon", "latitude": "lat", "visnirAlbedo": "HSA"}
)
dfhsa["date"] = pd.to_datetime(pd.to_datetime(dfhsa.time, unit="ms").dt.date)
dfhsa = dfhsa[(dfhsa.HSA>0) & (dfhsa.HSA<1)]


#%%
df = pd.merge(left=dfmod, right=dfhsa, 
              on=["id", "date"]).dropna() #on=["lat", "lon", "date"]).dropna()
df = df[np.abs( (df.albedoMOD - df.HSA) / (df.albedoMOD + df.HSA) ) < 0.5]
df = vx.from_pandas(df)


#%% orbit drift impact
'''
orbit drift impact estimated from HSA
'''
years = np.arange(2000, 2023)
for y in years:
    df_filtered = df[df.year==y]
    df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.HSA
    # df_filtered.viz.histogram("diff", label=str(y))
    print('Year: %d, diff mean=%.4f, diff median=%.4f, RMSE=%.4f' % (
        y, np.mean(df_filtered["diff"].values), 
        np.median(df_filtered["diff"].values),
        mean_squared_error(df_filtered.albedoMOD.values, df_filtered.HSA.values, squared=False)
    ))

df_filtered = df[(df.year>2001) &  (df.year<2020)]
df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.HSA
print('Year: %s, diff mean=%.4f, diff median=%.4f, RMSE=%.4f' % (
    "2002-2019", np.mean(df_filtered["diff"].values), 
    np.median(df_filtered["diff"].values),
    mean_squared_error(df_filtered.albedoMOD.values, df_filtered.HSA.values, squared=False)
))

#%%  Orbit drift effect figure
df = pd.read_excel("stat.xlsx", sheet_name="dt")

fig, ax = plt.subplots(figsize=(7,3)) #figsize=(8,7)
sns.barplot(
    data=df, x="year", y="dt", hue="sensor"
)
# ax.set_xticks(ax.get_xticks()[::4])
plt.xticks(rotation = 45)
ax.set(xlabel="", ylabel="$d(t)$")
sns.move_legend(ax, "upper left", bbox_to_anchor=(0.1, 1.30), ncol=2, title=None)
fig.savefig("print/dt.pdf", dpi=300, bbox_inches="tight")
fig.savefig("print/dt.png", dpi=300, bbox_inches="tight")
# %%
