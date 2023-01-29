%% load promice aws cloud cover data

urllist = readtable("C:\Users\au686295\Documents\GitHub\PhD\orbit-drift-MODIS-ice-albedo\shp\data_urls.csv","Delimiter",',');

for i = 1:length(urllist.data_name)
    opts = detectImportOptions(string(urllist.data_url(i)));
    opts.SelectedVariableNames = ["Year", "MonthOfYear", "DayOfMonth", ...
        "HourOfDay_UTC_", "CloudCover", "LatitudeGPS_degN_", "LongitudeGPS_degW_"];
    df = readtable(string(urllist.data_url(i)), opts);
    index = (df.CloudCover >-999) & (df.LatitudeGPS_degN_ > -999) & ...
        (df.LongitudeGPS_degW_ > -999) & (df.MonthOfYear > 5) & (df.MonthOfYear < 9);
    df = df(index,:);
    awsname = erase(string(urllist.data_name(i)), "_hour");
    disp(awsname);
    df.aws = repmat(awsname, length(df.Year), 1);
    df.LongitudeGPS_degW_ = df.LongitudeGPS_degW_ .* -1;
    
    [zd,zltr,zone] = timezone(df.LongitudeGPS_degW_);
    df.date = datetime(df.Year, df.MonthOfYear, df.DayOfMonth, df.HourOfDay_UTC_,...
        0, 0, 'TimeZone','UTC') + hours(zd);
    if i == 1
        writetable(df, "promiceCloud.csv", "WriteVariableNames", true, "WriteMode", 'overwrite');
    else
        writetable(df, "promiceCloud.csv", "WriteVariableNames", false, "WriteMode", 'append');
    end
end

%% statistical test and plot

opts = detectImportOptions("promiceCloud.csv");
opts.SelectedVariableNames = ["CloudCover", "aws", "date"];
df = readtable("promiceCloud.csv", opts);
df.hour = hms(df.date);
df.year = ymd(df.date);

[p,h,stats] = ranksum(df.CloudCover(df.hour==11),df.CloudCover(df.hour==12),'alpha',0.01,...
'tail','right')
[p,h,stats] = ranksum(df.CloudCover(df.hour==10),df.CloudCover(df.hour==12),'alpha',0.01,...
'tail','right')
[p,h,stats] = ranksum(df.CloudCover(df.hour==9),df.CloudCover(df.hour==12),'alpha',0.01,...
'tail','right')

f1 = figure;
h = heatmap(df, "hour", "aws", "ColorVariable", "CloudCover", "ColorMethod", "median");
h.Colormap = cmocean('balance');
h.ColorLimits = [0 1];
h.YDisplayLabels = upper({'cen','egp','kan\_l','kan\_m','kan\_u','kpc\_l','kpc\_u','mit','nuk\_k',...
    'nuk\_l','nuk\_n' ,'nuk\_u','qas\_a','qas\_l' ,'qas\_m' ,'qas\_u','sco\_l','sco\_u','tas\_a',...
    'tas\_l','tas\_u','thu\_l','thu\_u','thu\_u2','upe\_l' });
h.YLabel = "AWS";
h.Title = '';
axs = struct(gca); %ignore warning that this should be avoided
cb = axs.Colorbar;
cb.Label.String = "cloud cover";
fontsize(gca,11,"points");
exportgraphics(h,'print/cloudcover.pdf','Resolution',300);
exportgraphics(h,'print/cloudcover.png','Resolution',600);

f2 = figure;
meanCloud = groupsummary(df.CloudCover, df.hour, 'mean');
b = boxchart(df.hour,df.CloudCover, 'Notch', 'on');
hold on
plot(0:23, meanCloud,'-o')
grid on
xlim([-1,24])
xlabel("hour")
ylabel("cloud cover")
set(gca, 'XTick', 0:2:22, 'XTickLabelRotation', 0)
exportgraphics(f2,'print/cloudcoverBox.pdf','Resolution',300);
exportgraphics(f2,'print/cloudcoverBox.png','Resolution',300);
%% UPE_L
% daily
% url = "https://dataverse.geus.dk/api/access/datafile/:persistentId?persistentId=doi:10.22008/FK2/IW73UU/SXYOAP";
% hourly
url = "https://dataverse.geus.dk/api/access/datafile/:persistentId?persistentId=doi:10.22008/FK2/IW73UU/805YZE";
opts = detectImportOptions(url);
opts.SelectedVariableNames = ["time", "albedo", "cc", "gps_lat", "gps_lon"];
df = rmmissing(readtable(url, opts));
[df.year, df.month, df.day] = ymd(datetime(df.time));
index = (df.month > 5) & (df.month < 9);
df = df(index,:);

geoscatter(df.gps_lat, df.gps_lon);
writetable(df, "H:\AU\orbit\UPE_L.csv", "WriteVariableNames", true, "WriteMode", 'overwrite')