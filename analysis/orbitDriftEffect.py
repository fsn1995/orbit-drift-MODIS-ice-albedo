'''
Description: This script is used to generate figures for the manuscript.
More details can be found in the manuscript.


Created on Wed Aug 25 2021
Author: Shunan Feng (shunan.feng@envs.au.dk)

'''
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
dfaws = pd.read_csv("promiceAlbedo.csv").rename(columns={
    "albedo": "PROMICE"
})
dfaws = dfaws[dfaws.aws == "egp"]
dfaws["time"] = pd.to_datetime(dfaws.time)
# dfaws["Year"] = dfaws.time.dt.year
# dfaws["Month"] = dfaws.time.dt.month
# dfaws["Day"] = dfaws.time.dt.day
# dfaws = dfaws.groupby(['Year', 'Month', 'Day']).mean() 
# dfaws.reset_index(inplace=True)
# dfaws["time"] = pd.to_datetime({'year': dfaws.Year, 
#                                 'month': dfaws.Month, 
#                                 'day': dfaws.Day}).dt.date
# dfaws["time"] = pd.to_datetime(dfaws.time)

dfmod = pd.read_csv(r"modis\egp.csv")
dfmod["time"] = pd.to_datetime(dfmod["datetime"])
dfmod["MOD"] = dfmod["Snow_Albedo_Daily_Tile"] / 100


#%% MOD and PROMICE
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

# %%
