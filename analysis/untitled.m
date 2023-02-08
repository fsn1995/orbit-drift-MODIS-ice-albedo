%%

opts = detectImportOptions("C:\Users\au686295\Downloads\NUK_K_hour_v03 (1).txt");
opts.SelectedVariableNames = ["Year", "MonthOfYear", "DayOfMonth", ...
    "HourOfDay_UTC_", "CloudCover", "LatitudeGPS_degN_", "LongitudeGPS_degW_"];

% aws = 'nuk_k';
% opts = detectImportOptions("promiceCloud.csv");
% opts.SelectedVariableNames = ["CloudCover", "aws", "date"];
% df3 = readtable("promiceCloud.csv", opts);
% df3 = df3(strcmp(df3.aws, aws), :);


df3 = readtable("C:\Users\au686295\Downloads\NUK_K_hour_v03 (1).txt", opts);
index = (df3.CloudCover >-999) & (df3.LatitudeGPS_degN_ > -999) & ...
    (df3.LongitudeGPS_degW_ > -999) & (df3.MonthOfYear > 5) & (df3.MonthOfYear < 9);
df3 = df3(index,:);
df3.time = datetime(df3.Year, df3.MonthOfYear, df3.DayOfMonth, df3.HourOfDay_UTC_, 0,0,0);
%% 
opts = detectImportOptions("C:\Users\au686295\Downloads\NUK_K_hour (1).csv");
% opts = detectImportOptions("C:\Users\au686295\Downloads\NUK_K_hour.csv");
opts.SelectedVariableNames = ["time", "cc", "gps_lat", "gps_lon"];
df4 = rmmissing(readtable("C:\Users\au686295\Downloads\NUK_K_hour (1).csv", opts));


% opts = detectImportOptions("promiceCloud4.csv");
% opts.SelectedVariableNames = ["time", "cc", "gps_lat", "gps_lon", "aws"];
% df4 = readtable("promiceCloud4.csv", opts);
% df4 = df4(strcmp(df4.aws, aws), :);


df4.hour = hms(df4.time);
[df4.year, df4.month] = ymd(df4.time);
index = df4.month > 5 & df4.month <9 & df4.year<2022; 
df4 = df4(index,:);

%%
df = synchronize(table2timetable(df3), table2timetable(df4));
mdl = fitlm(df.cc, df.CloudCover);
figure;
plot(mdl);

figure;
b = boxchart(df.hour,df.CloudCover, 'Notch', 'on');
title('v3')
figure;
b = boxchart(df.hour,df.cc, 'Notch', 'on');
title('v4')
df.ccdiff = df.cc - df.CloudCover;
figure;
b = boxchart(df.hour,df.ccdiff, 'Notch', 'on');
title('v4 - v3')