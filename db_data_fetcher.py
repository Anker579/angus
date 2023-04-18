import MySQLdb
import datetime as dt
from dotenv import load_dotenv, find_dotenv
import os
import pandas as pd
import plotly.express as px
# from dotenv import dotenv_values
# config = dotenv_values(".env")

# load_dotenv(find_dotenv())

class DBCommunicator():

    def __init__(self) -> None:
        self.HOST = os.getenv("HOST")
        self.DATABASE = os.getenv("DATABASE")
        self.USER = os.getenv("USER")
        self.PASSWORD = os.getenv("PASSWORD")

    def db_connector(self):
        print(self.HOST, self.DATABASE, self.USER, self.PASSWORD)
        db = MySQLdb.connect(host=self.HOST,
            database=self.DATABASE,
            user=self.USER,
            password=self.PASSWORD)
        return db

    def create_cursor(self, db):
        curs = db.cursor()
        return curs
    
    def create_sql_string(self):
        sql = ("SELECT time, temp_c FROM pitsford_weather_scrape")        
        return sql
    
    def create_df(self, results):
        df = pd.DataFrame(results, columns=['time', 'temp_c'])
        return df
    
    # def create_data_tuple(self, data_dict):
    #     '''example data: data = (time, 10, 8, "cold", 51, 8)'''
    #     time = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     temp_c = data_dict["temp_c"]
    #     feelslike_c = data_dict["feelslike_c"]
    #     wx_desc = data_dict["wx_desc"]
    #     lat = data_dict["lat"]
    #     long = data_dict["long"]
    #     data = (time, temp_c, feelslike_c, wx_desc, lat, long)
    #     return data


if __name__ == "__main__":
    my_db_comm = DBCommunicator()
    db = my_db_comm.db_connector()
    curs = my_db_comm.create_cursor(db=db)
    sql = my_db_comm.create_sql_string()
    curs.execute(sql)
    result = db.fetchall()
    df = my_db_comm.create_df(results=result)
    fig = px.scatter(df, x='time', y='temp_c', title='Temperature vs Time')
    fig.show()