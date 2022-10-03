#functions to debug fbo.db

import sqlite3

#initialize fbo.db by creating a new table for each airport in the airports table
#of flight.db
def init_fbo():
    #create a connection to the flights.db
    con = sqlite3.connect('flights.db')
    cur = con.cursor()
    airports = []
    sql = "SELECT code FROM airports"
    for row in cur.execute(sql):
        airports.append(row[0])
    con.close()

    #now connect to the fbo db
    con = sqlite3.connect('fbo.db')
    cur = con.cursor()
    #Now for each airport we previously pulled, we need to create a table in
    #the fbo database
    for airport in airports:
        sql = f"CREATE TABLE '{airport}' ('name' TEXT)"
        cur.execute(sql)
        con.commit()


#Displays a list of the airports that are missing FBO information in the db
def show_empty():
    #create a connection to the flights.db
    con = sqlite3.connect('flights.db')
    cur = con.cursor()
    airports = []
    sql = "SELECT code FROM airports"
    for row in cur.execute(sql):
        airports.append(row[0])
    con.close()

    con = sqlite3.connect('fbo.db')
    cur = con.cursor()
    emptyAirports = []
    for airport in airports:
        sql = f"SELECT * FROM {airport}"
        count = 0
        for row in cur.execute(sql):
            count += 1
        if count == 0:
            emptyAirports.append(airport)
    print(emptyAirports)
    input("Press enter to exit: ")
show_empty()
