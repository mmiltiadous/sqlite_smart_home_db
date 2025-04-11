#type in command for inputing specifi file: python p1g.py -d sqlite:///myhome.db P1g-2022-12-01-2023-01-10.csv.gz
#or to input all files: python p1g.py -d sqlite:///myhome.db P1g-*.csv.gz 
#or for help: python p1g.py --help
#it automatically insert the info in messages db

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

    # Get a list of all files in the directory of P1g files
    files = os.listdir('./P1g')[0:]
    #input='P1g-*.csv.gz'
    if input=='P1g-*.csv.gz':
        file_paths=files
    else:
        file_paths =  [i for i in files if input in i]
    for i in range(len(file_paths)):
        file_paths[i]='./P1g/'+file_paths[i]
    return file_paths

## p1g
def create_p1g_table(file_paths):
    #read and modify files to be inserted in the database
    def read_p1g_files(file_path,num):
        p1g = pd.read_csv(file_path, compression='gzip')
        p1g[p1g.columns[0]] = p1g[p1g.columns[0]].apply(lambda dt: int(datetime.strptime(dt, "%Y-%m-%d %H:%M").timestamp()))  # convert to epoch
        p1g["Message"] = np.nan
        p1g["MessageId"] = 0
        for row in p1g.index:
            p1g.loc[row, "Message"] = f"the total gas usage is {p1g.iloc[row, 1]}"
            p1g.loc[row, "MessageId"] = f"{num}{row}"  
        # check for dublicates
        # Drop rows with missing values 
        p1g.dropna(how='any', inplace=True)
        # Check for duplicates
        #duplicates = p1g.duplicated()
        #num_duplicates = duplicates.sum()
        #print(f"Number of duplicates found: {num_duplicates}")
        # Remove duplicates
        p1g.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        return p1g
    
    p1g=read_p1g_files(file_paths[0],file_paths[0][6:])

    if len(file_paths)>1:
        for i in range(1,len(file_paths)):
            p1g2=read_p1g_files(file_paths[i],file_paths[i][6:])
            p1g=pd.concat([p1g, p1g2])

        #check in the whole table for dublicates
        duplicates = p1g.duplicated()
        num_duplicates = duplicates.sum()
        print(f"Number of duplicates found in p1g and deleted: {num_duplicates}")
        # Remove duplicates
        p1g.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        p1g['SourceId']=[3]*len(p1g)
        return p1g
    else:
        p1g['SourceId']=[3]*len(p1g)
        #check in the whole table for dublicates
        duplicates = p1g.duplicated()
        num_duplicates = duplicates.sum()
        print(f"Number of duplicates found in p1g and deleted: {num_duplicates}")
        # Remove duplicates
        p1g.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        return p1g


# communicate with the cmd 
import click

@click.command()
@click.option('-d', metavar='DBURL', help='Insert into the project database (DBURL is a SQLAlchemy database URL)')
@click.argument('csv_files', nargs=-1)
def insert_p1g(d, csv_files):
    """P1g-2022-12-01-2023-01-10.csv"""
    if d and csv_files and d.startswith('sqlite://') and csv_files[0].startswith('P1g-'):
        x = d+' '+csv_files[0]
        print('input for getting path(s):',x[20:])
        if len(get_paths(x[20:]))==1:
            if len(db_instance.db_pass_querry(f"SELECT * FROM messages WHERE  MessageId LIKE '%{str(x[20:])}%';"))!=0:
                print('the particular data are already in the database give other data')
            else:
                p1g=create_p1g_table(get_paths(x[20:])) 
                #create the table in right form to be inserted in db
                db_instance.insert_p1g(p1g) #insert the table in db
                db_instance.insert_messages(p1g)
                print(get_paths(x[20:])[0],':inserted!')

                #check for duplicates
                #...

        elif len(get_paths(x[20:]))>1:
            for i in range(len(get_paths(x[20:]))):
                if len(db_instance.db_pass_querry(f"SELECT * FROM messages WHERE  MessageId LIKE '%{str(get_paths(x[20:])[i][6:])}%';"))!=0:
                    print(get_paths(x[20:])[i],':file is already in the database')
                else:
                    print('inserting:',get_paths(x[20:])[i])
                    p1g=create_p1g_table([get_paths(x[20:])[i]]) 
                    #create the table in right form to be inserted in db
                    db_instance.insert_p1g(p1g) 
                    db_instance.insert_messages(p1g)
                    print('inserted!')
        print(db_instance.db_pass_querry("SELECT * FROM p1g ORDER BY EpochId LIMIT 5;")) #print the first 5 rows of the table just testing
        print(db_instance.db_pass_querry("SELECT * FROM messages ORDER BY MessageId LIMIT 5;")) #print the first 5 rows of the table just testing
   
    else:
        click.echo("Provide a database URL and a CSV file in that format: sqlite:///myhome.db P1g-2022-12-01-2023-01-10.csv.gz")

if __name__ == '__main__':
    insert_p1g()


