%% load promice aws cloud cover data

urllist = readtable("C:\Users\au686295\GitHub\PhD\orbit-drift-MODIS-ice-albedo\shp\data_urls_edition4.csv","Delimiter",',');

for i = 1:length(urllist.data_name)
    opts = detectImportOptions(string(urllist.data_url(i)));
    opts = setvartype(opts, {'gps_lat', 'gps_lon'}, 'double');
    opts.SelectedVariableNames = ["time", "cc", "gps_lat", "gps_lon"];
    
    df = rmmissing(readtable(string(urllist.data_url(i)), opts));
    
    awsname = erase(string(urllist.data_name(i)), "_hour");
    disp(awsname);
    df.aws = repmat(awsname, length(df.cc), 1);
    
    if i == 37
        df.gps_lon = df.gps_lon * -1;
    end
%     [zd,zltr,zone] = timezone(df.gps_lon);
%     df.time = datetime(df.time, 'TimeZone','UTC') - hours(zd);
    df.time = datetime(df.time, 'TimeZone','UTC') + hours(df.gps_lon/15);

    if i == 1
        writetable(df, "promiceCloud4localSolarTime.csv", "WriteVariableNames", true, "WriteMode", 'overwrite');
    else
        writetable(df, "promiceCloud4localSolarTime.csv", "WriteVariableNames", false, "WriteMode", 'append');
    end
end

%% statistical test and plot

opts = detectImportOptions("promiceCloud4localSolarTime.csv");
opts.SelectedVariableNames = ["time", "cc", "gps_lat", "gps_lon", "aws"];
df = readtable("promiceCloud4.csv", opts);
% disp(df.Properties.VariableNames)
df(df.aws=="weg_b", :) = [];
awslat = groupsummary(df.gps_lat, df.aws, 'mean');
awslon = groupsummary(df.gps_lon, df.aws, 'mean');
aws = upper(unique(df.aws));
dfaws = table(aws, awslat, awslon);
figure;
geoscatter(dfaws, "awslat", "awslon");
writetable(dfaws, "C:\Users\au686295\GitHub\PhD\orbit-drift-MODIS-ice-albedo\shp\AWS_station_locationsV4.csv", ...
    "WriteVariableNames", true, "WriteMode", 'overwrite');

df.hour = hms(df.time);
[df.year, df.month, df.day] = ymd(df.time);
index = df.month > 5 & df.month <9;
df = df(index,:);

% paired non-parametric Wilcoxon signed rank test
df11 = df(df.hour==11,:);
df12 = df(df.hour==12,:);

dftest = innerjoin(df11, df12, 'Keys', {'year','month', 'day'});
[p,h,stats] = signrank(dftest.cc_df11, dftest.cc_df12,'alpha',0.05,...
    'tail','right')

figure;
errorbar(tbl.Mean, unique(df.hour), tbl.("Standard Error"), "horizontal", "LineWidth",1.5);
grid on
set(gca, 'YTick', 0:2:22, 'YDir','reverse');
ylim([-0.5 23.5]);
xlabel("Cloud Cover (mean)");
ylabel("Local Solar Time (h)");
% 
% [p,t,stats] = kruskalwallis(df.cc, df.hour);
% figure
% [c,m,h,gnames] = multcompare(stats);
% tbl = array2table(m,"RowNames",gnames, ...
%     "VariableNames",["Mean","Standard_Error"])
% figure;
% errorbar(unique(df.hour), tbl.Mean, tbl.Standard_Error)

% one-way anova test, but note that cc data are not normally distributed 
% [p,tbl,stats] = anova1(df.cc, df.hour);
% figure;
% [c,m,h,gnames] = multcompare(stats);
% tbl = array2table(m,"RowNames",gnames, ...
%     "VariableNames",["Mean","Standard Error"])
% 
% tbl = array2table(c,"VariableNames", ...
%     ["Group","Control Group","Lower Limit","Difference","Upper Limit","P-value"]);
% tbl.("Group") = gnames(tbl.("Group"));
% tbl.("Control Group") = gnames(tbl.("Control Group"));

% not paired, non-parametric test
[p,h,stats] = ranksum(df.cc(df.hour==11),df.cc(df.hour==12),'alpha',0.05,...
'tail','right')
[p,h,stats] = ranksum(df.cc(df.hour==10),df.cc(df.hour==12),'alpha',0.05,...
'tail','right')
[p,h,stats] = ranksum(df.cc(df.hour==9),df.cc(df.hour==12),'alpha',0.05,...
'tail','right')

%% cloud cover plot
f1 = figure;
f1.Position = [521.8000  109.8000  811.2000  422.4000];
h = heatmap(df, "aws", "hour", "ColorVariable", "cc", "ColorMethod", "median");
h.Colormap = cmocean('balance');
h.ColorLimits = [0 1];
h.XDisplayLabels = upper(insertBefore(aws, "_", "\"));
h.XLabel = "AWS";
h.Title = '';
axs = struct(gca); %ignore warning that this should be avoided
cb = axs.Colorbar;
cb.Label.String = "cloud cover";
fontsize(gca,12,"points");
cb.FontSize=12;
sortx(h);
exportgraphics(h,'print/cc.pdf','Resolution',300);
exportgraphics(h,'print/cc.png','Resolution',300);

f2 = figure;
meanCloud = groupsummary(df.cc, df.hour, 'mean');
b = boxchart(df.hour,df.cc, 'Notch', 'on');
hold on
plot(0:23, meanCloud,'-o');
hold off
grid on
xlim([-1,24]);
xlabel("hour");
ylabel("cloud cover");
fontsize(gca,13,"points");
set(gca, 'XTick', 0:2:22, 'XTickLabelRotation', 0);
exportgraphics(f2,'print/ccBox.pdf','Resolution',300);
exportgraphics(f2,'print/ccBox.png','Resolution',300);

f3 = figure;
meanCloud = groupsummary(df.cc, df.year, 'mean');
b = boxchart(df.year,df.cc, 'Notch', 'on');
b.BoxMedianLineColor = 'red';
grid on
hold on
plot(unique(df.year),meanCloud, '-o', 'LineWidth',1.5, 'Color',	"#D95319");
hold off
xlim([2006.5,2022.5]);
ylabel("cloud cover");
fontsize(gca,13,"points");
exportgraphics(f3,'print/ccYearlyBox.pdf','Resolution',300);
exportgraphics(f3,'print/ccYearlyBox.png','Resolution',300);

f4=figure;
meanCloud = groupsummary(df.cc, df.hour, 'mean');
stdCloud = groupsummary(df.cc, df.hour, 'std');
numCloud = groupsummary(df.cc, df.hour, "nnz");
steCloud = stdCloud ./ sqrt(numCloud);
errorbar(unique(df.hour), meanCloud,  steCloud, "LineWidth",1.5);
grid on
set(gca, 'XTick', 0:2:22);
xlim([-0.5 23.5]);
ylabel("Cloud Cover (mean)");
xlabel("Local Solar Time (hour)");
fontsize(gca,13,"points");
exportgraphics(f4,'print/ccHourly.pdf','Resolution',300);
exportgraphics(f4,'print/ccHourly.png','Resolution',300);
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

%% load albedo data
urllist = readtable("C:\Users\au686295\GitHub\PhD\orbit-drift-MODIS-ice-albedo\shp\data_urls_edition4daily.csv","Delimiter",',');

for i = 1:length(urllist.data_name)
    opts = detectImportOptions(string(urllist.data_url(i)));
    opts = setvartype(opts, {'gps_lat', 'gps_lon'}, 'double');
    opts.SelectedVariableNames = ["time", "albedo", "cc", "gps_lat", "gps_lon"];
    
    df = rmmissing(readtable(string(urllist.data_url(i)), opts));
    
    awsname = erase(string(urllist.data_name(i)), "_hour");
    disp(awsname);
    df.aws = repmat(awsname, length(df.albedo), 1);
    
%     [zd,zltr,zone] = timezone(df.gps_lon);
%     df.time = datetime(df.time, 'TimeZone','UTC') - hours(zd);
    df.time = datetime(df.time, 'TimeZone','UTC');
    [df.year, df.month, df.day] = ymd(datetime(df.time));
    index = (df.month > 5) & (df.month < 9);
    df = df(index,:);

    if i == 1
        writetable(df, "promiceAlbedo.csv", "WriteVariableNames", true, "WriteMode", 'overwrite');
    else
        writetable(df, "promiceAlbedo.csv", "WriteVariableNames", false, "WriteMode", 'append');
    end
end