import json
import requests
import os
import csv
import sqlite3
import ssl

API_KEY = "69da2ed4"
dir_path = os.path.dirname(os.path.realpath(__file__))
CACHE_FNAME = dir_path + '/' + "project_cache_movie.json"

conn = sqlite3.connect(dir_path + '/' + 'movie_info.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Movies (id INTEGER PRIMARY KEY, Rating NUMERIC, Year NUMERIC)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Runtimes (id INTEGER PRIMARY KEY, Runtimes NUMERIC, Year NUMERIC)''')
cur.execute('''CREATE TABLE IF NOT EXISTS Names (id INTEGER PRIMARY KEY, Name TEXT UNIQUE)''')

def findTitles(filename):

    # Reads from a file containing the list of titles to look up and returns a list of those titles

    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + filename, "r") as f:
        lines = f.readlines()
    return [title.strip() for title in lines]

def check_previous_titles(cur):

    # Checks to see what's currently in the database.

    cur.execute("SELECT Names.name FROM Names INNER JOIN Movies ON Names.id = Movies.id")
    titles = []
    for item in cur.fetchall():
        titles.append(item[0])
    return titles   

def get_data(prev_titles, all_movies):

    # Makes the API request but in loops of 20

    total_list = []
    count = 0
    for title in all_movies:
        if title not in prev_titles:
            request_url = "http://www.omdbapi.com/?i=tt3896198&apikey={}&t={}&type={}&plot={}&r={}".format(API_KEY,title,'movie','short','json')
            r = requests.get(request_url)
            dic = json.loads(r.text)
            name = dic["Title"]
            ratings = dic["imdbRating"]
            year = dic["Year"]
            runtime = dic["Runtime"]
            total_list.append((name, ratings, year, runtime))
            count += 1    
        else:
            #print(title + " is already in database. Moving on.")    
            continue
        if count == 20:
            break
    return total_list    



def insert_data(lst, conn, cur):

    # Inserts the data into a database

    for n in lst:
        name = n[0]
        ratings = n[1]
        year = n[2]
        runtime = n[3]
        cur.execute("INSERT OR IGNORE INTO Names (name) VALUES (?)", (name, ))
        cur.execute("SELECT id FROM Names WHERE name = ?", (name, ))
        mov_id = cur.fetchone()[0]
        cur.execute("INSERT OR IGNORE INTO Movies (id, Rating, Year) VALUES (?,?,?)",(mov_id,ratings,year))
        cur.execute("INSERT OR IGNORE INTO Runtimes (id, Runtimes, Year) VALUES (?,?,?)",(mov_id,runtime,year))
    conn.commit()    
       
                 
def main():
    previous_titles = check_previous_titles(cur)
    all_titles = findTitles("titles.text")
    stuff = get_data(previous_titles, all_titles)
    insert_data(stuff, conn, cur)
    conn.close()        

if __name__ == "__main__":
    main()