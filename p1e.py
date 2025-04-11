#type in command for inputing specific file: python p1e.py -d sqlite:///myhome.db P1e-2022-12-01-2023-01-10.csv.gz
#or to input all files: python p1e.py -d sqlite:///myhome.db P1e-*.csv.gz 
#or for help: python p1e.py --help
#it automatically insert the info in messages table

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
import datetime
from datetime import datetime
import home_messages_db 
from home_messages_db import HomeMessagesDB

db_instance = HomeMessagesDB(dbfilename = "sqlite:///myhome.db") #initialize class
db_instance.create_database() #create database
db_instance.insert_sources()

def get_paths(input):
    import os
    #Get the current working directory
    cwd = os.getcwd()
    #print('current directory',cwd)

    # Get a list of all files in the directory of P1e files
    files = os.listdir('./P1e')[0:]
    #input='P1e-*.csv.gz'
    if input=='P1e-*.csv.gz':
        file_paths=files
    else:
        file_paths =  [i for i in files if input in i]
    for i in range(len(file_paths)):
        file_paths[i]='./P1e/'+file_paths[i]
    return file_paths

## p1e - Both T1 and T2 in the same message
def create_p1e_table(file_paths):
    #read and modify files to be inserted in the database
    #file_paths = ["./P1e/P1e-2022-12-01-2023-01-10.csv.gz"]
    def read_p1e_files(file_path,str):
        p1e = pd.read_csv(file_path, compression='gzip')
        p1e = p1e.iloc[:, 0:3]

        p1e[p1e.columns[0]] = p1e[p1e.columns[0]].apply(lambda dt: int(datetime.strptime(dt, "%Y-%m-%d %H:%M").timestamp()))  # convert to epoch

        p1e["Message"] = np.nan
        p1e["MessageId"] = 0

        for row in p1e.index:
            p1e.loc[row, "Message"] = f"the total energy usage in low-cost hours is {p1e.iloc[row, 1]} and in high-cost hours {p1e.iloc[row, 2]}"
            p1e.loc[row, "MessageId"] = f"{str}{row}"   # or just row

        p1e.dropna(subset=["Electricity imported T1", "Electricity imported T2"], inplace=True)
        # Check for duplicates
        #duplicates = p1e.duplicated()
        #num_duplicates = duplicates.sum()
        #print(f"Number of duplicates found: {num_duplicates}")
        # Remove duplicates
        p1e.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        return p1e
    
    if len(file_paths)>1:
        p1e=read_p1e_files(file_paths[0],file_paths[0][6:])
        for i in range(1,len(file_paths)):
            p1e2=read_p1e_files(file_paths[i],file_paths[i][6:])
            p1e=pd.concat([p1e, p1e2])

        #check in the whole table for dublicates
        duplicates = p1e.duplicated()
        num_duplicates = duplicates.sum()
        print(f"Number of duplicates found in p1e and deleted: {num_duplicates}")
        # Remove duplicates
        p1e.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        p1e['SourceId']=[2]*len(p1e)
        return p1e
    else:
        p1e=read_p1e_files(file_paths[0],file_paths[0][6:])
        p1e['SourceId']=[2]*len(p1e)
        #check in the whole table for dublicates
        duplicates = p1e.duplicated()
        num_duplicates = duplicates.sum()
        print(f"Number of duplicates found in p1e and deleted: {num_duplicates}")
        # Remove duplicates
        p1e.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        return p1e



# communicate with the cmd 

import click

@click.command()
@click.option('-d', metavar='DBURL', help='Insert into the project database (DBURL is a SQLAlchemy database URL)')
@click.argument('csv_files', nargs=-1)
def insert_p1e(d, csv_files):
    """P1e-2022-12-01-2023-01-10.csv.gz"""
    if d and csv_files and d.startswith('sqlite://') and csv_files[0].startswith('P1e-'):
        x = d+' '+csv_files[0]
        print('input for getting path(s):',x[20:])
        if len(get_paths(x[20:]))==1:
            if len(db_instance.db_pass_querry(f"SELECT * FROM messages WHERE  MessageId LIKE '%{str(x[20:])}%';"))!=0:
                print('the particular data are already in the database give other data')
            else:
                p1e=create_p1e_table(get_paths(x[20:])) 
                #create the table in right form to be inserted in db
                db_instance.insert_p1e(p1e) #insert the table in db
                db_instance.insert_messages(p1e)
                print(get_paths(x[20:])[0],':inserted!')
        elif len(get_paths(x[20:]))>1:
            for i in range(len(get_paths(x[20:]))):
                if len(db_instance.db_pass_querry(f"SELECT * FROM messages WHERE  MessageId LIKE '%{str(get_paths(x[20:])[i][6:])}%';"))!=0:
                    print(get_paths(x[20:])[i],':file is already in the database')
                else:
                    print('inserting:',get_paths(x[20:])[i])
                    p1e=create_p1e_table([get_paths(x[20:])[i]]) 
                    #create the table in right form to be inserted in db
                    db_instance.insert_p1e(p1e) 
                    db_instance.insert_messages(p1e)
                    print('inserted!')
        print(db_instance.db_pass_querry("SELECT * FROM p1e ORDER BY EpochId LIMIT 5;")) #print the first 5 rows of the table just testing
        print(db_instance.db_pass_querry("SELECT * FROM messages ORDER BY MessageId LIMIT 5;")) #print the first 5 rows of the table just testing
    else:
        click.echo("Provide a database URL and a CSV file in that format: sqlite:///myhome.db P1e-2022-12-01-2023-01-10.csv.gz")

if __name__ == '__main__':
    insert_p1e()








