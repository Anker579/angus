from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
import json
from dotenv import load_dotenv
import plotly
import plotly.express as px
from db_data_fetcher import DBCommunicator

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="AngusH579",
    password="rpisql03angus",
    hostname="AngusH579.mysql.pythonanywhere-services.com",
    databasename="AngusH579$rpi-weather-db",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Weatherdata(db.Model):
    __tablename__ = "pitsford_weather_scrape"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.TIMESTAMP)
    temp_c = db.Column(db.Float)
    feelslike_c = db.Column(db.Float)
    wx_desc = db.Column(db.String(4096))
    lat = db.Column(db.Float)
    long = db.Column(db.Float)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/workexperience')
def generic():
    return render_template('generic.html')

@app.route('/personalstatement')
def PS():
    return render_template('PS.html')

@app.route('/aboutme')
def elements():
    return render_template('elements.html')

@app.route('/tutoring')
def tutoring():
    return render_template('tutoring.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/personal projects')
def rpi():
    my_db_comm = DBCommunicator()
    db = my_db_comm.db_connector()
    curs = my_db_comm.create_cursor(db=db)
    sql = my_db_comm.create_sql_string()
    curs.execute(sql)
    result = curs.fetchall()
    df = my_db_comm.create_df(results=result)

    fig = px.scatter(df, x='time', y='temp_c', title='',
                     labels={
                        "time": "",
                        "temp_c": "Temperature /°C"
                     },
                     
                     )
    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)'})
    fig.update_xaxes(linecolor="#444")
    fig.update_yaxes(linecolor="#444")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('p_projects.html', graphJSON=graphJSON)


if __name__ == "__main__":
    app.run(debug=True)
