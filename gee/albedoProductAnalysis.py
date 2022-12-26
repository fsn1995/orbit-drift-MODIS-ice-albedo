#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import vaex as vx
sns.set_theme(style="darkgrid", font="Arial", font_scale=2)
# %%
dfmod = pd.read_csv("/data/shunan/data/orbit/poiMODIS5km.csv")
coord = dfmod[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
coord = coord.str.rstrip(']}')
coord = coord.str.split(",", expand=True)
dfmod["lat"] = coord[1]
dfmod["lon"] = coord[0]

dfmod = dfmod.drop(columns=["count", "label", ".geo"]).melt(
    id_vars=["system:index" ,"lat", "lon"], var_name="date", value_name="albedo"
)
dfmod["albedo"] = dfmod.albedo / 100
dfmod["date"] = pd.to_datetime(dfmod.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
dfmod["year"] = dfmod.date.dt.year
dfmod["month"] = dfmod.date.dt.month
dfmod["day"] = dfmod.date.dt.day

# %%
''' how many nan values per year?'''
df = dfmod.albedo.isna().groupby(dfmod.year).sum().reset_index(name='count')
df["length"] = dfmod.albedo.groupby(dfmod.year).count().reset_index(name='length')["length"]
df["ratio"] = (df["count"] / df["length"] *100).round(1).astype(str) +'%'

fig, ax = plt.subplots(figsize=(8,3))
sns.barplot(ax=ax, data=df, x="year", y="length", color="steelblue", label="total")
sns.barplot(ax=ax, data=df, x="year", y="count", color="orange", label="invalid")
ax.legend()
sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, 1.3), ncol=2)
ax.set_xticks(ax.get_xticks()[::5])
ax.set(xlabel="", ylabel="count")
ax.bar_label(ax.containers[-1], labels=df.ratio, label_type='center',
             rotation=90, fontsize=12)
fig.savefig("print/invalidobs.png", dpi=300, bbox_inches="tight")
fig.savefig("print/invalidobs.pdf", dpi=300, bbox_inches="tight")
# %%

# %%
