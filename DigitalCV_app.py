from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
import json
from dotenv import load_dotenv
import plotly
import plotly.express as px
from db_data_fetcher import DBCommunicator
import MySQLdb # <-- Added for the review system

app = Flask(__name__)
# IMPORTANT: Add a secret key for flash messaging to work.
# Change this to a random, secure string.
app.secret_key = 'a-very-secret-and-random-string'

# --- Connection for Weather Data (using SQLAlchemy) ---
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="AngusH579",
    password="rpisql03angus", # Your weather-db password
    hostname="AngusH579.mysql.pythonanywhere-services.com",
    databasename="AngusH579$rpi-weather-db",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- Connection Details for the Reviews Database ---
# Replace with your new database details for the reviews table
reviews_db_host = 'AngusH579.mysql.pythonanywhere-services.com'
reviews_db_user = 'AngusH579'
reviews_db_password = 'rpisql03angus' # <-- IMPORTANT: ADD YOUR PASSWORD
reviews_db_name = 'AngusH579$rpi-weather-db'     # <-- IMPORTANT: USE YOUR DB NAME FOR REVIEWS

def get_reviews_db_connection():
    """Establishes a connection to the reviews database."""
    connection = MySQLdb.connect(
        host=reviews_db_host,
        user=reviews_db_user,
        passwd=reviews_db_password,
        db=reviews_db_name
    )
    return connection


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


# --- NEW TUTORING ROUTE ---
@app.route('/tutoring', methods=['GET', 'POST'])
def tutoring():
    # --- Part 1: Handle the form submission (POST request) ---
    if request.method == 'POST':
        conn = None
        try:
            reviewer = request.form.get('reviewer_name')
            rating = request.form.get('rating')
            review_text = request.form.get('review_text')

            if not reviewer or not rating or not review_text:
                flash('All fields are required!', 'error')
                return redirect(url_for('tutoring_page'))

            conn = get_reviews_db_connection()
            cursor = conn.cursor()
            sql = "INSERT INTO reviews (reviewer_name, rating, review_text) VALUES (%s, %s, %s)"
            values = (reviewer, int(rating), review_text)
            cursor.execute(sql, values)
            conn.commit()
            
            flash('Thank you for your review! It will be displayed once approved.', 'success')

        except Exception as e:
            print(f"Error inserting review: {e}")
            flash('Sorry, there was an error submitting your review.', 'error')
            if conn: conn.rollback()
        finally:
            if conn: conn.close()
        
        return redirect(url_for('tutoring_page'))

    # --- Part 2: Display the page (GET request) ---
    conn = None
    reviews_list = []
    try:
        conn = get_reviews_db_connection()
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT reviewer_name, rating, review_text, review_date FROM reviews WHERE is_approved = TRUE ORDER BY review_date DESC"
        cursor.execute(sql)
        reviews_list = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching reviews: {e}")
        # Optionally flash an error if reviews can't be loaded
        # flash('Could not load reviews at this time.', 'error')
    finally:
        if conn: conn.close()

    return render_template('tutoring.html', reviews=reviews_list)


@app.route('/projects')
def projects():
    my_db_comm = DBCommunicator()
    db_conn = my_db_comm.db_connector()
    curs = my_db_comm.create_cursor(db=db_conn)
    sql = my_db_comm.create_sql_string()
    curs.execute(sql)
    result = curs.fetchall()
    df = my_db_comm.create_df(results=result)

    fig = px.scatter(df, x='time', y='temp_c', title='',
                     labels={"time": "", "temp_c": "Temperature /°C"})
    fig.update_layout({'plot_bgcolor': 'rgba(0,0,0,0)'})
    fig.update_xaxes(linecolor="#444")
    fig.update_yaxes(linecolor="#444")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('p_projects.html', graphJSON=graphJSON)


if __name__ == "__main__":
    app.run(debug=True)