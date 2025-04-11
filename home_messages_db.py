#You need to have four folders in the folder of the scripts. One for P1E files, one for P1g files,one for smartthings and one for OpenWeatherMap files.

import sqlalchemy as sa
import sqlalchemy.orm as orm
import sqlite3
from sqlite3 import Error
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
sb.set_theme(style="darkgrid")
import pandas as pd      
import os
import requests


class HomeMessagesDB:
    def __init__(self, dbfilename):
        self.dbfilename = dbfilename
        self.engine = sa.create_engine(dbfilename, echo=True)
        self.conn = sqlite3.connect(f'.{self.dbfilename[9:]}')  #create database
        self.cursor = self.conn.cursor()
    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
            :param create_table_sql: a CREATE TABLE statement
         """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
            # Commit your changes in the database
            self.conn.commit()
        except Error as e:
            print(e) 

    def create_database(self):
        create_sources_table = """ CREATE TABLE IF NOT EXISTS sources (
                                        SourceId integer PRIMARY KEY NOT NULL,
                                        Source NVARCHAR(50) NOT NULL
                                    ); """
        create_messages_table = """CREATE TABLE IF NOT EXISTS messages (
                                    MessageId NVARCHAR(50) PRIMARY KEY,
                                    Message NVARCHAR(50) NOT NULL,
                                    SourceId integer NOT NULL,
                                    FOREIGN KEY (SourceId) REFERENCES sources (SourceId)
                                    ON DELETE NO ACTION ON UPDATE NO ACTION
                                );"""
        create_smartthings_table = """CREATE TABLE IF NOT EXISTS smartthings (
                                    MessageId NVARCHAR(50) PRIMARY KEY,
                                    EpochId Integer NOT NULL,
                                    SourceId Integer NOT NULL,
                                    capability NVARCHAR(50),
                                    value Integer,
                                    unit NVARCHAR(50),
                                    deviceLabel NVARCHAR(50),
                                    location NVARCHAR(50),
                                    deviceId NVARCHAR(50),
                                    FOREIGN KEY (MessageId) REFERENCES messages (MessageId),
                                    FOREIGN KEY (SourceId) REFERENCES sources (SourceId)
                                    );"""
        create_p1e_table = """CREATE TABLE IF NOT EXISTS p1e (
                                    EpochId Integer primary_key NOT NULL,
                                    SourceId Integer NOT NULL,
                                    T1 Integer,
                                    T2 Integer,
                                    FOREIGN KEY (SourceId) REFERENCES sources (SourceId)
                                    );"""
        create_p1g_table = """CREATE TABLE IF NOT EXISTS p1g (
                                    EpochId Integer primary_key NOT NULL,            
                                    SourceId Integer NOT NULL,
                                    TotalGas Integer,          
                                    FOREIGN KEY (SourceId) REFERENCES sources (SourceId)                                                     
                                     );"""
        create_openweathermap_table = """ CREATE TABLE IF NOT EXISTS openweathermap(
                                        time INTEGER PRIMARY KEY,
                                        SourceId Integer NOT NULL,
                                        temperature_2m REAL,
                                        relativehumidity_2m INTEGER,
                                        rain REAL,
                                        snowfall REAL,
                                        windspeed_10m REAL,
                                        winddirection_10m INTEGER,
                                        soil_temperature_0_to_7cm REAL,
                                        FOREIGN KEY (SourceId) REFERENCES sources (SourceId)
                                    );"""
        # create tables
        self.cursor.execute(f"DROP TABLE IF EXISTS sources")

        self.create_table(create_sources_table)
        self.create_table(create_messages_table)
        self.create_table(create_smartthings_table)
        self.create_table(create_p1e_table)
        self.create_table(create_p1g_table)
        self.create_table(create_openweathermap_table)

    def insert_p1e(self,p1e1):
        self.create_database()   
        cursor = self.conn.cursor()
        ## insert p1e data
        #p1e=create_p1e_table()
        p1e=p1e1
        p1e.rename(columns={p1e.columns[0]: "EpochId"}, inplace=True)
        p1e.rename(columns={p1e.columns[1]: "T1"}, inplace=True)
        p1e.rename(columns={p1e.columns[2]: "T2"}, inplace=True)
        p1e_data=pd.concat([p1e["EpochId"], p1e["SourceId"],p1e["T1"],p1e["T2"]], axis=1)
        # creating column list for insertion
        cols = ",".join([str(i) for i in p1e_data.columns.tolist()])
        # Insert DataFrame records one by one.
        for i, row in p1e_data.iterrows():
            sql = "INSERT INTO p1e ({}) VALUES ({})".format(cols, ",".join(["?"] * len(row)))
            cursor.execute(sql, tuple(row))
            self.conn.commit()
        #remove duplicates if the same data is inserted:
        cursor.execute(f"DELETE FROM p1e WHERE rowid NOT IN (SELECT MIN(rowid) FROM p1e GROUP BY EpochId,SourceId, T1, T2)") 
        self.conn.commit()

    def insert_p1g(self,p1g1):
        self.create_database()   
        cursor = self.conn.cursor()
        ##insert p1g data
        #p1g=create_p1g_table()
        p1g=p1g1
        p1g.rename(columns={p1g.columns[0]: "EpochId"}, inplace=True)
        p1g.rename(columns={p1g.columns[1]: "TotalGas"}, inplace=True)
        p1g_data=pd.concat([p1g["EpochId"], p1g["SourceId"],p1g["TotalGas"]], axis=1)
        # creating column list for insertion
        cols = ",".join([str(i) for i in p1g_data.columns.tolist()])
        # Insert DataFrame records one by one.
        for i, row in p1g_data.iterrows():
            sql = "INSERT INTO p1g ({}) VALUES ({})".format(cols, ",".join(["?"] * len(row)))
            cursor.execute(sql, tuple(row))
            self.conn.commit()
        #remove duplicates if the same data is inserted:
        cursor.execute(f"DELETE FROM p1g WHERE rowid NOT IN (SELECT MIN(rowid) FROM p1g GROUP BY EpochId,SourceId,TotalGas)") 
        self.conn.commit()
        
        
    def insert_smartthings(self,smartthings1):
        self.create_database()   
        cursor = self.conn.cursor()
        ##insert smartthings data
        #smartthings=create_smartthings_table()
        smartthings=smartthings1
        smartthings.rename(columns={smartthings.columns[0]: "EpochId"}, inplace=True)
        smartthings_data=pd.concat([smartthings["MessageId"],
                                    smartthings["EpochId"], 
                                    smartthings["SourceId"],
                                    smartthings["capability"],
                                    smartthings["value"],
                                    smartthings["unit"],
                                    smartthings["deviceLabel"],
                                    smartthings["location"],
                                    smartthings["deviceId"]], axis=1)
        # creating column list for insertion
        cols = ",".join([str(i) for i in smartthings_data.columns.tolist()])
        # Insert DataFrame records one by one.
        for i, row in smartthings_data.iterrows():
            sql = "INSERT INTO smartthings ({}) VALUES ({})".format(cols, ",".join(["?"] * len(row)))
            cursor.execute(sql, tuple(row))
            self.conn.commit()  
    
    # Functions to insert openweather data
    # Since we are unsure that a link would stay forever, we made a table based on the link to the weatherdata, and saved that data. 
    # We also added that file it to the repository
    def insert_openweathermap(self, weatherdata): # maybe we should change it to only have argument "self" and add a link in the function
        self.create_database()   
        cursor = self.conn.cursor()
        weatherdata = pd.read_csv(weatherdata)
        ## insert openweathermap data
        cols = ",".join([str(i) for i in weatherdata.columns.tolist()])
        # Insert DataFrame records one by one.
        for i, row in weatherdata.iterrows():
            sql = "INSERT INTO openweathermap ({}) VALUES ({})".format(cols, ",".join(["?"] * len(row)))
            cursor.execute(sql, tuple(row))
            self.conn.commit()

    # In order to show how we made the weatherdata, we added this function:
    def make_weatherdata(self, link = "https://archive-api.open-meteo.com/v1/era5?latitude=52&longitude=4&timeformat=unixtime&start_date=2023-01-01&end_date=2023-05-15&hourly=temperature_2m,relativehumidity_2m,rain,snowfall,windspeed_10m,winddirection_10m,soil_temperature_0_to_7cm"):
        file_path = 'weatherdata.csv'
        if  os.path.exists(file_path):
            print(f'You have already made {file_path}')
        else:
            response = requests.get(link)
            data = response.json()

            # Convert response data to a DataFrame
            df = pd.DataFrame(data["hourly"])
            df = df.dropna()
            df['SourceId'] = 4
            df.to_csv(file_path, index = False)
            print(f'{file_path} has been made succesfully using the following link: {link}')


    def insert_messages(self,file):
        self.create_database()
        cursor = self.conn.cursor()
        ##insert messages data
        file_m=pd.concat([file["MessageId"], file["Message"],file["SourceId"]], axis=1)
        #combine them vertivally
        #insert them to table in database
        # creating column list for insertion
        cols = ",".join([str(i) for i in file_m.columns.tolist()])
        # Insert DataFrame recrds one by one.
        for i, row in file_m.iterrows():
            sql = "INSERT INTO messages ({}) VALUES ({})".format(cols, ",".join(["?"] * len(row)))
            cursor.execute(sql, tuple(row))
            self.conn.commit() 

    def insert_sources(self):
        self.create_database()
        #Creating a cursor object using the cursor() method
        cursor = self.conn.cursor()
        ##insert source data
        sources = pd.DataFrame({'SourceId': [1, 2, 3, 4],
                                'Source': ['SmartThings', 'P1E', 'P1G', 'weatherdata.csv']})
        # creating column list for insertion
        cols = ",".join([str(i) for i in sources.columns.tolist()])
        # Insert DataFrame recrds one by one.
        for i, row in sources.iterrows():
            sql = "INSERT INTO sources ({}) VALUES ({})".format(cols, ",".join(["?"] * len(row)))
            cursor.execute(sql, tuple(row))
            self.conn.commit()
            
    def db_pass_querry(self,text):
        #i.e text:"SELECT * FROM EMPLOYEE LIMIT 5"
        #Creating a cursor object using the cursor() method
        sql2 = str(sa.text(text))
        a=pd.read_sql(sql2,self.conn)
        return a
    
    

        