
sc = satelliteScenario;

sat = satellite(sc, "sat000025994tle.txt");

leadTime = 2*24*3600;                                          % seconds
trailTime = leadTime;
gt = groundTrack(sat,"LeadTime",leadTime,"TrailTime",trailTime)

satelliteScenarioViewer(sc, "Dimension","2D")