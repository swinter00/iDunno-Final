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



def movie_box_rating_zip(cur):
    '''
    This function returns a list of tuples containing movie data where the first item is that movie's
    IMDB rating and the second item is that movie's box office gross. The cursor of the database is used
    as an input.
    '''
    cur.execute("SELECT Movies.Rating, BoxInfo.box FROM BoxInfo INNER JOIN Movies ON BoxInfo.id = Movies.id")
    return [(float(rating), float(box)) for rating, box in cur.fetchall() if rating != 'N/A']

def movie_box_runtime_zip(cur):
    '''
    This function returns a list of tuples containing movie data where the first item is that movie's
    runtime and the second item is that movie's box office gross. The cursor of the database is used
    as an input.
    '''
    cur.execute("SELECT Runtimes.Runtimes, BoxInfo.box FROM BoxInfo INNER JOIN Runtimes ON BoxInfo.id = Runtimes.id")
    return [(float(runtime.split()[0]), float(box)) for runtime, box in cur.fetchall() if runtime != 'N/A']

def calc_year_box_averages(cur):
    '''
    This function calculates the average box office gross for every year included in a data base. The
    cursor for the database is inputted and a tuple containing each year and its average box office
    gross is returned.
    '''
    cur.execute("SELECT year FROM BoxInfo")
    years = []
    for item in cur.fetchall():
        if item[0] not in years:
            years.append(int(item[0]))
    year_averages = []
    for year in years:
        cur.execute("SELECT box FROM BoxInfo WHERE year = ?", (year, ))
        totals = [float(item[0]) for item in cur.fetchall()]
        average = sum(totals) / len(totals)
        year_averages.append((year, average))
    return year_averages

def calc_year_stocks_averages(cur):
    '''
    This function calculates the average DJIA end of day price average for every year included in a data base. The
    cursor for the database is inputted and a tuple containing each year and its average box office
    gross is returned.
    '''
    year_averages = []
  
    years = []
    i = 20
    base = 2000
    while i >= 0:
        years.append(str(base + i))
        i-=1
    
    for year in years:
        cur.execute("SELECT Price FROM Stock WHERE Date = ?", (year, ))
        totals = [float(item[0]) for item in cur.fetchall()]
        average = sum(totals) / len(totals)
        year_averages.append((int(year), average))

    return year_averages

def zip_by_year(year_data_tup_x, year_data_tup_y):
    '''
    This function accepts two lists of tuples formatted as (year, value) and returns a list of tuples
    where the values of each tuple are combined based on corresponding year, with the first inputted
    list as the x value and the second as the y value.
    '''
    data_tups = []
    for year, value in year_data_tup_x:
        for year1, value1 in year_data_tup_y:
            if year == year1:
                data_tups.append((value, value1))
    return data_tups

def calc_data_dict(point_tuples, relationship_string):
    '''
    This function performs statistical analysis with inputs of a list of tuples with x, y point values
    and a string describing the relationship of those points. It finds the line of best fit, r, r^2,
    and the description of the correlation before returning this information in a dictionary that also
    documents the relationships between the points.
    '''
    data_dict = {}
    data_dict["Relationship"] = relationship_string
    x_values = numpy.array([x for x, y in point_tuples])
    y_values = numpy.array([y for x, y in point_tuples])
    
    m, b, r, p, std_err = stats.linregress(x_values, y_values)
    data_dict["Line of best fit"] = "{} + {}x".format(b, m)

    #calculating r
    data_dict["r"] = r

    #calculating r^2
    data_dict["r^2"] = r * r

    #determining correlation
    if r == 0:
        data_dict["Correlation"] = "No correlation"
    else:
        if r < 0:
            direction = "Negative"
        if r > 0:
            direction = "Positive"
        if abs(r) >= .8:
            strength = "Very strong"
        elif abs(r) >= .65:
            strength = "Strong"
        elif abs(r) >= .5:
            strength = "Moderate"
        elif abs(r) >= .35:
            strength = "Weak"
        elif abs(r) >= .2:
            strength = "Very weak"
        else:
            strength = "Almost nonexistent"
        data_dict["Correlation"] = "{}, {}".format(strength, direction)

    return data_dict

def create_scatter_visualization(point_tuples, x_label, y_label):
    '''
    This function creates and displays scatter-plot visualization with the line of best fit displayed. 
    A list of tuples of points, a label for the x axis, and a label for the y axis are used as inputs.
    '''
    x_values = [x for x, y in point_tuples]
    y_values = [y for x, y in point_tuples]
    df = pandas.DataFrame({'X': x_values, 'Y':y_values})

    reg = LinearRegression().fit(numpy.vstack(df['X']), y_values)
    df['bestfit'] = reg.predict(numpy.vstack(df['X']))

    # plotly figure setup
    fig=go.Figure()
    fig.add_trace(go.Scatter(name= (str(x_label) + " vs " + str(y_label)), x=df['X'], y=df['Y'].values, mode='markers'))
    fig.add_trace(go.Scatter(name='line of best fit', x=x_values, y=df['bestfit'], mode='lines'))
    fig.update_layout(xaxis_title = x_label, yaxis_title = y_label)
    
    fig.show()

def outlier_filter(point_tuples, eloquent=False):
    '''
    This function accepts a list of points arranged in tuples and a boolean value for 
    eloquent. It checks for and removes outliers before returning a list of all points that does 
    not contain the outliers. If eloquent is True, the number of points removed will be printed.
    '''
    y_vals = numpy.array([y for x, y in point_tuples])
    x_vals = numpy.array([x for x, y in point_tuples])
    median_y = numpy.median(y_vals)
    median_x = numpy.median(x_vals)
    first_quartile_y = numpy.quantile(y_vals, .15)
    third_quartile_y = numpy.quantile(y_vals, .85)
    first_quartile_x = numpy.quantile(x_vals, .15)
    third_quartile_x = numpy.quantile(x_vals, .85)
    iqr_x = third_quartile_x - first_quartile_x
    iqr_y = third_quartile_y - first_quartile_y
    lower_bound_x = first_quartile_x - (iqr_x*1.5)
    upper_bound_x = third_quartile_x + (iqr_x*1.5)
    lower_bound_y = first_quartile_y - (iqr_y*1.5)
    upper_bound_y = third_quartile_y + (iqr_y*1.5)

    ticker = 0
    no_outliers = []
    for x, y in point_tuples:
        if x >= lower_bound_x and x <= upper_bound_x and y >= lower_bound_y and y <= upper_bound_y:
            no_outliers.append((x, y))
        else:
            ticker += 1

    if eloquent:
        print("Removed {} points.".format(ticker))
    return no_outliers

def calc_year_rating_averages(cur):
    '''
    This function calculates the average movie rating for every year included in a data base. The
    cursor for the database is inputted and a tuple containing each year and its average movie
    rating is returned.
    '''
    cur.execute("SELECT year FROM Movies")
    years = []
    for item in cur.fetchall():
        if item[0] not in years:
            if int(item[0]) >= 2000:
                years.append(int(item[0]))
    year_averages = []
    for year in years:
        cur.execute("SELECT Rating FROM Movies WHERE year = ?", (year, ))
        totals = [float(item[0]) for item in cur.fetchall() if item[0] != 'N/A']
        average = sum(totals) / len(totals)
        year_averages.append((year, average))
    return year_averages

def calc_year_runtime_averages(cur):
    '''
    This function calculates the average movie runtime for every year included in a data base. The
    cursor for the database is inputted and a tuple containing each year and its average movie
    runtime is returned.
    '''
    cur.execute("SELECT Movies.Year FROM Runtimes INNER JOIN Movies ON Movies.id = Runtimes.id")
    years = []
    for item in cur.fetchall():
        if item[0] not in years:
            if int(item[0]) >= 2000:
                years.append(int(item[0]))
    year_averages = []
    for year in years:
        cur.execute("SELECT Runtimes.Runtimes FROM Runtimes INNER JOIN Movies ON Movies.id = Runtimes.id WHERE Movies.Year = ?", (year, ))
        totals = [float(item[0].split()[0]) for item in cur.fetchall() if item[0] != 'N/A']
        average = sum(totals) / len(totals)
        year_averages.append((year, average))
    return year_averages

def main():
    

    #setting up db
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + '/' + "movie_info.db")
    cur = conn.cursor()
                
    
    year_box = calc_year_box_averages(cur) 
    year_ratings = calc_year_rating_averages(cur)
    year_runtimes = calc_year_runtime_averages(cur)
    year_stocks = calc_year_stocks_averages(cur)
    conn.commit()

    
    data_dicts = []
    #compare average stock market performance and box office gross by year
    stocks_box = (zip_by_year(year_stocks, year_box))
    data_dicts.append(calc_data_dict(stocks_box, "Dow Jones Industrial Average by year (dollars) vs. average box office gross by year (dollars)"))
    
    #compare average ratings and box office gross by individual movie
    ratings_box = outlier_filter((movie_box_rating_zip(cur)))
    data_dicts.append(calc_data_dict(ratings_box, "Individual movie ratings (out of 10) vs. box office gross per individual movie (dollars)"))

    #compare average runtime and box office gross by individual movie
    runtime_box = outlier_filter((movie_box_runtime_zip(cur)))
    data_dicts.append(calc_data_dict(runtime_box, "Individual movie runtime (minutes) vs. box office gross per individual movie (dollars)"))

    #compare average stock market performance and movie rating per year
    stocks_ratings = (zip_by_year(year_stocks, year_ratings))
    data_dicts.append(calc_data_dict(stocks_ratings, "Dow Jones Industrial Average by year (dollars) vs. Average yearly movie ratings (out of 10)"))

    #compare average stock market performance and movie runtime per year
    stocks_runtime = (zip_by_year(year_stocks, year_runtimes))
    data_dicts.append(calc_data_dict(stocks_runtime, "Dow Jones Industrial Average by year (dollars) vs. Average movie runtime by year (minutes)"))

    #compare avg box office to avg ratings
    box_ratings = outlier_filter((zip_by_year(year_box, year_ratings)))
    data_dicts.append(calc_data_dict(box_ratings, "Average box office gross by year (dollars) vs. Average Movie ratings (out of 10)"))
   
    #avg runtime vs avg box
    runtime_box = outlier_filter((zip_by_year(year_runtimes, year_box)))
    data_dicts.append(calc_data_dict(runtime_box, "Average movie runtime by year (minutes) vs. Average box office gross by year (dollars)"))



    with open(os.path.dirname(os.path.abspath(__file__)) + "/data_analysis.text", "w") as f:
        f.write("Analysis on Academy-Award Winning films box office gross, ratings, runtime, and US stock market performance for the 2000s\n\n")

        f.write("Average box office gross, movie rating, runtime, and stock market price per year:\n")
        for i in range(len(year_box)):
            f.write("Year: {}\n".format(year_box[i][0]))
            f.write("Average box office gross: ${}\n".format(year_box[i][1]))
            f.write("Average movie rating out of 10: {} on IMDB\n".format(year_ratings[i][1]))
            f.write("Average movie runtime: {} minutes\n".format(year_runtimes[i][1]))
            f.write("Average stock market price: ${}\n\n".format(year_stocks[i][1]))

        f.write("Correlation data:\n")
        for d in data_dicts:
            f.write("Relationship: {}\n".format(d["Relationship"]))
            f.write("Line of best fit: {}\n".format(d["Line of best fit"]))
            f.write("r value: {}\n".format(d["r"]))
            f.write("r^2 value: {}\n".format(d["r^2"]))
            f.write("Correlation: {}\n\n".format(d["Correlation"]))

    create_scatter_visualization(ratings_box, "Individual Movie ratings (out of 10)", "Individual movie box office returns (dollars)") #ratingsbox
    create_scatter_visualization(stocks_box, "Dow Jones Industrial Average by year (dollars)", "Average box office returns of movies by year (dollars)") #stocksbox
    create_scatter_visualization(runtime_box, "Individual movie runtime (minutes)", "Individual box office returns of movies (dollars)") #runtimebox
    create_scatter_visualization(stocks_ratings, "Dow Jones Industrial Average by year (dollars)", "Average movie ratings by year (out of 10)")
    create_scatter_visualization(stocks_runtime, "Dow Jones Industrial Average by year (dollars)", "Average movie runtime by year (minutes)")
    create_scatter_visualization(box_ratings, "Average box office returns of movies by year (dollars)", "Average movie ratings by year (out of 10)")
    create_scatter_visualization(runtime_box, "Average movie runtime by year (minutes)", "Average box office gross by year (dollars)")

if __name__ == "__main__":
    main()
