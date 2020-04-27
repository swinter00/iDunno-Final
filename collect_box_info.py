from bs4 import BeautifulSoup
import requests
import os
import sqlite3

'''
INSTRUCTIONS TO RUN:
Run this file until the output states that 219 entries are in the database. That is the total amount
of movies that the data analysis is ran on.
'''

def generateTitleYearLinks(prev_titles):
    ''' 
    This function accesses a Wikipedia page that lists all Academy Award winning films. It uses
    beautiful soup to extract the links to the movies released after the year 2000 included on this 
    list. It returns a list of tuples containing the title, year released, and Wikipedia page link
    for each movie. The input is a list of titles previously added to the database, and the function
    will check to only add new titles to the returned list.
    '''
    wiki_page = requests.get("https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films")
    soup = BeautifulSoup(wiki_page.text, "html.parser")
    movies=soup.find_all("tr")
    movie_info = []
    for item in movies:
        try:
            new_item = item.td.next_sibling.next_sibling
            year = int(new_item.a.text)
            if year >= 2000:
                title = item.td.i.a["title"]
                if "film)" in title:
                    title = title.split("(")[0].strip()
                if title in prev_titles:
                    continue
                link = "https://en.wikipedia.org" + item.td.i.a["href"]
                movie_info.append((title, year, link))
        except:
            continue
    return movie_info

def generateTitleYearBox(movie_info):
    '''
    This function takes in a list of tuples containing movie titles, release years, and Wikipedia
    page links. For each movie in the list, the function generates a Beautiful Soup object of the 
    Wikipedia page and extracts the box office gross of the movie. This number is formatted to be read
    as an integer. The function returns a list of tuples containing the title, year released, and box
    office gross of each movie. The function uses a ticker system to ensure that only 20 items are
    accessed and added.
    '''
    ticker = 0
    title_year_box = []
    for title, year, link in movie_info:
        page = requests.get(link)
        msoup = BeautifulSoup(page.text, "html.parser")
        try:
            movie_data = msoup.find("table").tbody.children
            for item in movie_data:
                try:
                    if item.th.text == "Box office":
                        box = item.td.text.split("[")[0].strip()
                        box = box.replace(u'\xa0', u' ')
                        new_box = ""
                        for ch in box:
                            if ch not in "$€,":
                                new_box += ch
                        if "million" in new_box.lower():
                            s_box = new_box.split()[0].strip()
                            if "." in s_box:
                                m_box = s_box.split(".")[1]
                                while len(m_box) < 6:
                                    m_box += "0"
                                final_box = int("".join([s_box.split(".")[0], m_box]))
                            else:
                                final_box = int(s_box + ("000000"))
                        elif "billion" in new_box.lower():
                            s_box = new_box.split()[0].strip()
                            if "." in s_box:
                                m_box = s_box.split(".")[1]
                                while len(m_box) < 9:
                                    m_box += "0"
                                final_box = int("".join([s_box.split(".")[0], m_box]))
                            else:
                                final_box = int(s_box + ("000000000"))
                        else:
                            final_box = int(new_box.split()[0].strip())
                        title_year_box.append((title, year, final_box))
                        ticker += 1
                except:
                    continue
        except:
            title_year_box.append((title, year, None))
        if ticker == 20:
            break
    return title_year_box

def setUpDatabase(db_name):
    '''
    This function creates a database using its desired name as input and inserts a BoxInfo table 
    and Names table into that database. The cursor and connection of the database are returned.
    '''
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+ '/' + db_name)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS BoxInfo (id INTEGER PRIMARY KEY, year INTEGER, box INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS Names (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    conn.commit()
    return cur, conn

def addToTable(data, cur, conn):
    '''
    This function adds data into a database table from a list of tuples containing the title,
    release year, and box office gross of movies. It will only add a specified number of entries, and
    it will only add data that has not already been entered. The code first enters an id for the movie
    into the Names table if it is new, and then pulls this idea to be inserted into the BoxInfo table.
    The list of tuples and the cursor and connection of the database are inputs.
    '''
    for title, year, box in data:
        cur.execute("INSERT OR IGNORE INTO Names (name) VALUES (?)", (title, ))
        cur.execute("SELECT id FROM Names WHERE name = ?", (title, ))
        mov_id = cur.fetchone()[0]
        cur.execute("INSERT INTO BoxInfo (id, year, box) VALUES (?, ?, ?)", (mov_id, year, box))
    conn.commit()
    cur.execute("SELECT id FROM BoxInfo")
    print("{} titles in the database.".format(len(cur.fetchall())))
    print("Added {} new entries. Run again to add more.".format(len(data)))


def findPreviousTitles(cur):
    '''
    This function returns a list of titles that have already been added to the database. It accepts
    the database cursor as input.
    '''
    cur.execute("SELECT Names.name FROM Names INNER JOIN BoxInfo ON Names.id = BoxInfo.id")
    titles = []
    for item in cur.fetchall():
        titles.append(item[0])
    return titles

def generateTitlesFile(cur, filename):
    '''
    This function creates a text file of all the valid titles pulled from Wikipedia. This file was
    used for my other group members to reference. The function accepts the database cursor and desired
    filename to write to as inputs.
    '''
    cur.execute("SELECT name FROM Names")
    titles = []
    for item in cur.fetchall():
        titles.append(item[0])
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + filename, "w") as f:
        for title in titles:
            f.write("{}\n".format(title))

def main():
    cur, conn = setUpDatabase("movie_info.db")
    addToTable(generateTitleYearBox(generateTitleYearLinks(findPreviousTitles(cur))), cur, conn)
    generateTitlesFile(cur, "titles.text")
    conn.close()

if __name__ == "__main__":
    main()