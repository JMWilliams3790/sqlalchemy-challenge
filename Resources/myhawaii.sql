--stations table
CREATE TABLE stations (
  station VARCHAR PRIMARY KEY,
  name VARCHAR,
  latitude VARCHAR,
  longitude VARCHAR,
  elevation VARCHAR
);

--measurements table
CREATE TABLE measurements (
  station VARCHAR REFERENCES stations(station),
  date VARCHAR,
  prcp VARCHAR,
  tobs VARCHAR
);

