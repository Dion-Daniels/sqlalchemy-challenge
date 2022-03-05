#import libraries
from flask import Flask, jsonify
import pandas as pd
import datetime as dt
from datetime import date
from dateutil.relativedelta import relativedelta
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#create engine and classes
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
inspector = inspect(engine)
inspector.get_table_names()
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


#create variables for most recent recording date, date 12 months prior, and station with most recordings
latest_recording = (session.query(Measurement.date).order_by(Measurement.date.desc()).first()).date
last_12m_iso = date.fromisoformat(latest_recording)- relativedelta(years=1)
last_12m = date.isoformat(last_12m_iso)

top_station = (session.query(func.count(Measurement.date),Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.date).desc()).first()).station



#################################################
# Flask Setup
#################################################
# @TODO: Initialize your Flask app here
# YOUR CODE GOES HERE
app = Flask(__name__)
#################################################
# Flask Routes
#################################################

#Home page with route ids
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return(f"Hello and welcome to my Sqlalchemy challenge<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/start date yyyy-mm-dd format<br/>"
    f"/api/v1.0/start date yyyy-mm-dd format/end date yyyy-mm-dd format<br/>"
    ) 


# page for last 12 months of percipitation data
@app.route('/api/v1.0/precipitation')
def precipitation():
    stmt = session.query(Measurement.date,Measurement.prcp).\
    filter(Measurement.date >=last_12m).\
    order_by(Measurement.date.asc()).statement
    df2 = pd.read_sql_query(stmt, session.bind).dropna()
    trial = {k: g["prcp"].tolist() for k,g in df2.groupby("date")}
    return jsonify(trial)


# list of all stations
@app.route('/api/v1.0/stations')
def stations():
    station_df = pd.read_sql_query(session.query(Station.station).statement, session.bind)
    return jsonify(station_df.to_dict())


# page for last 12 months of temperature data
@app.route('/api/v1.0/tobs')
def tobs():
    stmt = session.query(Measurement.date,Measurement.tobs).\
    filter((Measurement.date >=last_12m) & (Measurement.station == top_station)).\
    order_by(Measurement.date.asc()).statement
    df3 = pd.read_sql_query(stmt, session.bind).set_index('date').dropna()
    df3_trial = {k: g["tobs"].tolist() for k,g in df3.groupby("date")}
    return jsonify(df3_trial)


# page for min, max,and average temperature from a given date
@app.route('/api/v1.0/<start>')
def test(start):


    stmt = session.query(func.min(Measurement.tobs).label('Min'),
            func.max(Measurement.tobs).label('Max'),
            func.avg(Measurement.tobs).label('Average')).\
            filter(Measurement.date >=start).statement
    df3 = pd.read_sql_query(stmt, session.bind).dropna()
    return jsonify(df3.to_dict())



# page for min, max,and average temperature within a given date range
@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    
    stmt = session.query(func.min(Measurement.tobs).label('Min'),
            func.max(Measurement.tobs).label('Max'),
            func.avg(Measurement.tobs).label('Average')).\
            filter((Measurement.date >=start)&(Measurement.date <=end)).statement
    df3 = pd.read_sql_query(stmt, session.bind).dropna()
    return jsonify(df3.to_dict())

if __name__ == "__main__":
    app.run(debug=True)
