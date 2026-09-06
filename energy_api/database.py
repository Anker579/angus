import os
import MySQLdb


def get_energy_db_connection():
    connection = MySQLdb.connect(
        host=os.getenv("ENERGY_DB_HOST"),
        user=os.getenv("ENERGY_DB_USER"),
        passwd=os.getenv("ENERGY_DB_PASSWORD"),
        db=os.getenv("ENERGY_DB_NAME")
    )

    return connection