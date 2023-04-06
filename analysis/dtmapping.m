%% delta a mapping
f = figure;
% f.Position = [1000  610 858 728];
f.Position = [725 764 1252 415];
t = tiledlayout(1,3);

ax1 = nexttile;
[A, x, y, I] = geoimread("H:\AU\orbit\medianDeltamasked.tif");
fprintf("median is %d, std is %d \n", median(A(),"all", "omitnan"), std(A(:), "omitnan"));
[X, Y] = meshgrid(x, y);


greenland()

mapshow(ax1, X, Y, A, DisplayType="surface");
cb = colorbar(ax1);
clim([-0.03, 0.03]);
cmocean('-balance');
scalebarpsn('location','se');
cb.Label.String = 'median\Delta\alpha(2002-2019)';
fontsize(gca,12,"points");
c.Label.FontSize = 12;
text(ax1, min(x)+10, max(y)-300, 'a)', 'FontSize',20);
axis off
%% d(t) mapping
ax2 = nexttile;
[A, x, y, I] = geoimread("H:\AU\orbit\dtmasked.tif");
fprintf("median is %d, std is %d \n", median(A(),"all", "omitnan"), std(A(:), "omitnan"));
[X, Y] = meshgrid(x, y);

greenland()

mapshow(ax2, X, Y, A, DisplayType="surface");
cb = colorbar(ax2);
clim([-0.10, 0.10]);
cmocean('-balance');
scalebarpsn('location','se');
cb.Label.String = 'd(2020)';
fontsize(gca,12,"points");
c.Label.FontSize = 12;
text(ax2, min(x)+10, max(y)-300, 'b)', 'FontSize',20);
axis off
% %% signal to noise ratio
% [imdt, x, y, I] = geoimread("H:\AU\orbit\dtmasked.tif");
% [imDelta, x, y, I] = geoimread("H:\AU\orbit\medianDeltamasked.tif");
% [X, Y] = meshgrid(x, y);
% snr = imDelta ./ imdt;
% 
% ax3 = nexttile;
% greenland()
% mapshow(ax3, X, Y, snr, DisplayType="surface");
% cb = colorbar(ax3);
% clim([-5, 5]);
% cmocean('-balance');
% scalebarpsn('location','se');
% cb.Label.String = 'SNR: median\Delta\alpha(2002-2019)/d(2020)';
% fontsize(gca,12,"points");
% c.Label.FontSize = 12;
% text(ax3, min(x)+10, max(y)-300, 'c)', 'FontSize',20);
%% dt figure
A = imread("print\dt.png");
% A = imresize(A, 0.8);
ax3 = nexttile();
imshow(A);
text(ax3,5, 120, 'c)', 'FontSize',20);
%% export
t.TileSpacing = 'compact';
t.Padding = 'compact';
% exportgraphics(t, 'print/dtall.pdf', 'Resolution',300);