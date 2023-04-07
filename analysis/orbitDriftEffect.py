#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# import vaex as vx
import numpy as np
from scipy import stats
from sklearn.metrics import mean_squared_error #, r2_score
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
#%%  Orbit drift effect figure
df = pd.read_excel("stat.xlsx", sheet_name="dt")
df["dt"] = df.dt.round(2)

fig, ax = plt.subplots(figsize=(3,7)) #figsize=(8,7)
sns.barplot(
    data=df, x="dt", y="year", hue="sensor", ax=ax
)
# ax.tick_params(axis='x', labelrotation = 45)
ax.set(xlabel="$d(t)$", ylabel="")
sns.move_legend(ax, "upper left", bbox_to_anchor=(-0.6, 1.25), ncol=2, title=None)
# ax.annotate("a)", xy=(0.05, 0.8),  xycoords='axes fraction')
# sns.move_legend(ax, "upper left", bbox_to_anchor=(0.09, -0.65), ncol=2, title=None)

# fig.savefig("print/dt.pdf", dpi=300, bbox_inches="tight")
fig.savefig("print/dt.png", dpi=300, bbox_inches="tight")


#%% UPE_L
dfaws = pd.read_csv("/data/shunan/data/orbit/UPE_Ldaily.csv").rename(columns={
    "albedo": "PROMICE"
})
dfaws["time"] = pd.to_datetime(dfaws.time)

dfmod = pd.read_csv("/data/shunan/data/orbit/UPE_L_MOD.csv")
dfmod["time"] = pd.to_datetime(dfmod["datetime"])
dfmod["MOD"] = dfmod["Snow_Albedo_Daily_Tile"] / 100

dfmyd = pd.read_csv("/data/shunan/data/orbit/UPE_L_MYD.csv")
dfmyd["time"] = pd.to_datetime(dfmyd["datetime"])
dfmyd["MYD"] = dfmyd["Snow_Albedo_Daily_Tile"] / 100

dfhsa = pd.read_csv("/data/shunan/data/orbit/UPE_L_HSA.csv").rename(columns={
    "visnirAlbedo": "HSA"
})
dfhsa["time"] = pd.to_datetime(dfhsa["datetime"]).dt.date
dfhsa = dfhsa.groupby("time").mean().reset_index()
dfhsa["time"] = pd.to_datetime(dfhsa["time"])

dfs3 = pd.read_csv("/data/shunan/data/orbit/UPE_Ls3albedo.csv").rename(columns={
    "s3albedo": "S3"
})
dfs3["time"] = pd.to_datetime(dfs3.imdate)

#%% correlation
df = pd.merge(left=dfmod, right=dfaws, 
              on=["time"]).dropna()
df = df[df.time>pd.to_datetime("2019-01-01")]              
slope, intercept, r_value, p_value, std_err = stats.linregress(df.MOD, df.PROMICE)
print('MOD: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}'.format(slope,intercept,r_value,p_value))


df = pd.merge(left=dfmyd, right=dfaws, 
              on=["time"]).dropna()
df = df[df.time>pd.to_datetime("2019-01-01")]                  
slope, intercept, r_value, p_value, std_err = stats.linregress(df.MYD, df.PROMICE)
print('MYD: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}'.format(slope,intercept,r_value,p_value))

df = pd.merge(left=dfhsa, right=dfaws, 
              on=["time"]).dropna()
df = df[df.time>pd.to_datetime("2019-01-01")]                  
slope, intercept, r_value, p_value, std_err = stats.linregress(df.HSA, df.PROMICE)
print('HSA: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}'.format(slope,intercept,r_value,p_value))

df = pd.merge(left=dfs3, right=dfaws, 
              on=["time"]).dropna()
df = df[df.time>pd.to_datetime("2019-01-01")]                  
slope, intercept, r_value, p_value, std_err = stats.linregress(df.S3, df.PROMICE)
print('S3: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}'.format(slope,intercept,r_value,p_value))

#%% MOD and UPE_L
df = pd.merge(left=dfmod, right=dfaws, on=["time"]).dropna()
df = df[(df.time>pd.to_datetime("2020-01-01")) & (df.time<pd.to_datetime("2020-12-31"))]              
slope, intercept, r_value, p_value, std_err = stats.linregress(df.MOD, df.PROMICE)
rmse = mean_squared_error(df.PROMICE, df.MOD, squared=False)
meandiff = np.mean(df.PROMICE - df.MOD)
print('2020: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}, rmse:{4:.2f}, bias:{4:.2f}'.format(slope,intercept,r_value,p_value, rmse,meandiff))

df = pd.merge(left=dfmod, right=dfaws, on=["time"]).dropna()
df = df[(df.time>pd.to_datetime("2021-01-01")) & (df.time<pd.to_datetime("2021-12-31"))]              
slope, intercept, r_value, p_value, std_err = stats.linregress(df.MOD, df.PROMICE)
rmse = mean_squared_error(df.PROMICE, df.MOD, squared=False)
meandiff = np.mean(df.PROMICE - df.MOD)
print('2021: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}, rmse:{4:.2f}, bias:{4:.2f}'.format(slope,intercept,r_value,p_value, rmse,meandiff))

df = pd.merge(left=dfmod, right=dfaws, on=["time"]).dropna()
df = df[(df.time>pd.to_datetime("2022-01-01")) & (df.time<pd.to_datetime("2022-12-31"))]              
slope, intercept, r_value, p_value, std_err = stats.linregress(df.MOD, df.PROMICE)
rmse = mean_squared_error(df.PROMICE, df.MOD, squared=False)
meandiff = np.mean(df.PROMICE - df.MOD)
print('2022: \ny={0:.4f}x+{1:.4f}\nOLS_r:{2:.2f}, p:{3:.3f}, rmse:{4:.2f}, bias:{4:.2f}'.format(slope,intercept,r_value,p_value, rmse,meandiff))

#%%
# fig, ax = plt.subplots(1,4, sharey='row', figsize=(8,6)) #figsize=(8,7)
fig, ax = plt.subplots(1,4, sharey='row', figsize=(20,4)) #figsize=(8,7)

sns.lineplot(ax=ax[0], data=dfaws, x="time", y="PROMICE", label="PROMICE", color="k")
sns.scatterplot(ax=ax[0], data=dfmod, x="time", y="MOD", label="MOD10", alpha=0.5)
sns.scatterplot(ax=ax[0], data=dfmyd, x="time", y="MYD", label="MYD10", alpha=0.5)
sns.scatterplot(ax=ax[0], data=dfhsa, x="time", y="HSA", label="HSA", alpha=0.5)
sns.scatterplot(ax=ax[0], data=dfs3, x="time", y="S3", label="S3", alpha=0.5, color="purple")
ax[0].set_xlim(pd.to_datetime("2019-06-01"), pd.to_datetime("2019-08-31"))
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[0].set_ylim(0.25, 1)
sns.move_legend(ax[0], "upper left", bbox_to_anchor=(0.65, 1.25), ncol=5)
ax[0].set_xticks(ax[0].get_xticks()[::2])
ax[0].set(xlabel="2019", ylabel="albedo")
ax[0].annotate("a)", xy=(0.85, 0.80),  xycoords='axes fraction')

sns.lineplot(ax=ax[1], data=dfaws, x="time", y="PROMICE", label="PROMICE", color="k")
sns.scatterplot(ax=ax[1], data=dfmod, x="time", y="MOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[1], data=dfmyd, x="time", y="MYD", label="MYD", alpha=0.5)
sns.scatterplot(ax=ax[1], data=dfhsa, x="time", y="HSA", label="HSA", alpha=0.5)
sns.scatterplot(ax=ax[1], data=dfs3, x="time", y="S3", label="S3", alpha=0.5, color="purple")
ax[1].set_xlim(pd.to_datetime("2020-06-01"), pd.to_datetime("2020-08-31"))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[1].set_ylim(0.25, 1)
ax[1].legend().remove()
ax[1].set_xticks(ax[1].get_xticks()[::2])
ax[1].set(xlabel="2020", ylabel="")
ax[1].annotate("b)", xy=(0.85, 0.80),  xycoords='axes fraction')

sns.lineplot(ax=ax[2], data=dfaws, x="time", y="PROMICE", label="PROMICE", color="k")
sns.scatterplot(ax=ax[2], data=dfmod, x="time", y="MOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[2], data=dfmyd, x="time", y="MYD", label="MYD", alpha=0.5)
sns.scatterplot(ax=ax[2], data=dfhsa, x="time", y="HSA", label="HSA", alpha=0.5)
sns.scatterplot(ax=ax[2], data=dfs3, x="time", y="S3", label="S3", alpha=0.5, color="purple")
ax[2].set_xlim(pd.to_datetime("2021-06-01"), pd.to_datetime("2021-08-31"))
ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[0].set_ylim(0.25, 1)
ax[2].legend().remove()

ax[2].set_xticks(ax[2].get_xticks()[::2])
ax[2].set(xlabel="2021", ylabel="")
ax[2].annotate("c)", xy=(0.85, 0.80),  xycoords='axes fraction')

sns.lineplot(ax=ax[3], data=dfaws, x="time", y="PROMICE", label="PROMICE", color="k")
sns.scatterplot(ax=ax[3], data=dfmod, x="time", y="MOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[3], data=dfmyd, x="time", y="MYD", label="MYD", alpha=0.5)
sns.scatterplot(ax=ax[3], data=dfhsa, x="time", y="HSA", label="HSA", alpha=0.5)
sns.scatterplot(ax=ax[3], data=dfs3, x="time", y="S3", label="S3", alpha=0.5, color="purple")
ax[3].set_xlim(pd.to_datetime("2022-06-01"), pd.to_datetime("2022-08-31"))
ax[3].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[0].set_ylim(0.25, 1)
ax[3].legend().remove()

ax[3].set_xticks(ax[3].get_xticks()[::2])
ax[3].set(xlabel="2022", ylabel="")
ax[3].annotate("d)", xy=(0.85, 0.80),  xycoords='axes fraction')

fig.savefig("print/timeSeries.png", dpi=300, bbox_inches="tight")
fig.savefig("print/timeSeries.pdf", dpi=300, bbox_inches="tight")




#%%

# # %%
# '''MOD'''
# dfmod = pd.read_csv("/data/shunan/data/orbit/poiMOD5km.csv")
# dfmod["id"] = np.arange(0, len(dfmod))
# coord = dfmod[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
# coord = coord.str.rstrip(']}')
# coord = coord.str.split(",", expand=True)
# dfmod["lat"] = coord[1].astype(float).round(13)
# dfmod["lon"] = coord[0].astype(float).round(13)

# dfmod = dfmod.drop(columns=["count", "label", ".geo"]).melt(
#     id_vars=["system:index" ,"lat", "lon", "id"], var_name="date", value_name="albedo"
# )
# dfmod["albedoMOD"] = dfmod.albedo / 100
# dfmod["date"] = pd.to_datetime(dfmod.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
# dfmod["year"] = dfmod.date.dt.year.astype(float)
# dfmod["month"] = dfmod.date.dt.month.astype(float)
# dfmod["day"] = dfmod.date.dt.day.astype(float)

# '''MYD'''
# dfmyd = pd.read_csv("/data/shunan/data/orbit/poiMYD5km.csv")
# coord = dfmyd[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
# coord = coord.str.rstrip(']}')
# coord = coord.str.split(",", expand=True)
# dfmyd["lat"] = coord[1].astype(float)
# dfmyd["lon"] = coord[0].astype(float)

# dfmyd = dfmyd.drop(columns=["count", "label", ".geo"]).melt(
#     id_vars=["system:index" ,"lat", "lon"], var_name="date", value_name="albedo"
# )
# dfmyd["albedoMYD"] = dfmyd.albedo / 100
# dfmyd["date"] = pd.to_datetime(dfmyd.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
# dfmyd["year"] = dfmyd.date.dt.year.astype(float)
# dfmyd["month"] = dfmyd.date.dt.month.astype(float)
# dfmyd["day"] = dfmyd.date.dt.day.astype(float)

# #%%  Orbit drift effect figure
# df = pd.read_excel("stat.xlsx", sheet_name="dt")

# fig, ax = plt.subplots(1,2, figsize=(14,4)) #figsize=(8,7)
# sns.barplot(
#     data=df, x="year", y="dt", hue="sensor", ax=ax[0]
# )
# ax[0].tick_params(axis='x', labelrotation = 45)
# ax[0].set(xlabel="", ylabel="$d(t)$")
# ax[0].annotate("a)", xy=(0.05, 0.8),  xycoords='axes fraction')
# sns.move_legend(ax[0], "upper left", bbox_to_anchor=(0.09, -0.65), ncol=2, title=None)

# df = pd.merge(left=dfmod, right=dfmyd.drop(columns=["year", "month", "day"]), 
#               on=["lat", "lon", "date"]).dropna()
# df = df[np.abs( (df.albedoMOD - df.albedoMYD) / (df.albedoMOD + df.albedoMYD) ) < 0.5]
# df = vx.from_pandas(df)

# df_filtered = df[df.year<2020]
# df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.albedoMYD
# df_filtered.viz.histogram("diff", label="2002-2019", what=vx.stat.count() / len(df_filtered))
# df_filtered = df[df.year==2020]
# df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.albedoMYD
# df_filtered.viz.histogram("diff", label="2020", what=vx.stat.count() / len(df_filtered))
# ax[1].plot([0,0], [0, 0.45], ls='--', label="Median(2002-2019)=0.00", color=(0.2980392156862745, 0.4470588235294118, 0.6901960784313725))
# ax[1].plot([0.01, 0.01], [0, 0.45], ls='--', label="Median(2020)=+0.01",  color=(0.8666666666666667, 0.5176470588235295, 0.3215686274509804))
# # use axvline will remove all xticks except (0,0), weird...
# # ax.axvline(x="0", ls='--', label="Median(2019)=0", color=(0.2980392156862745, 0.4470588235294118, 0.6901960784313725))
# # ax.axvline(x="-0.1", ls='--', label="Median(2020)=-0.01", color=(0.8666666666666667, 0.5176470588235295, 0.3215686274509804))
# ax[1].legend()
# ax[1].set_xlim(-0.5, 0.5)
# ax[1].set_ylim(0, 0.40)
# ax[1].set(xlabel=r"$\Delta \alpha$ (MOD-MYD)", ylabel="frequency")
# ax[1].annotate("b)", xy=(0.05, 0.8),  xycoords='axes fraction')
# sns.move_legend(ax[1], "lower left", bbox_to_anchor=(-0.3, -1.2), ncol=2)
# fig.savefig("print/dt.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/dt.png", dpi=300, bbox_inches="tight")
# %%
