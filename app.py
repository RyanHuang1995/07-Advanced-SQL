import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
from sqlalchemy.pool import StaticPool
engine = create_engine('sqlite:///Resources/hawaii.sqlite',
                    connect_args={'check_same_thread':False},
                    poolclass=StaticPool)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/previous_year_tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """ Return the precipitation"""
    # Define the date
    query = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date > "2016-08-19",Measurement.date < "2017-08-19").all()
    precipitation = {date:prcp for date,prcp in query}
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    # Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/previous_year_tobs")
def tobs():         
    results = session.query(Measurement.tobs).\
        filter(Measurement.date > '2016-08-19').\
        filter(Measurement.station=="USC00519281").all()
           
    tobs = list(np.ravel(results))
    return jsonify(tobs)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temperature(start=None,end=None):
    Min,Avg,Max = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()[0]
    results = {
    "Max":Max,
    "Avg":Avg,
    "Min":Min}
    return jsonify(results)

           
           

if __name__ == '__main__':
    app.debug = True
    app.run()
