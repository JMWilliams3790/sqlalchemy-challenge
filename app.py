import numpy as np
import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurements = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

# Precipitation Dicts
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dict of all precip measurements"""
    # Query all dates and measurements
    results = session.query(Measurements.date, Measurements.prcp).all()

    session.close()

    # Convert into list
    prcpList = []
    for date, prcp in results:
        prcpDict = {}
        prcpDict[date] = prcp
        prcpList.append(prcpDict)

    return jsonify(prcpList)



# List stations
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Stations.name).all()

    session.close()

    # Add to list
    stationList = []
    for station in results:
        stationList.append(station)

    return jsonify(stationList)


# Temperature Dicts
@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    StationActivity = session.query(Measurements.station, Stations.name, func.count(Measurements.station)).\
    filter(Stations.station == Measurements.station).group_by(Measurements.station).\
    order_by(func.count(Measurements.station).desc())

    station, name, count = StationActivity.first()
    print(f"{station} {name} {count}")

    maxQuery, yearAgo = session.query(func.max(Measurements.date),func.date(func.max(Measurements.date), "-12 months")).filter(Measurements.station == station).first()
    print(maxQuery, yearAgo)
    """Return a dict of temps"""
    # Query all dates and measurements
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.station == station).\
            filter(Measurements.date >= yearAgo, Measurements.date <= maxQuery).\
            order_by(Measurements.date)

    session.close()

    # Convert into list
    tempList = []
    for date, temp in results:
        tempDict = {}
        tempDict[date] = temp
        tempList.append(tempDict)

    return jsonify(tempList)


@app.route("/api/v1.0/<start>")
def startdate(start):
    """Fetch from the specified start date"""
    session = Session(engine)
    
    # This is some data cleaning for better matching

    results = session.query(Measurements.date, func.max(Measurements.tobs),\
                      func.min(Measurements.tobs),func.avg(Measurements.tobs)).\
                        filter(Measurements.date >= start).group_by(Measurements.date).order_by(Measurements.date).all()
    
    tempList = []
    for date, tmax, tmin, tavg in results:
        tempDict = {}
        tempDict["date"] = date
        tempDict["tmax"] = tmax
        tempDict["tmin"] = tmin
        tempDict["tavg"] = tavg
        tempList.append(tempDict)


    return jsonify(tempList)


if __name__ == '__main__':
    app.run(debug=True)
