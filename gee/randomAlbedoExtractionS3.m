%% Random sampling of S3 albedo

imfolder = "H:\AU\orbit\dataverse_files";
imfiles = dir(imfolder+ '\*.tif');
poicoordinate = readtable("C:\Users\au686295\Documents\GitHub\PhD\orbit-drift-MODIS-ice-albedo\shp\poicoord.csv");
lat = poicoordinate.lat;
lon = poicoordinate.lon;

for i = 1:length(imfiles)
    s3albedo = geotiffinterp(fullfile(imfiles(i).folder, imfiles(i).name),...
        lat, lon);
    imdate = repmat(datetime(erase(imfiles(i).name, ".tif")), length(s3albedo), 1);
    fprintf("processing %s \n", imdate(1));
    df = table(s3albedo, lat, lon, imdate);
    if i == 1
        writetable(df, "H:\AU\orbit\pois3albedo.csv", "WriteVariableNames", true, "WriteMode", 'overwrite');
    else
        writetable(df, "H:\AU\orbit\pois3albedo.csv", "WriteVariableNames", false, "WriteMode", 'append');
    end
end
