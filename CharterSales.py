
import sqlite3
import csv
from random import randint
from Tools import get_num_input
from Tools import refresh_quotes
from Tools import tick
from Tools import blankspace
from Tools import get_distance
from Tools import get_airport_coord
from Tools import airport_distance



#prints a list of flights to the console.  Argument is expected to be a list of flights (dictionaries)
def print_flights(flights):
    count = 0
    for flight in flights:
        #flight is a dictionary with dep, dest, and pax
        count += 1
        dep = flight['dep']
        arr = flight['arr']
        pax = flight['pax']
        #Let's also add the distance at the end.
        dist = round(airport_distance(dep, arr))
        print()
        print(f"{count}: Dep: {dep}  --  Dest: {arr}  -- Pax: {pax} -- Dist: {dist} NM")
    #Adds a go back option to the list of printed flights.
    count += 1
    print()
    print(f"{count}: Go Back")
    print()

#Create a quote and write it to the quotes table.  For now the quote is a simple dollar amount
#But this process can be made more complex in the future.  Argument is the flight the user selected
#as a dictionary object.
def make_quote(flight):
    #Start by printing some blankspace and showing the selected flight:
    blankspace(10)
    print("Selected Flight:")
    dep = flight['dep']
    arr = flight['arr']
    pax = flight['pax']
    print(f"Selected Flight: Dep: {dep}  --  Dest: {arr}  -- Pax: {pax}")
    print()
    price = -1
    while price < 0:
        try:
            price = int(input("Please enter an amount to quote: $"))
        except:
            print("Please enter numbers only, no decimals...")
    blankspace(10)
    print("Quote Summary:")
    print(f"Quote: ${price}  --  Dep: {dep}  --  Dest: {arr}  -- Pax: {pax}")
    ready = input("Ready to send quote? (y/n): ")
    #If user responds with yes (y/Y), writes the quote into the quotes table.
    if ready.lower() =='y':
        #before we write in the quote, we use this point to determine which FBO's will be used at the
        #dep and arr airports.  fbolist is a list object.  Index 0 is dep, index 1 is arr.
        fbolist = get_fbos(flight)
        depfbo = fbolist[0]
        arrfbo = fbolist[1]
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = f"INSERT INTO quotedflights (dep, arr, pax, price, depfbo, arrfbo) VALUES ('{dep}', '{arr}', '{pax}', '{price}', '{depfbo}', '{arrfbo}')"
        cur.execute(sql)
        con.commit()
        blankspace(10)
        print("Quote sent to the customer")
        input("Press Enter to continue: ")

#Prints all quoted flights to the console
def print_quotes():
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = f"SELECT * FROM quotedflights"
    print()
    print("Quoted Flights:")
    for row in cur.execute(sql):
        dep = row[1]
        arr = row[2]
        pax = row[3]
        price = row[4]
        print(f"Dep: {dep} -- Arr: {arr} -- PAX - {pax}  --  Quote: ${price}")
        

#Finds the FBO's at both the departure and arrival airport.
#Argument is expected to be a flight dictionary object
#Returns a list where index 0 is the dep fbo and index 1 is the arr fbo
def get_fbos(flight):
    dep = flight['dep']
    arr = flight['arr']
    #Now let's connect to db and find the fbo's at the dep and arr airport.
    con = sqlite3.connect('data/fbo.db')
    cur = con.cursor()
    sql = f"SELECT * FROM {dep}"
    arrfbos = []
    depfbos = []
    for row in cur.execute(sql):
        depfbos.append(row[0])
    sql = f"SELECT *FROM {arr}"
    for row in cur.execute(sql):
        arrfbos.append(row[0])
    #We need to select random indexes for the arrfbos and depfbos
    arrindex = randint(0, len(arrfbos)-1)
    depindex = randint(0, len(depfbos)-1)
    arrfbo = arrfbos[arrindex]
    depfbo = depfbos[depindex]
    fbolist = [depfbo, arrfbo]
    return fbolist
        


#Asks the user how they would like to filter the avilable flights.
def get_filter_option():
    print("How would you like to view the currently available charter requests?")
    print()
    print("1. By Departure Airport/Area")
    print("2. By Arrival Airport/Area")
    print("3. Show all Quotable Flights")
    print("4. Exit")
    print()
    return get_num_input(1,4)

#Returns list of all available flights from the available quotes table filtered by the user's filtering
#selection  Argument is the filter option from get_filter_option.  Returns a list of flight dictionaries.
def get_flights(filterOption):
    #connect to db first
    flights = []
    availableQuotes = []
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = ''
    
    #Let's start by getting all of our available quotes and adding them to a list for us to check.
    sql = "SELECT * FROM availablequotes"
    for row in cur.execute(sql):
        flight = {
            'dep':row[0],
            'arr':row[1],
            'pax':row[2]
            }
        availableQuotes.append(flight)
    
    #The SQL statement is going to depend on the user's input to the filtering option.
    #Filter option 1  - filter by departure airport/area
    if filterOption == 1:
        userAirport = ''
        userLat = -1.1
        userLong = -1.1

        #Ask user for the departure airport.  While loop checks against the airports csv file to ensure a valid airport
        #was entered.
        while True:
            userAirport = input("Please enter the departure airport to filter by: ")
            airportCoord = get_airport_coord(userAirport)
            #Checks against index 0 of returned list to see if the airport was found.
            if airportCoord[0]:
                userLat = float(airportCoord[1])
                userLong = float(airportCoord[2])
                break
            else:
                print("Airport not found, please try again...")
                print()

        dist = 0
        #Start looping until user enters a valid number
        while True:
            try:
                dist = int(input("Please enter a distance to filter by: "))
                break
            except:
                print("Please enter a whole number only...")
                print()
        #Now that we have our departure airport and distance to check by, we need to check each quote to see if
        #the departure airport is within a user specified number of miles from the user specified airport.
        for quote in availableQuotes:
            #If the user airport is within dist specified miles of of the airport we are checking, this flight
            #should be added to the flights list.
            #First we need to get the coordinates of the quotes departure airport
            dep = quote['dep']
            sql = f"SELECT lat, long FROM airports WHERE code = '{dep}'"
            res = cur.execute(sql)
            coordlist = res.fetchone()
            quoteLat = coordlist[0]
            quoteLong = coordlist[1]
            if get_distance(userLat, userLong, quoteLat, quoteLong) < dist:
                flights.append(quote)
        return flights
                     
    #If Filter option 2 - filter by the arrival airport/area
    if filterOption == 2:
        userAirport = ''
        userLat = -1.1
        userLong = -1.1

        #Ask user for the departure airport.  While loop checks against the airports csv file to ensure a valid airport
        #was entered.
        while True:
            userAirport = input("Please enter the arrival airport to filter by: ")
            airportCoord = get_airport_coord(userAirport)
            #Checks against index 0 of returned list to see if the airport was found.
            if airportCoord[0]:
                userLat = float(airportCoord[1])
                userLong = float(airportCoord[2])
                break
            else:
                print("Airport not found, please try again...")
                print()

        dist = 0
        #Start looping until user enters a valid number
        while True:
            try:
                dist = int(input("Please enter a distance to filter by: "))
                break
            except:
                print("Please enter a whole number only...")
                print()
        #Now that we have our departure airport and distance to check by, we need to check each quote to see if
        #the departure airport is within a user specified number of miles from the user specified airport.
        for quote in availableQuotes:
            #If the user airport is within dist specified miles of of the airport we are checking, this flight
            #should be added to the flights list.
            #First we need to get the coordinates of the quotes departure airport
            arr = quote['arr']
            sql = f"SELECT lat, long FROM airports WHERE code = '{arr}'"
            res = cur.execute(sql)
            coordlist = res.fetchone()
            quoteLat = coordlist[0]
            quoteLong = coordlist[1]
            if get_distance(userLat, userLong, quoteLat, quoteLong) < dist:
                flights.append(quote)
        return flights

    #If Filter Option 3 - show all flights that are currently quoteable.
    if filterOption == 3:
        return availableQuotes
                 

##### MAIN FUNCTION BELOW
def main():
    #Next ask if you would like to make your aircraft available for quote requests, and which region
    #you are advertising departure out of

    #Start of the make quotes loop
    while True:
        #Before selecting a filter option, print a list of all quoted trips.
        print_quotes()
        print()
        print()
        filterOption = get_filter_option()
        #If exit selected, break from the loop.
        if filterOption == 4:
            break
        flights = get_flights(filterOption)
        print("Please Select a flight to quote: ")
        print_flights(flights)
        #Adding a go back option so that the user isn't forced to select a quote
        goBackOption = len(flights) + 1
        makeQuoteOption = get_num_input(1, len(flights) + 1)
        print()
        #Should only make a quote if the makeQuoteOption doesn't equal goBackOption
        if makeQuoteOption != goBackOption:
            make_quote(flights[makeQuoteOption - 1])
