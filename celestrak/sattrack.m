%%
startTime = datetime(2002,3,1);
stopTIme  = datetime(2022,9,30);
timeline = startTime:seconds(60):stopTIme;
[y, m, d] = ymd(timeline);
%%
sc = satelliteScenario(startTime, stopTIme, 60);

sat = satellite(sc, "sat000025994tle.txt");

% leadTime = 2*24*3600;                                          % seconds
% trailTime = leadTime;
% gt = groundTrack(sat,"LeadTime",leadTime,"TrailTime",trailTime)

% satelliteScenarioViewer(sc)

position = states(sat,"CoordinateFrame","geographic");
lat = position(1,:);
lon = position(2,:);
alt = position(3,:);
% df = table(timeline, lat, lon, alt, y, m, d);
%%
summerSolstice = datetime(2002, 6, 22):years(1):datetime(2022, 6, 22);


for i=1:length(summerSolstice)
    indexTIme = summerSolstice(i);
    [yi, mi, di] = ymd(indexTIme);
    index = y==yi & m ==mi & d == di;
    figure;
    geoscatter(lat(index), lon(index));
    title(string(indexTIme));
end

%%
% figure;
% for i=1:length(summerSolstice)
%     indexTIme = summerSolstice(i);
%     [yi, mi, di] = ymd(indexTIme);
%     index = y==yi & m ==mi & d == di;
%     geoplot(lat(index), lon(index), DisplayName=string(yi*10000+ mi*100+ di));
%     hold on
% end
% geolimits([60 75],[-90 0])
% %%
% yi = 2003;
% mi = 6;
% di = 22;
% 
% index = y==yi & m ==mi & d == di;
% geoplot(lat(index), lon(index), DisplayName=string(yi*10000+ mi*100+ di));
% geolimits([60 75],[-90 0])