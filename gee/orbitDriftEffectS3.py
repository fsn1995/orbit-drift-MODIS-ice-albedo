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
'''S3'''
dfs3 = pd.read_csv("/data/shunan/data/orbit/pois3albedo.csv")
dfs3["date"] = pd.to_datetime(dfs3.imdate)
dfs3 = dfs3[(dfs3.s3albedo>0) & (dfs3.s3albedo<1)]


#%%
df = pd.merge(left=dfmod, right=dfs3, 
              on=["lat", "lon", "date"]).dropna() #on=["lat", "lon", "date"]).dropna()
df = df[np.abs( (df.albedoMOD - df.s3albedo) / (df.albedoMOD + df.s3albedo) ) < 0.5]
df = vx.from_pandas(df)


#%% orbit drift impact
'''
orbit drift impact estimated from HSA
'''
years = np.arange(2017, 2021)
for y in years:
    df_filtered = df[df.year==y]
    df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.s3albedo
    print('Year: %d, diff mean=%.4f, diff median=%.4f, RMSE=%.4f' % (
        y, np.mean(df_filtered["diff"].values), 
        np.median(df_filtered["diff"].values),
        mean_squared_error(df_filtered.albedoMOD.values, df_filtered.s3albedo.values, squared=False)
    ))

# df_filtered = df[(df.year>2016) &  (df.year<2020)]
# df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.s3albedo
# print('Year: %s, diff mean=%.4f, diff median=%.4f, RMSE=%.4f' % (
#     "2017-2019", np.mean(df_filtered["diff"].values), 
#     np.median(df_filtered["diff"].values),
#     mean_squared_error(df_filtered.albedoMOD.values, df_filtered.s3albedo.values, squared=False)
# ))


# %%
