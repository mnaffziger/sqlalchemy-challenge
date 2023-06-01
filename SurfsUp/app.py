# Import the dependencies.
import numpy as np

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

# Code written below was influenced by in-class activities, as well as the solutions for this assignment.  


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../src/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

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
    """List all available api routes."""
    return (
        f"Welcome to the Climate Analysis API for the Honolulu, Hawaii Region"
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/percipitation"
        f"/api/v1.0/tobs"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all weather stations around Honolulu, Hawaii"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into flattened / normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/percipitation")
def percipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of percipitation data including the date, and station from the past year"""
        # Query all observed percipitation records from the previous year
    recent_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
                         filter(Measurement.date >= recent_year).all()

    session.close()

    # Create dictionary with prcp records
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data from the most active reporting station over the previous year"""
    # Query all observed tobs records over the previous year
    recent_year = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    # query most active station
    results = session.query(Measurement.tobs).\
                        filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= recent_year).all()
    session.close()

    # Flatten queried tobs data
    temps_recorded = list(np.ravel(results))

    # Create json
    return jsonify(temps_recorded)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    ### To be honest, I did not have enough time to fully think this one through.
        # Not saying it was too difficult, just that the work/life/balance got in the way of figuring this out myself
        # Credit here towards the solutions and way too many stackoverflow pages

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:

        start = dt.datetime.strptime(start, "%m%d%Y")
        
        # # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        # Flatten results
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == '__main__':
    app.run()
