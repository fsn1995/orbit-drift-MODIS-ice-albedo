%% load data
opts = detectImportOptions("H:\AU\orbit\modmydmerge.csv");
opts.SelectedVariableNames = ["albedoMOD", "year", "albedoMYD"];
df = readtable("H:\AU\orbit\modmydmerge.csv", opts);

%% group statistics
dfmean = groupsummary(df, "year","mean");
% dfstd  = groupsummary(df, "year", "std");
rf = rowfilter(dfmean);


f1 = figure;
f1.Position = [ 413.0000  266.6000  703.2000  375.2000];
dfmod = dfmean(rf.year < 2021, ["mean_albedoMOD", "year"]);
mdlmod = fitlm(dfmod.year, dfmod.mean_albedoMOD);
disp(mdlmod);
h1 = plot(mdlmod);
hold on
delete([h1(1), h1(3), h1(4)]);
set(h1(2), "Color", "#D95319", "LineStyle","--", "LineWidth",1.5, ...
    "DisplayName", "2002-2020");

dfmod = dfmean(rf.year < 2020, ["mean_albedoMOD", "year"]);
mdlmod = fitlm(dfmod.year, dfmod.mean_albedoMOD);
disp(mdlmod);
h2 = plot(mdlmod);
delete([h2(1), h2(3), h2(4)]);
set(h2(2), "Color", "#80B3FF", "LineStyle","-.", "LineWidth",1.5, ...
    "DisplayName", "2002-2019");

% dfmyd = dfmean(rf.year < 2021, ["mean_albedoMYD", "year"]);
% mdlmyd = fitlm(dfmyd.year, dfmyd.mean_albedoMYD);
% h3 = plot(mdlmyd);
% delete([h3(1), h3(3), h3(4)]);
% set(h3(2), "Color", "#D95319", "LineStyle","--", "LineWidth",1.5);


h4 = scatter(dfmean, "year", "mean_albedoMOD", ...
    "filled", "DisplayName", "MOD10 (mean)", "MarkerFaceColor","#0072BD");
% scatter(dfmean, "year", "mean_albedoMYD", ...
%     "filled", "DisplayName", "MYD10", "MarkerFaceColor", "#D95319");
grid on
xlim([2001.5 2022.5]);
ylim([0.759 0.85])
xlabel("year");
ylabel("average albedo (JJA)");
title("");
xregion(2019.9, 2022.5);
text(2018, 0.796, "\downarrow -0.0003\cdota^{-1}", "Color","#D95319");
text(2014, 0.785, "\uparrow -0.0004\cdota^{-1}", "Color","#80B3FF");
legend([h1(2) h2(2) h4]);
fontsize(14,"points");
exportgraphics(f1, "print\modtrend.pdf", "Resolution", 300);
exportgraphics(f1, "print\modtrend.png", "Resolution", 300);