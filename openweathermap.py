import click
import pandas as pd
from home_messages_db import HomeMessagesDB

@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('-d', '--database', 'dburl', required=True, help='Insert into the project database (DBURL is a SQLAlchemy database URL)')
@click.help_option('-h', '--help')
def openweathermap(file, dburl):
    """
    Insert weather data from the openweathermap file into the database.

    Usage:
    python openweathermap.py [OPTIONS] weatherdata.csv

    Output options:
    -d DBURL  insert into the project database (DBURL is a SQLAlchemy database URL)
    """

    # Create an instance of HomeMessagesDB
    db = HomeMessagesDB(dburl)

    # Insert weather data into the database
    db.create_database()
    db.insert_openweathermap(file)

    # Print some information about the inserted data
    print(f"Weather data from {file} inserted into the database.")

if __name__ == '__main__':
    openweathermap()