import requests
import sqlite3
import json
import ssl
import os
import math
from scipy import stats

from sklearn.linear_model import LinearRegression #import batch for regression
import numpy
import pandas
import plotly.express as px
import plotly.graph_objects as go
import plotly.graph_objects as go




API_KEY = 'QD2RMJA4DDU480V3'
r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=DIA&apikey=' + API_KEY)

    

result = r.json()
dataForAllMonths = result['Monthly Time Series']
#got all months data pulled'''

#setting up db
path = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(path + '/' + "movie_info.db")
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Stock (Date NUMERIC, Price NUMERIC)''')


cur.execute('select * from Stock;')
numrows = len(cur.fetchall())
start_count = numrows
end_count = numrows + 19

count = 0
for key in dataForAllMonths.keys():
    if (count >= start_count and count <= end_count):

        price = float(dataForAllMonths[key]['4. close'])
        #print(key)
        date = str(key)
        #stronk = "INSERT INTO Stock (Date, Price) VALUES (" + str(date) + ", " + str(price) + ")"
        cur.execute('''INSERT INTO Stock (Date, Price) VALUES (?, ?)''', (str(date)[:4], str(price)))
    count += 1
    
conn.commit()
cur.close()