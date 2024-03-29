
'''
Description: This script is used to generate figures for the manuscript.
The script is used to compare the MODIS Terra albedo with the HSA albedo.
More details can be found in the manuscript.


Created on Wed Aug 25 2021
Author: Shunan Feng (shunan.feng@envs.au.dk)

'''
#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import vaex as vx
import numpy as np
from scipy import stats
# from pylr2.regress2 import regress2
from sklearn.metrics import mean_squared_error #, r2_score
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
# %%
'''MOD'''
dfmod = pd.read_csv("/data/shunan/data/orbit/poiMOD5km.csv")
coord = dfmod[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
coord = coord.str.rstrip(']}')
coord = coord.str.split(",", expand=True)
dfmod["lat"] = coord[1].astype(float)
dfmod["lon"] = coord[0].astype(float)

dfmod = dfmod.drop(columns=["count", "label", ".geo"]).melt(
    id_vars=["system:index" ,"lat", "lon"], var_name="date", value_name="albedo"
)
dfmod["albedoMOD"] = dfmod.albedo / 100
dfmod["date"] = pd.to_datetime(dfmod.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
dfmod["year"] = dfmod.date.dt.year.astype(float)
dfmod["month"] = dfmod.date.dt.month.astype(float)
dfmod["day"] = dfmod.date.dt.day.astype(float)

'''MYD'''
dfmyd = pd.read_csv("/data/shunan/data/orbit/poiMYD5km.csv")
coord = dfmyd[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
coord = coord.str.rstrip(']}')
coord = coord.str.split(",", expand=True)
dfmyd["lat"] = coord[1].astype(float)
dfmyd["lon"] = coord[0].astype(float)

dfmyd = dfmyd.drop(columns=["count", "label", ".geo"]).melt(
    id_vars=["system:index" ,"lat", "lon"], var_name="date", value_name="albedo"
)
dfmyd["albedoMYD"] = dfmyd.albedo / 100
dfmyd["date"] = pd.to_datetime(dfmyd.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
dfmyd["year"] = dfmyd.date.dt.year.astype(float)
dfmyd["month"] = dfmyd.date.dt.month.astype(float)
dfmyd["day"] = dfmyd.date.dt.day.astype(float)

#%% plot the annual long time series of MOD albedo
df = pd.merge(left=dfmod, right=dfmyd.drop(columns=["year", "month", "day"]), 
              on=["lat", "lon", "date"]).dropna()
df.to_csv("/data/shunan/data/orbit/modmydmerge.csv") # save the merged data             
# df = df[np.abs( (df.albedoMOD - df.albedoMYD) / (df.albedoMOD + df.albedoMYD) ) < 0.5]
#%%
years = np.arange(2002, 2023, dtype=np.double)
modMean = years
modStd = years
mydMean = years
mydStd = years

for i in range(len(years)):
    y=years[i]
    df_filtered = df[df.year==y]
    # modMean[i] = np.mean(df_filtered.albedoMOD)
    # modStd[i] = np.std(df_filtered.albedoMOD)
    # print('Year: %d, mean=%.4f, median=%.4f, RMSE=%.4f, std=%.4f' % (
    #     y, np.mean(df_filtered.albedoMOD),
    #     np.median(df_filtered.albedoMOD),
    #     mean_squared_error(df_filtered.albedoMOD, df_filtered.albedoMYD, squared=False),
    #     np.std(df_filtered.albedoMOD)
    # ))
    mydMean[i] = np.mean(df_filtered.albedoMYD)
    mydStd[i] = np.std(df_filtered.albedoMYD)
    print('Year: %d, mean=%.4f, median=%.4f, RMSE=%.4f, std=%.4f' % (
        y, np.mean(df_filtered.albedoMYD),
        np.median(df_filtered.albedoMYD),
        mean_squared_error(df_filtered.albedoMOD, df_filtered.albedoMYD, squared=False),
        np.std(df_filtered.albedoMYD)
    ))


#%%
''' how many nan values per year?'''
dfclass = pd.read_csv("/data/shunan/data/orbit/poiMODIS5kmclass.csv")
coord = dfclass[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
coord = coord.str.rstrip(']}')
coord = coord.str.split(",", expand=True)
dfclass["lat"] = coord[1].astype(float)
dfclass["lon"] = coord[0].astype(float)

dfclass = dfclass.drop(columns=["count", "label", ".geo"]).melt(
    id_vars=["system:index" ,"lat", "lon"], var_name="date", value_name="classvalue"
).dropna()
dfclass["date"] = pd.to_datetime(dfclass.date.str.strip("_Snow_Albedo_Daily_Tile_Class"), format="%Y_%m_%d")
dfclass["year"] = dfclass.date.dt.year#.astype(float)
dfclass["month"] = dfclass.date.dt.month#.astype(float)
dfclass["day"] = dfclass.date.dt.day#.astype(float)

dfclassplot = pd.DataFrame()
dfclassplot["year"] = dfclass.year.unique()
for i in dfclass.classvalue.unique():
    dfpass = dfclass[dfclass.classvalue == i]
    countYear = dfclass.groupby("year").count().reset_index(drop=False).classvalue
    dfclassplot[str(i)] = dfpass.groupby("year").count().reset_index(drop=False).classvalue 

dfclassplot = dfclassplot.rename(columns={
    '101.0': 'No decision',
    '111.0': 'Night',
    '125.0': 'Land',
    '137.0': 'Inland water',
    '139.0': 'Ocean',
    '150.0': 'Cloud',
    '250.0': 'Missing',
    '251.0': 'Self-shadowing',
    '254.0': 'Non-production mask'
})

fig, ax = plt.subplots(figsize=(6,4))
dfclassplot.plot(
    kind="bar", stacked=True, x="year", ax=ax
)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1.1))
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
ax.set(xlabel="")
ax.set_xticks(ax.get_xticks()[::5])
ax.tick_params(axis='x', labelrotation = 45)

fig.savefig("print/invalidmod.png", dpi=300, bbox_inches="tight")
fig.savefig("print/invalidmod.pdf", dpi=300, bbox_inches="tight")

#%%
df = pd.merge(left=dfmod, right=dfmyd.drop(columns=["year", "month", "day"]), 
              on=["lat", "lon", "date"]).dropna()
df = df[np.abs( (df.albedoMOD - df.albedoMYD) / (df.albedoMOD + df.albedoMYD) ) < 0.5]
df = vx.from_pandas(df)


#%% orbit drift impact
'''
orbit drift impact estimated from MYD
'''
years = np.arange(2002, 2023)
for y in years:
    df_filtered = df[df.year==y]
    df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.albedoMYD
    print('Year: %d, diff mean=%.4f, diff median=%.4f, RMSE=%.4f, std=%.4f' % (
        y, np.mean(df_filtered["diff"].values), 
        np.median(df_filtered["diff"].values),
        mean_squared_error(df_filtered.albedoMOD.values, df_filtered.albedoMYD.values, squared=False),
        np.std(df_filtered["diff"].values)
    ))


#%%  Orbit drift effect figure
fig, ax = plt.subplots(figsize=(7,3)) #figsize=(8,7)
df_filtered = df[df.year<2020]
df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.albedoMYD
df_filtered.viz.histogram("diff", label="2002-2019", what=vx.stat.count() / len(df_filtered))
df_filtered = df[df.year==2020]
df_filtered["diff"] = df_filtered.albedoMOD - df_filtered.albedoMYD
df_filtered.viz.histogram("diff", label="2020", what=vx.stat.count() / len(df_filtered))
ax.plot([0,0], [0, 0.45], ls='--', label="Median(2002-2019)=0.00", color=(0.2980392156862745, 0.4470588235294118, 0.6901960784313725))
ax.plot([0.01, 0.01], [0, 0.45], ls='--', label="Median(2020)=+0.01",  color=(0.8666666666666667, 0.5176470588235295, 0.3215686274509804))
# use axvline will remove all xticks except (0,0), weird...
# ax.axvline(x="0", ls='--', label="Median(2019)=0", color=(0.2980392156862745, 0.4470588235294118, 0.6901960784313725))
# ax.axvline(x="-0.1", ls='--', label="Median(2020)=-0.01", color=(0.8666666666666667, 0.5176470588235295, 0.3215686274509804))
ax.legend()
ax.set_xlim(-0.5, 0.5)
ax.set_ylim(0, 0.45)
ax.set(xlabel=r"$\Delta \alpha$ (MOD-MYD)", ylabel="frequency")
sns.move_legend(ax, "lower left", bbox_to_anchor=(-0.3, -1.3), ncol=2)
fig.savefig("print/driftEffectMYD.png", dpi=300, bbox_inches="tight")
fig.savefig("print/driftEffectMYD.pdf", dpi=300, bbox_inches="tight")

#%% scatter plot of median/mean albedo

df = pd.merge(left=dfmod, right=dfmyd.drop(columns=["year", "month", "day"]), 
              on=["lat", "lon", "date"]).dropna()
df = df[np.abs( (df.albedoMOD - df.albedoMYD) / (df.albedoMOD + df.albedoMYD) ) < 0.5]
df["MOD corrected"] = df.albedoMOD * 0.9844 + 0.0046
#%%
df_filtered = df.groupby(["date"]).median()


fig, ax = plt.subplots(2,2, sharey='row', figsize=(8,6)) #figsize=(8,7)

sns.scatterplot(ax=ax[0,0], data=df_filtered, x="date", y="albedoMOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[0,0], data=df_filtered, x="date", y="albedoMYD", label="MYD", alpha=0.5)
ax[0,0].set_xlim(pd.to_datetime("2019-05-28"), pd.to_datetime("2019-09-04"))
ax[0,0].set_ylim(0.7, 0.98)
ax[0,0].legend().remove()
ax[0,0].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[0,0].set_xticks(ax[0,0].get_xticks()[::4])
ax[0,0].set(xlabel="", ylabel="albedo (median)")
ax[0,0].annotate("a)", xy=(0.85, 0.1),  xycoords='axes fraction')

sns.scatterplot(ax=ax[0,1], data=df_filtered, x="date", y="albedoMOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[0,1], data=df_filtered, x="date", y="albedoMYD", label="MYD", alpha=0.5)
# sns.scatterplot(ax=ax[0,1], data=df_filtered, x="date", y="MOD corrected", label="MOD corrected", alpha=0.5)
ax[0,1].set_xlim(pd.to_datetime("2020-05-28"), pd.to_datetime("2020-09-04"))
ax[0,1].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[0,1].set_xticks(ax[0,1].get_xticks()[::4])
ax[0,1].set(xlabel="")
ax[0,1].annotate("b)", xy=(0.85, 0.1),  xycoords='axes fraction')
sns.move_legend(ax[0,1], "upper left", bbox_to_anchor=(-0.9, 1.35), ncol=2)
# sns.move_legend(ax[0,1], "upper left", bbox_to_anchor=(-1.65, 1.4), ncol=3)
# fig.savefig("print/modismedian.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/modismedian.png", dpi=300, bbox_inches="tight")

df_filtered = df.groupby(["date"]).mean()

# fig, ax = plt.subplots(1,2, sharey='row', figsize=(6,2)) #figsize=(8,7)

sns.scatterplot(ax=ax[1,0], data=df_filtered, x="date", y="albedoMOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[1,0], data=df_filtered, x="date", y="albedoMYD", label="MYD", alpha=0.5)
ax[1,0].set_xlim(pd.to_datetime("2019-05-28"), pd.to_datetime("2019-09-04"))
ax[1,0].set_ylim(0.65, 0.95)
ax[1,0].legend().remove()
ax[1,0].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[1,0].set_xticks(ax[1,0].get_xticks()[::4])
ax[1,0].set(xlabel="2019", ylabel="albedo (mean)")
ax[1,0].annotate("c)", xy=(0.85, 0.1),  xycoords='axes fraction')

sns.scatterplot(ax=ax[1,1], data=df_filtered, x="date", y="albedoMOD", label="MOD", alpha=0.5)
sns.scatterplot(ax=ax[1,1], data=df_filtered, x="date", y="albedoMYD", label="MYD", alpha=0.5)
# sns.scatterplot(ax=ax[1,1], data=df_filtered, x="date", y="MOD corrected", label="MOD corrected", alpha=0.5)
ax[1,1].set_xlim(pd.to_datetime("2020-05-28"), pd.to_datetime("2020-09-04"))
ax[1,1].legend().remove()
ax[1,1].xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
ax[1,1].set_xticks(ax[1,1].get_xticks()[::4])
ax[1,1].set(xlabel="2020")
ax[1,1].annotate("d)", xy=(0.85, 0.1),  xycoords='axes fraction')
# sns.move_legend(ax[1,1], "upper left", bbox_to_anchor=(-1.1, 1.5), ncol=2)
# fig.savefig("print/modismean.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/modismean.png", dpi=300, bbox_inches="tight")
fig.savefig("print/modisTimeSeries.pdf", dpi=300, bbox_inches="tight")
fig.savefig("print/modisTimeSeries.png", dpi=300, bbox_inches="tight")
# fig.savefig("print/modisTimeSeriesCorrected.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/modisTimeSeriesCorrected.png", dpi=300, bbox_inches="tight")

#%% pixel to pixel correlation
'''before orbit drift of terra'''
df_filtered = df[df.year<2020]

slope, intercept, r_value, p_value, std_err = stats.linregress(df_filtered.albedoMOD.values, df_filtered.albedoMYD.values)
rma_results = regress2(df_filtered.albedoMOD.values, df_filtered.albedoMYD.values, _method_type_2="reduced major axis")
k = rma_results['slope']
b = rma_results['intercept'] 

fig, ax = plt.subplots(figsize=(8,7))
ax.plot([0,1], [0,1], '--', color = 'white') # reference line
ax.plot(np.array([0,1]), k * np.array([0,1]) + b, color='b') # rma regression
ax.set_aspect('equal', 'box')
ax.set_xlim(0,1)
ax.set_ylim(0,1)
ax.annotate(
    '2002-2019 JJA\nn:%s' % (format(len(df_filtered.albedoMYD.values), ',')), xy=(0.5, 0.15),  
    xycoords='data', horizontalalignment='left', verticalalignment='top'
)
df_filtered.viz.heatmap("albedoMOD", "albedoMYD", what=np.log(vx.stat.count()), show=True,
                        xlabel="MOD albedo", ylabel="MYD albedo")
print('RMA: \ny={0:.4f}x+{1:.4f}\nRMA_r:{2:.2f} \n k std: {3:.4f} \n b std: {4:.4f}'
      .format(k, b, rma_results['r'], rma_results['std_slope'], rma_results['std_intercept']))
print('mean bias is: %.4f' % np.mean(df_filtered.albedoMOD.values - df_filtered.albedoMYD.values))      
print('RMSE is %.4f' % (mean_squared_error(df_filtered.albedoMYD.values, df_filtered.albedoMOD.values, squared=False)))
fig.savefig("print/albedo/modis20022020scatter.png", dpi=300, bbox_inches="tight")


fig, ax = plt.subplots(figsize=(7,3)) #figsize=(8,7)
df_filtered.viz.histogram("albedoMOD", label="MOD")
df_filtered.viz.histogram("albedoMYD", label="MYD")
ax.legend()
ax.set(xlabel = 'Albedo')
ax.set_xlim(0,1)
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
fig.savefig("print/albedo/modis20022020hist.png", dpi=300, bbox_inches="tight")

#%%
'''after orbit drift of terra'''
df_filtered = df[df.year==2020]

slope, intercept, r_value, p_value, std_err = stats.linregress(df_filtered.albedoMOD.values, df_filtered.albedoMYD.values)
rma_results = regress2(df_filtered.albedoMOD.values, df_filtered.albedoMYD.values, _method_type_2="reduced major axis")
k = rma_results['slope']
b = rma_results['intercept'] 

fig, ax = plt.subplots(figsize=(8,7))
ax.plot([0,1], [0,1], '--', color = 'white') # reference line
ax.plot(np.array([0,1]), k * np.array([0,1]) + b, color='b') # rma regression
ax.set_aspect('equal', 'box')
ax.set_xlim(0,1)
ax.set_ylim(0,1)
ax.annotate(
    '2020 JJA\nn:%s' % (format(df_filtered.albedoMYD.count(), ',')), xy=(0.5, 0.15),  
    xycoords='data', horizontalalignment='left', verticalalignment='top'
)
df_filtered.viz.heatmap("albedoMOD", "albedoMYD", what=np.log(vx.stat.count()), show=True,
                        xlabel="MOD albedo", ylabel="MYD albedo")
print('RMA: \ny={0:.4f}x+{1:.4f}\nRMA_r:{2:.2f} \n k std: {3:.4f} \n b std: {4:.4f}'
      .format(k, b, rma_results['r'], rma_results['std_slope'], rma_results['std_intercept']))
print('mean bias is: %.4f' % np.mean(df_filtered.albedoMOD.values - df_filtered.albedoMYD.values))   
print('RMSE is %.4f' % (mean_squared_error(df_filtered.albedoMOD.values, df_filtered.albedoMYD.values, squared=False)))
fig.savefig("print/albedo/modis2020scatter.png", dpi=300, bbox_inches="tight")


fig, ax = plt.subplots(figsize=(7,3)) #figsize=(8,7)
df_filtered.viz.histogram("albedoMOD", label="MOD")
df_filtered.viz.histogram("albedoMYD", label="MYD")
ax.legend()
ax.set(xlabel = 'Albedo')
ax.set_xlim(0,1)
ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
fig.savefig("print/albedo/modis2020hist.png", dpi=300, bbox_inches="tight")




#%%
# '''are MOD2020 statistically different from MYD<2020?'''
# stats.ranksums(df[df.year<2020].albedoMOD.values, 
#                df[df.year==2020].albedoMOD.values, 
#                alternative='less')

# '''are MYD2020 statistically different from MYD<2020?'''
# stats.ranksums(df[df.year<2020].albedoMYD.values, 
#                df[df.year==2020].albedoMYD.values, 
#                alternative='less')


# df = dfmod.albedo.isna().groupby(dfmod.year).sum().reset_index(name='count')
# df["length"] = dfmod.albedo.groupby(dfmod.year).count().reset_index(name='length')["length"]
# df["ratio"] = df["count"] / df["length"] *100
# df["ratiolabel"] = (df["count"] / df["length"] *100).round(1).astype(str) +'%'


# fig, ax = plt.subplots(1,2, figsize=(16,4))

# ax2 = ax[0].twinx()
# ax[0].bar(df.year, df["length"], label="total")
# ax[0].bar(df.year, df["count"], label="invalid")
# ax[0].legend()
# # ax.grid(None)
# ax2.scatter(df.year, df.ratio, color="g", marker="o")
# sns.move_legend(ax[0], "upper center", bbox_to_anchor=(0.50, 1.25), ncol=2)
# # ax.set_xticks(ax.get_xticks()[::5])
# ax[0].set(xlabel="", ylabel="count")
# ax2.set(xlabel="", ylabel="invalid ratio (%)")
# ax2.yaxis.label.set_color('g')
# ax2.tick_params(axis='y', colors='g')
# ax2.grid(None)
# ax[0].tick_params(axis='x', labelrotation = 45)
# ax[0].annotate("a)", xy=(0.05, 0.8),  xycoords='axes fraction')

# dfclassplot.plot(
#     kind="bar", stacked=True, x="year", ax=ax[1]
# )
# sns.move_legend(ax[1], "upper left", bbox_to_anchor=(1, 1.25))
# ax[1].ticklabel_format(axis="y", style="sci", scilimits=(0,0))
# ax[1].set(xlabel="")
# ax[1].set_xticks(ax[1].get_xticks()[::5])
# ax[1].tick_params(axis='x', labelrotation = 45)
# ax[1].annotate("b)", xy=(0.05, 0.8),  xycoords='axes fraction')
# # fig.savefig("print/invalidmod.png", dpi=300, bbox_inches="tight")
# # fig.savefig("print/invalidmod.pdf", dpi=300, bbox_inches="tight")
#%%
# df = pd.read_excel("stat.xlsx", sheet_name="bias")
# fig, ax = plt.subplots(figsize=(6,3)) 
# sns.scatterplot(data=df, x="year", y="MOD-MYD")
# ax.set(xlabel="", ylabel="bias (MOD-MYD)")
# fig.savefig("print/modisBias.pdf", dpi=300, bbox_inches="tight")
# fig.savefig("print/modisBias.png", dpi=300, bbox_inches="tight")
# %%
# fig, ax = plt.subplots(figsize=(8,3))
# ax2 = ax.twinx()
# sns.barplot(ax=ax, data=df, x="year", y="length", color="steelblue", label="total")
# sns.barplot(ax=ax, data=df, x="year", y="count", color="orange", label="invalid")
# ax2.scatter(df.year, df.ratio)
# ax.legend()
# sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, 1.3), ncol=2)
# ax.set_xticks(ax.get_xticks()[::5])
# ax.set(xlabel="", ylabel="count")
# ax.bar_label(ax.containers[-1], labels=df.ratiolabel, label_type='center',
#              rotation=90, fontsize=12)
# # fig.savefig("print/invalidobs.png", dpi=300, bbox_inches="tight")
# # fig.savefig("print/invalidobs.pdf", dpi=300, bbox_inches="tight")

# %%
# %% archived
# ''' how many nan values per year?'''
# df = dfmod.albedo.isna().groupby(dfmod.year).sum().reset_index(name='count')
# df["length"] = dfmod.albedo.groupby(dfmod.year).count().reset_index(name='length')["length"]
# df["ratio"] = df["count"] / df["length"] *100
# df["ratiolabel"] = (df["count"] / df["length"] *100).round(1).astype(str) +'%'


# fig, (ax1, ax2) = plt.subplots(figsize=(6,6), nrows=2, sharex=True)
# # plt.style.use("seaborn-dark")
# ax12 = ax1.twinx()
# ax1.bar(df.year, df["length"], label="total")
# ax1.bar(df.year, df["count"], label="invalid")
# ax1.legend()
# ax12.scatter(df.year, df.ratio, color="r", marker="+")
# sns.move_legend(ax1, "upper center", bbox_to_anchor=(0.55, 1.35), ncol=2)
# ax1.set(xlabel="", ylabel="count")
# ax12.set(xlabel="", ylabel="invalid ratio (%)")
# ax12.yaxis.label.set_color('r')
# ax12.tick_params(axis='y', colors='r')
# ax12.grid(None)
# # fig.savefig("print/invalidobs.png", dpi=300, bbox_inches="tight")
# # fig.savefig("print/invalidobs.pdf", dpi=300, bbox_inches="tight")
# ''' how many nan values per year?'''
# df = dfmyd.albedo.isna().groupby(dfmyd.year).sum().reset_index(name='count')
# df["length"] = dfmyd.albedo.groupby(dfmyd.year).count().reset_index(name='length')["length"]
# df["ratio"] = df["count"] / df["length"] *100
# df["ratiolabel"] = (df["count"] / df["length"] *100).round(1).astype(str) +'%'


# ax22 = ax2.twinx()
# ax2.bar(df.year, df["length"], label="total")
# ax2.bar(df.year, df["count"], label="invalid")
# # ax2.legend()
# # ax.grid(None)
# ax22.scatter(df.year, df.ratio, color="r", marker="+")
# # sns.move_legend(ax2, "upper center", bbox_to_anchor=(0.55, 1.35), ncol=2)
# # ax.set_xticks(ax.get_xticks()[::5])
# ax2.set(xlabel="", ylabel="count")
# ax22.set(xlabel="", ylabel="invalid ratio (%)")
# ax22.yaxis.label.set_color('r')
# ax22.tick_params(axis='y', colors='r')
# ax22.grid(None)
# ax2.ticklabel_format(axis='y', style='scientific', scilimits=(0,0))