%% Mapping the average view time 

%% MOD Predrift
f = figure;
% f.Position = [1000  610 858 728];
f.Position = [725 764 1252 415];
t = tiledlayout(1,3, 'TileSpacing', 'compact', 'Padding', 'compact');

ax1 = nexttile;
[A, x, y, I] = geoimread("H:\AU\orbit\modImgPreDrift.tif");
impreDrift = A./10;
fprintf("min is %.2f, max is %.2f \n", ...
    min(impreDrift(:), [], "omitnan"), max(impreDrift(:), [], "omitnan"));
[X, Y] = meshgrid(x, y);

greenland('k')
mapshow(ax1, X, Y, impreDrift, DisplayType="surface");
cb = colorbar(ax1);
clim([10.5, 16.5]);
cmocean('-solar', 12);
scalebarpsn('location','se');
cb.Label.String = 'Local time (h)';
title(ax1, 'a) MOD 2002-2019', 'FontWeight','normal');
% hold on
% mapshow(ax1, X, Y, impreDrift, 'DisplayType', 'contour',...
%     'LineColor', 'k')
fontsize(ax1,16,"points");
axis off

%% MOD Postdrift
ax2 = nexttile;
[A, x, y, I] = geoimread("H:\AU\orbit\modImgPostDrift.tif");
impostDrift = A./10;
fprintf("min is %.2f, max is %.2f \n", ...
    min(impostDrift(:), [], "omitnan"), max(impostDrift(:), [], "omitnan"));
[X, Y] = meshgrid(x, y);

greenland('k')
mapshow(ax2, X, Y, impostDrift, DisplayType="surface");
cb = colorbar(ax2);
clim([10.5, 16.5]);
cmocean('-solar', 12);
% scalebarpsn('location','se');
cb.Label.String = 'Local time (h)';
title(ax2, 'b) MOD 2022', 'FontWeight','normal');
fontsize(ax2,16,"points");
axis off

%% view time difference

ax3 = nexttile;
A = (impostDrift - impreDrift) .* 60;
% fprintf("min is %.2f, max is %.2f \n", ...
%     min(A(:), [], "omitnan"), max(A(:), [], "omitnan"));

greenland('k')
mapshow(ax3, X, Y, A, DisplayType="surface");
cb = colorbar(ax3);
clim([-30 0]);
cmocean('-matter',12);
% scalebarpsn('location','se');
cb.Label.String = '\Delta min';
title(ax3, 'c) View time difference', 'FontWeight','normal');
% cbarrow("down");
fontsize(ax3,16,"points");
axis off
%% export

exportgraphics(t, 'print/viewtimeMap.pdf', 'Resolution',300);