# Smart Home Energy Data Project

This repository contains the completed group assignment (the_actual_assignment.md) for the 'Essentials for Data science' course at Leiden University. The goal of the project was to design a system to process and analyze raw real-world data from various smart home devices (build database from scratch).

We developed a set of command-line tools and a database interface to clean, integrate, and store device messages related to temperature, humidity, motion, energy and gas usage, and weather. The data covers over a year of activity collected from one household.

The project consists of:

- A relational SQLite database to store normalized and deduplicated messages from different sources.
- A Python class interface (`HomeMessagesDB`) for accessing the database.
- Command-line scripts to process data from:
  - SmartThings (TSV files)
  - Electricity usage (P1e, gzipped CSV)
  - Gas usage (P1g, gzipped CSV)
  - Weather data (OpenWeatherMap, JSON or on-demand)
- Data analysis notebooks answering questions about patterns in energy use, occupancy, and device behavior.

## Technologies Used

- Python 3.x
- Pandas
- SQLAlchemy
- Click (for CLI tools)
- Matplotlib / Seaborn
- SQLite

## Group Members

- [Myriana Miltiadous] – [home_messages_db.py, p1e.py, p1g.py, report_gas_and_electricity_usage_weekly.ipynb, report_light_usage.ipynb]
- [Vasiliki Gkika] – [home_messages_db.py, smartthings.py, report_energy_gas_daily_usage.ipynb, report_light_usage.ipynb]
- [Pelagia Kalpakidou] – [home_messages_db.py, p1e.py, p1g.py, report_gas_and_electricity_usage_weekly.ipynb, report_energy_gas_daily_usage.ipynb]
- [Alice Abramowicz] - [openweathermap.py, generate_weatherdata.py, report_weather.ipynb]
- [Celine Li Q] - [smartthings.py]
- [Timon Huijser] - [openweathermap.py, generate_weatherdata.py, report_weather.ipynb]

## Getting Started

Information about which data are inserted in the database can be found in the_actual_assignment.md. We decided to insert in our database only files containing in their name year '2023' since those were accessible from all the data folders(some data files have names with 2023 and also include some months of 2022).

To execute the commands mentioned in the reports, it is necessary to download the entire folder containing the files associated with the 2023 data. The corresponding files are in the folders with the following names: P1e, P1g and smartthings. For the weather data the data are in weatherdata.csv. All in all, the necessary files can be downloaded as a zip file from this repository and then everything is set for executing the command line tools and create the database.

For creating the database,inserting data in it and querying it, we created a class name HomeMessagesDB which is in the home_messages_db.py script. Our database consists of 6 tables with the following structure:

sources:{ SourceId integer PRIMARY KEY NOT NULL,
Source NVARCHAR(50) NOT NULL}
messages :{ MessageId NVARCHAR(50) PRIMARY KEY,
Message NVARCHAR(50) NOT NULL,
SourceId integer NOT NULL,
FOREIGN KEY (SourceId) REFERENCES sources (SourceId)}
smartthings :{ MessageId NVARCHAR(50) PRIMARY KEY,
EpochId Integer NOT NULL,
SourceId Integer NOT NULL,
capability NVARCHAR(50),
value Integer,
unit NVARCHAR(50),
deviceLabel NVARCHAR(50),
location NVARCHAR(50),
deviceId NVARCHAR(50),
FOREIGN KEY (MessageId) REFERENCES messages (MessageId),
FOREIGN KEY (SourceId) REFERENCES sources (SourceId)}

p1e:{ EpochId Integer primary_key NOT NULL,
SourceId Integer NOT NULL,
T1 Integer,
T2 Integer,
FOREIGN KEY (SourceId) REFERENCES sources (SourceId)}

p1g :{ EpochId Integer primary_key NOT NULL,
SourceId Integer NOT NULL,
TotalGas Integer,
FOREIGN KEY (SourceId) REFERENCES sources (SourceId)}

openweathermap :{ time INTEGER PRIMARY KEY,
SourceId Integer NOT NULL,
temperature_2m REAL,
relativehumidity_2m INTEGER,
rain REAL,
snowfall REAL,
windspeed_10m REAL,
winddirection_10m INTEGER,
soil_temperature_0_to_7cm REAL,
FOREIGN KEY (SourceId) REFERENCES sources (SourceId)}

The goal was to keep all the initialized information from the files provided and in addition have the message table in which messages are generated in the message column, regarding data from the files (e.g. for p1g if total gas is 3839.584 then the message generated will be ‘the total energy usage in low-cost hours is 3839.584’, the messageId will be the name of the file from where the information is taken and a number indicated the row(e.g. P1e-2022-12-01-2023-01-10.csv.gz0). In the sources table we have just four rows containing a number from 1 to 4 and the name of the source files (p1e, p1g and smartthings).

For each of the source files categories we created a tool (p1e.py, p1g.py, smartthings.py). The tools import HomeMessagesDB class and after making the necessary manipulation of the data, they use the class to insert the data into the database. For all the data insertions, the messages table is also updated with the relevant rows according to the data. All the tools can be executed from the command prompt as in the following specifications. ( Informative messages are also generated for wrong inputs by the user ):

‘’’

P1e:
Type in command for:

-Inputting specific file: python p1e.py -d sqlite:///myhome.db P1e-2022-12-01-2023-01-10.csv.gz
-Input all files: python p1e.py -d sqlite:///myhome.db P1e-*.csv.gz
-For help: python p1e.py –help

P1g:
Type in command for:

-Inputting specific file: python p1g.py -d sqlite:///myhome.db P1g-2022-12-01-2023-01-10.csv.gz
-Input all files: python p1g.py -d sqlite:///myhome.db P1g-*.csv.gz
-For help: python p1g.py --help

Smartthings:
Type in command for:

-Inputing specific file: python smartthings.py -d sqlite:///myhome.db smartthingsLog.2023-01-03_09_01_26.tsv
-Input all files: python smartthings.py -d sqlite:///myhome.db smartthingsLog.*.tsv
-For help: python smartthings.py –help

‘’’

After executing the insertion commands, the tools print the 5 first rows from their respective
Table and the first 5 rows of the messages table, sorted by their primary keys.
The tools also check if any of the files that the user want to insert is already in the database and print appropriate message. Duplicates where also considered and deleted from all the tables so in the database there are no duplicates.

For the openweathermapdata a different procedure was followed. We decided to keep the messages table clean from openwheatherdata, so we did not add messages for the measured variables of the weatherdata. A method is added in home_messages_db.py, called make_weatherdata(), which makes the weatherdata based on the website link. With the tool generate_weatherdata.py, a file can be created called weatherdata.csv. This file is also added to github repository. This file name is used in the source table under the column 'name'. To insert the weatherdata.csv in the database's table named 'openweathermap' using both the openwheathermap.py tool and the generate_weatherdata.py tool via command prompt the following specification should be used:

‘’’

Openweathermap:
Type in command for:

-Generate the csv file: python generate_weatherdata.py -d sqlite:///myhome.db
-Input the csv file: python openweathermap.py -d sqlite:///myhome.db weatherdata.csv
-For help with the Generation: python generate_weatherdata.py -h
-For help with the Input: python openweathermap.py -h

‘’’

Finally, the following reports are provided as notebooks containing at least one question about data, one visualization and one table:

-report_gas_and_electricity_usage_weekly.ipynb
-report_energy_gas_daily_usage.ipynb
-report_weather.ipynb (at the end, there are some notes on usage of ChatGPT)
-report_light_usage.ipynb

