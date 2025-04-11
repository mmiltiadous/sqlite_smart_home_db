import click
import os
from home_messages_db import HomeMessagesDB

@click.command()
@click.option('-d', '--database', 'dburl', required=True, help='Specify the database URL')
@click.help_option('-h', '--help')
def generate_weatherdata(dburl):
    """
    Generate weather data file using the make_weatherdata() function from HomeMessagesDB.

    Usage:
    python generate_weatherdata.py [OPTIONS]

    Options:
    -d, --database DBURL    Specify the database URL

    Examples:
    python generate_weatherdata.py -d sqlite:///myhome.db
    """

    # Specify the file path for the weather data
    file_path = 'weatherdata.csv'

    # Check if the weather data file already exists
    if os.path.exists(file_path):
        print(f"You have already generated {file_path}")
    else:
        # Create an instance of HomeMessagesDB
        db = HomeMessagesDB(dburl)

        # Generate the weather data using the make_weatherdata() function
        db.make_weatherdata()

        print(f'{file_path} has been generated successfully.')


if __name__ == '__main__':
    generate_weatherdata()