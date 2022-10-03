#Various Tools used throughout the program

import sqlite3
import math
import csv
from random import randint


#tick function - simulates one iteration of time.
#First answers quotes from previous turn
#Next refreshes the quotes table

def tick():
    if randint(1,4) == 3:
        hot_quote()
    answer_quotes()
    refresh_quotes()

#Returns string of a random fbo at the argument supplied airport
def get_fbo(airport):
    con = sqlite3.connect('data/fbo.db')
    cur = con.cursor()
    sql = f"SELECT * FROM {airport}"
    fboList = []
    for row in cur.execute(sql):
        fboList.append(row[0])
    index = randint(0, len(fboList)-1)
    fbo = fboList[index]
    return fbo

#Simulates a hot quote being requested (someone calling for an
#urgent round trip flight 
def hot_quote():
    blankspace(10)
    #We need to get a random aircraft from our list, a random airport within 50 miles of it, and a random destination
    #within the number of miles set for maximum quotes.
    con = sqlite3.connect('data/aircraft.db')
    cur = con.cursor()
    sql = "SELECT * FROM aircraft"
    allAircraft = []
    for row in cur.execute(sql):
        allAircraft.append(row[0])
    randomAircraft = randint(0, len(allAircraft)-1)
    aircraft = allAircraft[randomAircraft]
    sql = f"SELECT home FROM aircraft WHERE tail = '{aircraft}'"
    res = cur.execute(sql)
    home = res.fetchone()[0]

    con.close()
    allAirports = []
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT code FROM airports"
    for row in cur.execute(sql):
        allAirports.append(row[0])

    #Let's find a possible departure airport within 200 miles of aircraft homebase
    #25% chance that the dep airport will be the aircrafts home airport
    dep = ''
    if randint(1, 4) == 1:
        dep = home
    else:
        possibleDeps = []
        for airport in allAirports:
            if airport_distance(home, airport) < 200:
                possibleDeps.append(airport)
        dep = possibleDeps[randint(0, len(possibleDeps)-1)]

    #Now let's find a list of arrival airports within min and max quote number of miles from the dep.
    #First let's get the saved quotemaxdist
    con.close()
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT num FROM settings WHERE name = 'quotemaxdist'"
    res = cur.execute(sql)
    maxDist = res.fetchone()[0]
    sql = "SELECT num FROM settings WHERE name = 'quotemindist'"
    res = cur.execute(sql)
    minDist = res.fetchone()[0]

    #Now let's build a list of possible arrival airports
    possibleArrs = []
    for airport in allAirports:
        dist = airport_distance(dep, airport)
        if dist > minDist and dist < maxDist:
            possibleArrs.append(airport)
    
    arr = possibleArrs[randint(0, len(possibleArrs)-1)]
    
    print("RING RING.... RING RING")
    input("Press Enter to continue: ")
    print()
    print(f"Hello!  Is {aircraft} available for a round trip flight from {dep} to {arr}?")
    choice = input("(y/n): ")
    if choice.lower() == 'y':
        #Let's grab some FBO data
        depfbo = get_fbo(dep)
        arrfbo = get_fbo(arr)
        pax = randint(1, 11)
        print()
        print(f"Great!  We'd like to use {depfbo} in {dep}")
        print(f"and {arrfbo} in {arr}.  We have {pax} passengers")
        print()
        print("What kind of price can you give me on this trip?")
        print()
        price = input("Please enter price for this quote: $ ")
        #We don't do any calcs at this point to see how close to good the price is, so it's just a random chance, we'll say 1 in 2
        print()
        print()
        print("Thanks, we'll be in touch!  Have a fantastic day!")
        input("Press Enter to continue: ")
        print()
        print()
        print("*twiddling thumbs*.... *twiddling thumbs*...")
        input("Press Enter to continue: ")
        print()
        print()
        if randint(1,2) == 1:
            #Time to write this quote into the bookedquotes table
            print("Good news everyone!  This trip was accepted.  Would you like to book it?")
            bookChoice = input("(y/n): ")
            if bookChoice.lower() == 'y':
                #We need to get fbo data for this trip
                sql = "INSERT INTO bookedquotes (dep, arr, pax, price, depfbo, arrfbo)"
                sql=sql+f" VALUES('{dep}', '{arr}', {pax}, {price}, '{depfbo}', '{arrfbo}')"
                cur.execute(sql)
                con.commit()
                sql2 = "INSERT INTO bookedquotes (dep, arr, pax, price, depfbo, arrfbo)"
                sql2=sql2+f" VALUES('{arr}', '{dep}', {pax}, {price}, '{arrfbo}', '{depfbo}')"
                cur.execute(sql2)
                con.commit()
                print()
                print("Flights written into booked quotes list")
                input("Press Enter to continue: ")


                
        else:
            print("It looks like the client didn't book this quote.  Better luck next time")
            input("Press Enter to continue: ")
    else:
        print()
        print("Oh well, thanks for taking my call!  Have a good day!")
        input("Press Enter to continue: ")
    
#Answers quotes from the previous turn
def answer_quotes():
    #Let's start by fetching all of the previous quotes.
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT * FROM quotedflights"
    quotes = []
    for row in cur.execute(sql):
        #Sets the random chance a flight will be selected and put into the quotes list.
        if randint(1, 2) == 1:
            flight = {
                'dep':row[1],
                'arr':row[2],
                'pax':row[3],
                'price':row[4],
                'depfbo':row[5],
                'arrfbo':row[6]
                }
            quotes.append(flight)
    #We now have a list of quotes that were accepted (the quotes list).
    if len(quotes) > 0:
        blankspace(10)
        print("One or more of your quotes were accepted!")
        input("Press Enter to continue: ")
        #Since we have accepted quotes, we need to start a While loop displaying all of the quotes and asking the user
        #which quote they want to push to the schedule.
        while len(quotes) > 0:
            blankspace(10)
            #Print each quote in the quotes list
            count = 1
            for flight in quotes:
                dep = flight['dep']
                arr = flight['arr']
                pax = flight['pax']
                price = flight['price']
                depfbo = flight['depfbo']
                arrfbo = flight['arrfbo']
                dist = round(airport_distance(dep, arr))
                print(f"{count}: Quote: ${price} -- Dep: {dep} -- Arr: {arr} -- Pax: {pax} -- Dist: {dist} NM")
                print()
                print(f"Departure FBO: {depfbo} -- Arrival FBO: {arrfbo}")
                print()
                print("-------------------------------------------------")
                print()
                count += 1
            print(f"{count}: Exit")
            print()
            #Ask user which trip they would like to move to the schedule
            print(f"Enter a selection number from above, or enter {count} to Exit")
            print()
            selection = get_num_input(1, len(quotes)+1)
            if selection == len(quotes)+1:
                #confirm the user is ready to exit
                print()
                print()
                print("Any quotes not pushed to the schedule will be lost")
                confirm = input("Are you sure you want to continue? (y/n): ")
                if confirm.lower() == 'y':
                    break
            #The else case indicates the user selected a flight.  Let's get this flights info and confirm they
            #want to add it to the schedule.
            else:
                flight = quotes[selection-1]
                dep = flight['dep']
                arr = flight['arr']
                pax = flight['pax']
                price = flight['price']
                depfbo = flight['depfbo']
                arrfbo = flight['arrfbo']
                blankspace(10)
                print("Selected Flight:")
                print()
                print(f"Dep: {dep} -- Arr: {arr} -- Pax: {pax} -- Quote: ${price}")
                print()
                print(f"Departure FBO: {depfbo} -- Arrival FBO: {arrfbo}")
                print()
                print()
                confirm = input("Are you sure you want to push this flight to the schedule? (y/n): ")
                if confirm.lower() == 'y':
                    #Time to write the flight to the bookedquotes table
                    sql = f"INSERT INTO bookedquotes ('dep', 'arr', 'pax', 'price', 'depfbo', 'arrfbo') VALUES ('{dep}', '{arr}', '{pax}', '{price}', '{depfbo}', '{arrfbo}')"
                    cur.execute(sql)
                    con.commit()
                    #Now we need to remove this flight from quotes list.
                    quotes.remove(flight)
                    print("Quote pushed to schedule.")
                    input("Press Enter to continue: ")
            if len(quotes) == 0:
                blankspace(10)
                print("All accepted quotes have been pushed")
                input("Press Enter to continue: ")


    else:
        blankspace(10)
        print("You have no new messages...")
        input("Press Enter to continue: ")

    #At this point we need to remove all data from the quoted flights table
    sql = "DELETE from quotedflights"
    cur.execute(sql)
    con.commit()
    



#refresh quotes - removes data from the availablequotes table and regenerates
#a new list of 100 quotable trips.  Quotable trips consist of a random departure
#airport, and random arrival airport (with a minimum
#calculatd distance of 50 miles between them) and a random number of pax (between 1 and 11)
#The max number of pax and minimum distance should be customizeable in the future.
def refresh_quotes():
    #first connect to db
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    #next lets remove all data from the availablequotes table
    sql = "DELETE FROM availablequotes"
    cur.execute(sql)
    con.commit()
    #Let's fetch a list of all airports registered in the DB, and them to the list allAirports.
    #each airport in allAirports should be a dictionary object with it's code, lat, and long.
    allAirports = []
    sql = "SELECT * from airports"
    for row in cur.execute(sql):
        airport = {
            'code':row[0],
            'lat':row[1],
            'long':row[2]
            }
        allAirports.append(airport)
    #allAirports now mirrors the airports table in the db.  Next we can select two random airports
    #in the allAirports list, make sure their distance is less than X minimum distance, and if it is
    #write the flight into the availablequotes table of the db.
    #Let's iterate through 100 times (create 100 flights), this should be user specified in the future.
    count = 0
    while count < 200:
        #grabs random departure and arrival airport indexes
        depIndex = randint(0, len(allAirports)-1)
        arrIndex = randint(0, len(allAirports)-1)
        #now let's cast dep and arr so that they become dictionaries of dep and arr airport
        dep = allAirports[depIndex]
        arr = allAirports[arrIndex]
        depCode = dep['code']
        arrCode = arr['code']
        depLat = dep['lat']
        depLong = dep['long']
        arrLat = arr['lat']
        arrLong = arr['long']
        #Generates a random number of pax from 1 to 11
        pax = randint(1, 11)
        #If the distance between them is more than X minimum distance, the flight should be written
        #to the availablequotes table.
        charterMin = get_charter_min()
        charterMax = get_charter_max()
        distance = get_distance(depLat, depLong, arrLat, arrLong)
        if distance >= charterMin and distance <= charterMax:
            sql = f"INSERT INTO availablequotes VALUES ('{depCode}', '{arrCode}', '{pax}')"
            cur.execute(sql)
            count += 1
    con.commit()

def get_charter_min():
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT num FROM settings WHERE name = 'quotemindist'"
    res = cur.execute(sql)
    charterMin = res.fetchone()[0]
    return charterMin

def get_charter_max():
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT num FROM settings WHERE name = 'quotemaxdist'"
    res = cur.execute(sql)
    charterMax = res.fetchone()[0]
    return charterMax


#Gets a user input and ensures that it is between the range specified in
#the arguments
def get_num_input(minimum, maximum):
    while True:
        try:
            user = int(input('Please select one of the above options: '))
            if user <= maximum and user >= minimum:
                return user
            else:
                print('Selection out of range...')
        except:
            print('Invalid selection, please enter numbers only')
            print()

#Print x lines of blankspace.  Argument is number of blank lines to print
def blankspace(x):
    for i in range(x):
        print()


#converts distance from degrees and decimal to nautical miles.
#returns the distance in nautical miles.
def get_distance(lat1, lon1, lat2, lon2):
    R = 3443.9185
 
    # Our formula requires we convert all degrees to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
 
    lat_span = lat1 - lat2
    lon_span = lon1 - lon2
 
    a = math.sin(lat_span / 2) ** 2
    b = math.cos(lat1)
    c = math.cos(lat2)
    d = math.sin(lon_span / 2) ** 2
 
    dist = 2 * R * math.asin(math.sqrt(a + b * c * d))
 
    return dist

#Returns the distance between two airports (expected to be string objects)
def airport_distance(airportOne, airportTwo):
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    #Let's fetch the lat and long for airport one and two
    sql = f"SELECT lat FROM airports WHERE code = '{airportOne}'"
    res = cur.execute(sql)
    airportOneLat = res.fetchone()[0]
    sql = f"SELECT long FROM airports WHERE code = '{airportOne}'"
    res = cur.execute(sql)
    airportOneLong = res.fetchone()[0]
    sql = f"SELECT lat FROM airports WHERE code = '{airportTwo}'"
    res = cur.execute(sql)
    airportTwoLat = res.fetchone()[0]
    sql = f"SELECT long FROM airports WHERE code = '{airportTwo}'"
    res = cur.execute(sql)
    airportTwoLong = res.fetchone()[0]
    return get_distance(airportOneLat, airportOneLong, airportTwoLat, airportTwoLong)

#Returns the latitude and longitude of an airport searching through the airports csv file.
#Takes an argument of a string (can be 3 letter or 4 letter code).
#Returns list of 0 - True/False whether airport was found, 1 - lat, 2 - long.
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
    with open('data/airports.csv', 'r', encoding = 'utf-8') as file:
        csvreader = csv.reader(file)
        #Loop through CSV to find airport
        for row in csvreader:
            if row[1] == airport:
                lat = row[4]
                long = row[5]
                found = True
    latlong = [found, lat, long]
    return latlong

#Nolan's Functions
def getFuel():
    print("Enter fuel remaining in pounds: ")
    fuel = input()
    return fuel

