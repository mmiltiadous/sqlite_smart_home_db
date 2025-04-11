#type in command for inputing specific file: python smartthings.py -d sqlite:///myhome.db smartthingsLog.2023-01-03_09_01_26.tsv
#or to input all files: python smartthings.py -d sqlite:///myhome.db smartthingsLog.*.tsv
#or for help: python smartthings.py --help
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

    # Get a list of all files in the directory of Smartthings files
    files = os.listdir('./smartthings')[0:]
    #input='smartthings-*.csv.gz'
    if input=='smartthingsLog.*.tsv':
        file_paths=files
    else:
        file_paths =  [i for i in files if input in i]
    for i in range(len(file_paths)):
        file_paths[i]='./smartthings/'+file_paths[i]
    return file_paths

def create_smartthings_table(file_paths):
    #file_paths = ['./smartthings/smartthingsLog.2023-01-16_16_54_26.tsv','./smartthings/smartthingsLog.2023-01-16_16_54_26.tsv']
    def read_smartthings_files(file_path,str1):
        df = pd.read_csv(file_path, sep='\t')
        epoch_time = []
        for timestamp in df['epoch']:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                c = int(dt.timestamp())
            except ValueError:
                c = float('nan')  # Set NaN for invalid timestamps
            epoch_time.append(c)

        df['epoch'] = epoch_time
        df = df.dropna(subset=['epoch'])

        #remove duplicates
        delete_indeces = []
        for i in range(1, len(df)):
            if (df.iloc[i,0:3] == df.iloc[i-1,0:3]).all() and (df.iloc[i,5:] == df.iloc[i-1,5:]).all():
                delete_indeces.append(i-1)    

        df = df.drop(delete_indeces)
        df = df.reset_index(drop=True)


        # messageId
        df['MessageId'] = [None]*len(df)
        for i in range(len(df)):
            df.loc[i, 'MessageId'] = str(f'{str1}:')+str(df.loc[i, 'attribute'])[0:3] + str(i)

        # message column
        df['unit'] = df['unit'].fillna('')
        df['Message'] = [None]*len(df)
        for row in df.index: 
            df.loc[row, "Message"] = f"{df.iloc[row, 6]} - {df.iloc[row, 2]} {df.iloc[row, 3]}{df.iloc[row, 4]}"
        return df
    
    if len(file_paths)>1:
        smartthings=read_smartthings_files(file_paths[0],file_paths[0][14:])
        for i in range(1,len(file_paths)):
            smartthings2=read_smartthings_files(file_paths[i],file_paths[i][14:])
            smartthings=pd.concat([smartthings, smartthings2])

        #check in the whole table for dublicates
        duplicates = smartthings.duplicated()
        num_duplicates = duplicates.sum()
        print(f"Number of duplicates found in smartthings and deleted: {num_duplicates}")
        # Remove duplicates
        smartthings.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        smartthings['SourceId']=[1]*len(smartthings)
        return smartthings
    else:
        smartthings=read_smartthings_files(file_paths[0],file_paths[0][14:])
        smartthings['SourceId']=[1]*len(smartthings)
        #check in the whole table for dublicates
        duplicates = smartthings.duplicated()
        num_duplicates = duplicates.sum()
        print(f"Number of duplicates found in smartthings and deleted: {num_duplicates}")
        # Remove duplicates
        smartthings.drop_duplicates(inplace=True)
        #return the resulting DataFrame
        return smartthings
    
# communicate with the cmd 
import click

@click.command()
@click.option('-d', metavar='DBURL', help='Insert into the project database (DBURL is a SQLAlchemy database URL)')
@click.argument('csv_files', nargs=-1)
def insert_smartthings(d, csv_files):
    """smartthingsLog.1.tsv [smartthingsLog.2.tsv ...]"""
    if d and csv_files and d.startswith('sqlite://') and csv_files[0].startswith('smartthingsLog.'):
        x = d+' '+csv_files[0]
        print('input for getting path(s):',str(x[20:]))
        if len(get_paths(x[20:]))==1:
            if len(db_instance.db_pass_querry(f"SELECT * FROM messages WHERE  MessageId LIKE '%{str(x[20:])}%';"))!=0:
                print('the particular data are already in the database give other data')
            else:
                smartthings=create_smartthings_table(get_paths(x[20:])) 
                #create the table in right form to be inserted in db
                db_instance.insert_smartthings(smartthings) #insert the table in db
                db_instance.insert_messages(smartthings)
                print(get_paths(x[20:])[0],':inserted!')
        elif len(get_paths(x[20:]))>1:
            for i in range(len(get_paths(x[20:]))):
                if len(db_instance.db_pass_querry(f"SELECT * FROM messages WHERE  MessageId LIKE '%{str(get_paths(x[20:])[i][14:])}%';"))!=0:
                    print(get_paths(x[20:])[i],':file is already in the database')
                else:
                    print('inserting:',get_paths(x[20:])[i])
                    smartthings=create_smartthings_table([get_paths(x[20:])[i]]) 
                    #create the table in right form to be inserted in db
                    db_instance.insert_smartthings(smartthings) 
                    db_instance.insert_messages(smartthings)
                    print('inserted!')
        print(db_instance.db_pass_querry("SELECT * FROM smartthings ORDER BY MessageId LIMIT 5;")) #print the first 5 rows of the table just testing
        print(db_instance.db_pass_querry("SELECT * FROM messages ORDER BY MessageId LIMIT 5;")) #print the first 5 rows of the table just testing

    else:
        click.echo("Provide a database URL and a TSV file in that format: sqlite:///myhome.db smartthingsLog.2023-01-03_09_01_26.tsv")

if __name__ == '__main__':
    insert_smartthings()