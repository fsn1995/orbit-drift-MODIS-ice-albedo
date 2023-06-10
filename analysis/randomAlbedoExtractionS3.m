%% Random sampling of S3 albedo

imfolder = "H:\AU\orbit\s3albedo";
imfiles = dir(imfolder);
poicoordinate = readtable("C:\Users\au686295\Documents\GitHub\PhD\orbit-drift-MODIS-ice-albedo\shp\poicoord.csv");
lat = poicoordinate.lat;
lon = poicoordinate.lon;

for i = 3:length(imfiles)
    s3albedo = geotiffinterp(fullfile(imfiles(i).folder, imfiles(i).name, ...
        "BBA_combination.tif"), lat, lon);
    imdate = repmat(datetime(imfiles(i).name), length(s3albedo), 1);
    fprintf("processing %s \n", imdate(1));
    df = table(s3albedo, lat, lon, imdate);
    if i == 3
        writetable(df, "H:\AU\orbit\pois3albedo.csv", "WriteVariableNames", true, "WriteMode", 'overwrite');
    else
        writetable(df, "H:\AU\orbit\pois3albedo.csv", "WriteVariableNames", false, "WriteMode", 'append');
    end
end

%% Extract at UPE_L

df = readtable("H:\AU\orbit\UPE_L.csv");
index = df.year>2018;
df = df(index, :);
geoscatter(df.gps_lat, df.gps_lon);
lat = mean(df.gps_lat);
lon = mean(df.gps_lon);

for i = 3:length(imfiles)
    s3albedo = geotiffinterp(fullfile(imfiles(i).folder, imfiles(i).name, ...
        "BBA_combination.tif"), lat, lon);
    imdate = repmat(datetime(imfiles(i).name), length(s3albedo), 1);
    fprintf("processing %s \n", imdate(1));
    df = table(s3albedo, lat, lon, imdate);
    if i == 3
        writetable(df, "H:\AU\orbit\UPE_Ls3albedo.csv", "WriteVariableNames", true, "WriteMode", 'overwrite');
    else
        writetable(df, "H:\AU\orbit\UPE_Ls3albedo.csv", "WriteVariableNames", false, "WriteMode", 'append');
    end
end
