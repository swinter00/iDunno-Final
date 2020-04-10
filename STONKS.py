import requests
import sqlite3
import json
import ssl

API_KEY = 'QD2RMJA4DDU480V3'
r = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=DIA&apikey=' + API_KEY)
"""" "if (r.status_code == 200):
  print r.json()"""


result = r.json()
dataForAllMonths = result['Monthly Time Series']
#got all months data pulled

#setting up db
conn = sqlite3.connect('/Users/user/Desktop/STONKdb.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS Month (Date TEXT, Price NUMERIC)''')

#were gonna do per year
#dataForSingleDate = dataForAllMonths['2017-10-30']

#print(dataForAllMonths[0])
count = 0
for key in dataForAllMonths.keys():
    count += 1
    if count == 121:
        break
    price = float(dataForAllMonths[key]['4. close'])
    print(key)
    date = str(key)
    stronk = "INSERT INTO Month (Date, Price) VALUES (" + str(date) + ", " + str(price) + ")"
    cur.execute(stronk)
    

conn.commit()
cur.close()
'''i = 0
while i < 100:
 //   cur.execute(INSERT INTO Month (Date, Price) VALUES ())
'''

'''
print dataForSingleDate['1. open']
print dataForSingleDate['2. high']
print dataForSingleDate['3. low']
print dataForSingleDate['4. close']
print dataForSingleDate['5. volume']'''