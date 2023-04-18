from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
import json
from dotenv import load_dotenv
import plotly
import plotly.express as px
from db_data_fetcher import DBCommunicator

load_dotenv()

app = Flask(__name__)


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

@app.route('/rpi')
def rpi():

    my_db_comm = DBCommunicator()
    db = my_db_comm.db_connector()
    curs = my_db_comm.create_cursor(db=db)
    sql = my_db_comm.create_sql_string()
    curs.execute(sql)
    result = db.fetchall()
    df = my_db_comm.create_df(results=result)

    fig = px.scatter(df, x='time', y='temp_c', title='Temperature vs Time')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('Rpi.html', graphJSON=graphJSON)

if __name__ == "__main__":
    app.run(debug=True)

