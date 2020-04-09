from bs4 import BeautifulSoup
import requests
import os
import sqlite3

def generateTitleYearLinks():
    wiki_page = requests.get("https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films")
    soup = BeautifulSoup(wiki_page.text, "html.parser")
    movies=soup.find_all("tr") #look for each movie in the table
    movie_info = [] #get a title, year, and link to the wikipedia page for each movie in the table
    for item in movies:
        try:
            new_item = item.td.next_sibling.next_sibling
            year = int(new_item.a.text)
            if year >= 2000:
                title = item.td.i.a["title"]
                if "film)" in title:
                    title = title.split("(")[0].strip()
                link = "https://en.wikipedia.org" + item.td.i.a["href"]
                movie_info.append((title, year, link))   
        except:
            continue
    return movie_info

def generateTitleYearBox(movie_info):
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
                except:
                    continue
        except:
            title_year_box.append((title, year, None))
    return title_year_box

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+ '/' + db_name)
    cur = conn.cursor()
    return cur, conn

def generateTable(title_year_box, cur, conn):
    cur.execute("DROP TABLE IF EXISTS BoxInfo")
    cur.execute("CREATE TABLE BoxInfo (title TEXT PRIMARY KEY, year INTEGER, box INTEGER)")
    for title, year, box in title_year_box:
        cur.execute("INSERT INTO BoxInfo (title, year, box) VALUES (?, ?, ?)", (title, year, box))
    conn.commit()

def createCSV(file_name, title_year_box):
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + file_name, "w") as f:
        f.write("Title,Year,Box Office Gross\n")
        for title, year, box in title_year_box:
            f.write("{},{},{}\n".format(title, year, box))

def generateTitlesFile(file_name, title_year_box):
    with open(os.path.dirname(os.path.abspath(__file__)) + "/" + file_name, "w") as m:
        for movie in title_year_box:
            m.write("{}\n".format(movie[0]))

def main():
    title_year_links = generateTitleYearLinks()
    title_year_box = generateTitleYearBox(title_year_links)
    cur, conn = setUpDatabase("movie_info.db")
    generateTable(title_year_box, cur, conn)
    #createCSV("title_year_box.csv", title_year_box)
    #generateTitlesFile("movie_titles.text", title_year_box)

if __name__ == "__main__":
    main()
    