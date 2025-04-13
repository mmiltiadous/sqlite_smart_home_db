# Smart Home Energy Data Project

This repository contains the final group project for the Essentials for Data Science course at Leiden University. The objective was to design and implement a system that processes and analyzes real-world data from various smart home devices by building a structured, queryable database from scratch.

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

## Used

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

## Important information

Information about which data are inserted in the database can be found in the_actual_assignment.md. We decided to insert in our database only files containing in their name year '2023' since those were accessible from all the data folders(some data files have names with 2023 and also include some months of 2022).

To execute the commands mentioned in the reports, it is necessary to download the entire folder containing the files associated with the 2023 data. The corresponding files are in the folders with the following names: P1e, P1g and smartthings. For the weather data the data are in weatherdata.csv. All in all, the necessary files can be downloaded as a zip file from this repository and then everything is set for executing the command line tools and create the database.

For creating the database,inserting data in it and querying it, we created a class name HomeMessagesDB which is in the home_messages_db.py script. Our database consists of 6 tables with the following structure:


### `sources`

Stores metadata about data sources.

```sql
SourceId INTEGER PRIMARY KEY NOT NULL,
Source NVARCHAR(50) NOT NULL
```
### `messages`

Stores messages linked to specific sources.

```sql
MessageId NVARCHAR(50) PRIMARY KEY,
Message NVARCHAR(50) NOT NULL,
SourceId INTEGER NOT NULL,
FOREIGN KEY (SourceId) REFERENCES sources(SourceId)
```

---

### `smartthings`

Contains sensor readings from SmartThings devices.

```sql
MessageId NVARCHAR(50) PRIMARY KEY,
EpochId INTEGER NOT NULL,
SourceId INTEGER NOT NULL,
capability NVARCHAR(50),
value INTEGER,
unit NVARCHAR(50),
deviceLabel NVARCHAR(50),
location NVARCHAR(50),
deviceId NVARCHAR(50),
FOREIGN KEY (MessageId) REFERENCES messages(MessageId),
FOREIGN KEY (SourceId) REFERENCES sources(SourceId)
```

---

### `p1e`

Stores electricity consumption data.

```sql
EpochId INTEGER PRIMARY KEY NOT NULL,
SourceId INTEGER NOT NULL,
T1 INTEGER,
T2 INTEGER,
FOREIGN KEY (SourceId) REFERENCES sources(SourceId)
```

---

### `p1g`

Stores gas consumption measurements.

```sql
EpochId INTEGER PRIMARY KEY NOT NULL,
SourceId INTEGER NOT NULL,
TotalGas INTEGER,
FOREIGN KEY (SourceId) REFERENCES sources(SourceId)
```

---

### `openweathermap`

Contains external weather data from OpenWeatherMap.

```sql
time INTEGER PRIMARY KEY,
SourceId INTEGER NOT NULL,
temperature_2m REAL,
relativehumidity_2m INTEGER,
rain REAL,
snowfall REAL,
windspeed_10m REAL,
winddirection_10m INTEGER,
soil_temperature_0_to_7cm REAL,
FOREIGN KEY (SourceId) REFERENCES sources(SourceId)
```

The goal was to keep all the initialized information from the files provided and in addition have the message table in which messages are generated in the message column, regarding data from the files (e.g. for p1g if total gas is 3839.584 then the message generated will be ‘the total energy usage in low-cost hours is 3839.584’, the messageId will be the name of the file from where the information is taken and a number indicated the row(e.g. P1e-2022-12-01-2023-01-10.csv.gz0). In the sources table we have just four rows containing a number from 1 to 4 and the name of the source files (p1e, p1g and smartthings).

For each of the source files categories we created a tool (p1e.py, p1g.py, smartthings.py). The tools import HomeMessagesDB class and after making the necessary manipulation of the data, they use the class to insert the data into the database. For all the data insertions, the messages table is also updated with the relevant rows according to the data. All the tools can be executed from the command prompt as in the following specifications. ( Informative messages are also generated for wrong inputs by the user ):

## Usage

### P1e:
Run one of the following commands:

- **Insert a specific file:**
```bash
python p1e.py -d sqlite:///myhome.db P1e-2022-12-01-2023-01-10.csv.gz
```
- **Insert all matching files:**
python p1e.py -d sqlite:///myhome.db P1e-*.csv.gz
- **Display help message:**
python p1e.py –help

### P1g:
Run one of the following commands:

- **Insert a specific file:**
python p1g.py -d sqlite:///myhome.db P1g-2022-12-01-2023-01-10.csv.gz
- **Insert all matching files:**
python p1g.py -d sqlite:///myhome.db P1g-*.csv.gz
- **Display help message:**
python p1g.py --help

### Smartthings:
Run one of the following commands:

- **Insert a specific file:**
python smartthings.py -d sqlite:///myhome.db smartthingsLog.2023-01-03_09_01_26.tsv
- **Insert all matching files:**
python smartthings.py -d sqlite:///myhome.db smartthingsLog.*.tsv
- **Display help message:**
python smartthings.py –help


## Openweathermap:

The OpenWeatherMap data is handled differently. We chose to exclude its messages from the messages table to keep it clean. Instead, weather data is stored in a separate table called openweathermap.

A method called make_weatherdata() is provided in home_messages_db.py to fetch and format weather data from the official OpenWeatherMap website. The tool generate_weatherdata.py uses this method to generate a CSV file (weatherdata.csv), which is already included in this repository. This file name is used in the source table under the column 'name'. To insert the weatherdata.csv in the database's table named 'openweathermap' using both the openwheathermap.py tool and the generate_weatherdata.py tool via command prompt the following commands should be used:

- **Generate the CSV file:**
python generate_weatherdata.py -d sqlite:///myhome.db
- **Insert the generated file into the database:**
python openweathermap.py -d sqlite:///myhome.db weatherdata.csv
- **Help for generating the CSV:**
python generate_weatherdata.py --help
- **Help for inserting the CSV:**
python openweathermap.py --help

## Notes:

After executing the insertion commands, the tools print the 5 first rows from their respective Table and the first 5 rows of the messages table, sorted by their primary keys.
The tools also check if any of the files that the user want to insert is already in the database and print appropriate message. Duplicates were also considered and deleted from all the tables so in the database there are no duplicates.


## Data reports: 
The following reports are provided as notebooks containing at least one question about data, one visualization and one table as requested by the assignment:

- **report_gas_and_electricity_usage_weekly.ipynb**
- **report_energy_gas_daily_usage.ipynb**
- **report_weather.ipynb (at the end, there are some notes on usage of ChatGPT)**
- **report_light_usage.ipynb**


