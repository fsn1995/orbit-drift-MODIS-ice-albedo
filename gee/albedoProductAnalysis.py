#%% 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import vaex as vx
# %%
dfmod = pd.read_csv("data\poiMODIS5km.csv")
coord = dfmod[".geo"].str.lstrip('[{"type":"Point","coordinates":[')
coord = coord.str.rstrip(']}')
coord = coord.str.split(",", expand=True)
dfmod["lat"] = coord[1]
dfmod["lon"] = coord[0]

dfmod = dfmod.drop(columns=["count", "label", ".geo"]).melt(
    id_vars=["system:index" ,"lat", "lon"], var_name="date", value_name="albedo"
)
dfmod["date"] = pd.to_datetime(dfmod.date.str.strip("_Snow_Albedo_Daily_Tile"), format="%Y_%m_%d")
# %%
