#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
# import matplotlib.dates as mdates
# import vaex as vx
# import numpy as np
# from scipy import stats
# from pylr2.regress2 import regress2
# from sklearn.metrics import mean_squared_error #, r2_score
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
#%%  Orbit drift effect figure
df = pd.read_excel("stat.xlsx", sheet_name="dt")
df["dt"] = df.dt.round(2)

fig, ax = plt.subplots(figsize=(7,3)) #figsize=(8,7)
sns.barplot(
    data=df, x="year", y="dt", hue="sensor", ax=ax
)
ax.tick_params(axis='x', labelrotation = 45)
ax.set(xlabel="", ylabel="$d(t)$")
sns.move_legend(ax, "upper left", bbox_to_anchor=(-0.05, 1.3), ncol=3, title=None)
# ax.annotate("a)", xy=(0.05, 0.8),  xycoords='axes fraction')
# sns.move_legend(ax, "upper left", bbox_to_anchor=(0.09, -0.65), ncol=2, title=None)

fig.savefig("print/dt.pdf", dpi=300, bbox_inches="tight")
fig.savefig("print/dt.png", dpi=300, bbox_inches="tight")

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