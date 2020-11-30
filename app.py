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

    """Return a dict of temps"""
    # Query all dates and measurements
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.station == "USC00519281").\
            filter(Measurements.date >= '2016-08-18', Measurements.date <= '2017-08-18').\
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

    # This is some data cleaning for better matching
    query_date = func.strftime(start.replace(" "," "))
    for date in start:
        search_term = start.replace(" ", " ")

        if search_term == query_date:
            search_term = query_date["start"].replace(" ", " ")


            return jsonify(session.query(Measurements.station, Stations.name, func.max(Measurements.tobs),\
                      func.min(Measurements.tobs),func.avg(Measurements.tobs)).\
                        filter(Measurements.date >= query_date).group_by(Measurements.station).all())

    return jsonify({"error": f"Date {start} not found."}), 404


if __name__ == '__main__':
    app.run(debug=True)
