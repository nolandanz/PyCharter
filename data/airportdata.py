import sqlite3
import csv

def get_airport_coord(airport):
    #CSV file needs a leading K in front of all airports (even non-ICAO.... silly...)
    #We need to modify dep to have a leading K if it's length is less than 4 characters
    lat = -1.1
    long = -1.1
    found = False
    if len(airport) < 4:
        airport = 'K'+airport
    airport = airport.upper()

    #Let's open the CSV file:
    with open('airports.csv', 'r', encoding = 'utf-8') as file:
        csvreader = csv.reader(file)
        #Loop through CSV to find airport
        for row in csvreader:
            if row[1] == airport:
                lat = row[4]
                long = row[5]
                found = True
    latlong = [found, lat, long]
    return latlong

def write_coords():
    #Pull list of all airports, and then update each airport
    #to write in coords.
    con = sqlite3.connect('flights.db')
    cur = con.cursor()
    sql = "SELECT * FROM airports"
    allAirports = []
    for row in cur.execute(sql):
        allAirports.append(row[0])
    for airport in allAirports:
        coords = get_airport_coord(airport)
        lat = coords[1]
        long = coords[2]
        sql = f"UPDATE airports SET lat = {lat}, long = {long} WHERE code = '{airport}'"
        cur.execute(sql)
    con.commit()        
