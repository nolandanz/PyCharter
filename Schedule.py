import sqlite3
from Tools import get_num_input
from Tools import blankspace
from Tools import get_airport_coord
from Tools import airport_distance
from Settings import airport_in_database
from Settings import add_airport

#Scheduling functions

#prints a list of booked quotes
def print_booked_quotes():
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT * FROM bookedquotes"
    for row in cur.execute(sql):
        print(row)

def get_all_aircraft():
    #Returns a list of all aircraft tail numbers.
    aircraft = []
    con = sqlite3.connect('data/aircraft.db')
    cur = con.cursor()
    sql = "SELECT tail FROM aircraft WHERE isactive = 1"
    for row in cur.execute(sql):
        aircraft.append(row[0])
    return aircraft

#Asks the user to enter an airport and verifies the airport exists in the flights database
#Argument is a string specifying the departure or arrival airport (should be either departure or arrival
def select_airport(deporarr):
    #Starts with a while loop to validate input
    airport = ''
    while True:
        airport = input(f"Please enter the {deporarr} airport code: ")
        airport = airport.upper()
        #If more than 3 letters and first letter a K, K should be dropped
        if len(airport) > 3 and airport[0] == 'K':
            airport = airport.replace('K', '', 1)
        #Now let's validate the input using the airport_in_database function
        #from settings
        if airport_in_database(airport):
            return airport
        elif get_airport_coord(airport)[0]:
            #If airport not found in the db, let's check if it's in the csv file.
            #Then let's ask the user if they would like to add it.
            print()
            print()
            print(f"Airport ID {airport} not yet added to airport coverage area.")
            selection = input("Would you like to add it? (y/n): ")
            if selection.lower() == 'y':
                #Let's add the airport to the database using the functions we've already created in the
                #Settings module.
                 added = add_airport(airport)
                 if added:
                    #Airport should now exist in the database, so we can break the loop here and still
                    #return the airport
                    return airport
        else:
            print()
            print()
            print("Airport not found/does not exist")
            input("Press Enter to continue: ")
            
#Returns a list of active trips, argument is the string for a tail number.
def get_active_trips(aircraft):
    con = sqlite3.connect(f'data/schedules/trips.db')
    cur = con.cursor()
    sql = f"SELECT * FROM {aircraft} WHERE isactive = 1"
    activeTrips = []
    for row in cur.execute(sql):
        activeTrips.append(row[0])
    return activeTrips

#Returns a string with the leg summary (tripnumber - airport1-airport2-airport3-airport4 etc.
#Takes an argument which is the trip number
def get_legs_string(aircraft, trip):
    legsString = ''
    con = sqlite3.connect(f'data/schedules/{aircraft}.db')
    cur = con.cursor()
    sql = f"SELECT * FROM '{trip}'"
    for row in cur.execute(sql):
        dep = row[1]
        arr = row[2]
        #If we haven't added any yet, we need to start it with our first dep and arr airport.
        if len(legsString) == 0:
            legsString = f"{dep}-{arr}"
        #Otherwise, we just need to add the current legs arr airport to the string.
        else:
            addString = f"-{arr}"
            legsString = legsString+addString
    return legsString


def print_active_schedules():
    #prints all active trips of all aircraft
    print("Schedule Summary - All Currently Active Trips")
    print("- - - - - - - - - - -  - - - - - - - - - - -")
    allAircraft = get_all_aircraft()
    for aircraft in allAircraft:
        #We need to get a list of all active trips
        print(f"Active trips on {aircraft}")
        
        con = sqlite3.connect('data/schedules/trips.db')
        cur = con.cursor()
        sql = f"SELECT num FROM {aircraft} WHERE isactive = '1'"
        for res in cur.execute(sql):
            #For each trip we want to print the trip number and the summary string
            trip = res[0]
            legs = get_legs_string(aircraft, trip)
            print(f"Trip #{trip}: {legs}")
        print()

def print_trip_summary(aircraft, trip):
    blankspace(10)
    con = sqlite3.connect(f'data/schedules/{aircraft}.db')
    cur = con.cursor()
    sql = f"SELECT * FROM '{trip}'"
    print(f"Trip Summary for Trip #{trip} on {aircraft}:")
    print("Leg#    Dep:     Arr:    Pax:       Distance:   ")
    print()
    for row in cur.execute(sql):
        leg = row[0]
        dep = row[1]
        arr = row[2]
        pax = row[3]
        depfbo = row[4]
        arrfbo = row[5]
        dist = round(airport_distance(dep, arr))
        print(f"{leg}       {dep}       {arr}       {pax}       {dist} NM  ")
        print(f"     Dep FBO: {depfbo}  /  Arr FBO: {arrfbo}")
        print()

def add_leg(aircraft, trip):
    #first need to determine if we are adding a leg from booked quotes or an empty leg
    blankspace(10)
    print("Add a leg to trip")
    print("Please select a below option:")
    print("1: Add a booked quote leg to this trip from the Charter Sales module")
    print("2: Add a non-quoted leg to this trip (Part 91/Owner/Company flight)")
    print("3: Go Back")
    selection = get_num_input(1,3)
    #if go back was selected, let's return False to get out of the function
    if selection == 3:
        return False
    dep = ''
    arr = ''
    pax = -1
    depfbo = ''
    arrfbo = ''
    quotekey = 0
    leg = -1
    #Selection 1 - flight should be added from the booked quotes table.
    if selection == 1:
        #Need to get all above variables from the booked quotes table.
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = "SELECT * FROM bookedquotes"
        bookedQuotes = []
        for row in cur.execute(sql):
            quote = {
                'key':row[0],
                'dep':row[1],
                'arr':row[2],
                'pax':row[3],
                'price':row[4],
                'depfbo':row[5],
                'arrfbo':row[6]
                }
            bookedQuotes.append(quote)
        #Let's print out the list of booked quotes and ask the user to select which quote they would like to add
        count = 1
        blankspace(10)
        for flight in bookedQuotes:
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
        print(f"{count}: Go Back")
        print()
        print()
        print("Please select one of the above quotes to add to the schedule, or select Go Back")
        quoteSelect = get_num_input(1, len(bookedQuotes)+1)
        #If go back selected, return false to leave function
        if quoteSelect == len(bookedQuotes)+1:
            return False
        flight = bookedQuotes[quoteSelect - 1]
        quotekey = flight['key']
        dep = flight['dep']
        arr = flight['arr']
        pax = flight['pax']
        depfbo = flight['depfbo']
        arrfbo = flight['arrfbo']

    if selection == 2:
        #We're adding a non-quoted leg to this trip so we'll need to get
        #the departure and arrival information from the user.

        #Let's show the user the booked quotes so that they can reference it as they build the flight.
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = "SELECT * FROM bookedquotes"
        bookedQuotes = []
        for row in cur.execute(sql):
            quote = {
                'key':row[0],
                'dep':row[1],
                'arr':row[2],
                'pax':row[3],
                'price':row[4],
                'depfbo':row[5],
                'arrfbo':row[6]
                }
            bookedQuotes.append(quote)
        blankspace(10)
        print("Booked Quotes: ")
        for flight in bookedQuotes:
            dep = flight['dep']
            arr = flight['arr']
            pax = flight['pax']
            price = flight['price']
            depfbo = flight['depfbo']
            arrfbo = flight['arrfbo']
            dist = round(airport_distance(dep, arr))
            print(f"Quote: ${price} -- Dep: {dep} -- Arr: {arr} -- Pax: {pax} -- Dist: {dist} NM")
            print()
            print(f"Departure FBO: {depfbo} -- Arrival FBO: {arrfbo}")
            print()
            print("-------------------------------------------------")
            print()

        print()
        print()
        print("Adding a Part 91/Empty/Company Flight:")
        dep = select_airport("departure")
        depfbo = select_fbo(dep, "departure")
        arr = select_airport("arrival")
        arrfbo = select_fbo(arr, "arrival")
        pax = -1
        #Now let's get the number of pax.  Using a while loop so user if forced to
        #enter a number.
        while pax == -1:
            try:
                pax = int(input("Please enter the number of passengers on this leg: "))
            except:
                print()
                print("Please enter a whole number only...")
                input("Press Enter to continue: ")
    #We need to calculate which leg this is going to be in the new trip summary.  Need to check first to see if
    #This is the first leg of the trip
    con = sqlite3.connect(f'data/schedules/{aircraft}.db')
    cur = con.cursor()
    sql = f"SELECT leg FROM '{trip}'"
    leg = 1
    for row in cur.execute(sql):
        leg += 1
    #Now let's create a user confirmation dialogue
    print_trip_summary(aircraft, trip)
    print()
    print("************NEW LEG***************")
    print(f"{leg}       {dep}       {arr}       {pax}       {depfbo} / {arrfbo}")
    print("************NEW LEG***************")
    print()
    confirm = input(f"Ready to write this leg to Trip #{trip}? (y/n): ")
    if confirm.lower() == 'y':
        #Let's write this trip to the schedule, we're already connected to the correct db file
        sql = f"INSERT INTO '{trip}' VALUES('{leg}', '{dep}', '{arr}', '{pax}', '{depfbo}', '{arrfbo}', '{quotekey}', 0)"
        cur.execute(sql)
        con.commit()
        
        
#Returns users fbo selection from the airport argument.  deporarr argument is for formatting
#the request to enter either a departure fbo or an arrival fbo.
def select_fbo(airport, deporarr):
    con = sqlite3.connect('data/fbo.db')
    cur = con.cursor()
    sql = f"SELECT * FROM {airport}"
    fboList = []
    for row in cur.execute(sql):
        fboList.append(row[0])
    print()
    print()
    print(f"Select {deporarr} FBO:")
    count = 1
    for fbo in fboList:
        print(f"{count}: {fbo}")
        count += 1
    selection = get_num_input(1, len(fboList))
    return fboList[selection-1]


#Removes the last leg of the argument provided trip from the aircraft
def remove_leg(aircraft, trip):
    blankspace(10)
    con = sqlite3.connect(f'data/schedules/{aircraft}.db')
    cur = con.cursor()
    sql = f"SELECT * FROM '{trip}'"
    legs = []
    print(f"Trip Summary for Trip #{trip} on {aircraft}:")
    print("Leg#    Dep:     Arr:    Pax:       Dep FBO/Arr FBO:")
    for row in cur.execute(sql):
        leg = {
            'leg':row[0],
            'dep':row[1],
            'arr':row[2],
            'pax':row[3],
            'depfbo':row[4],
            'arrfbo':row[5]
            }
        legs.append(leg)
    #If the trip is empty, len(legs) will be zero and we should inform the user
    #If empty we should return False to break out of the function
    if len(legs) == 0:
        print()
        print()
        print("This trip is currently empty, no flights to remove")
        input("Press Enter to continue: ")
        return False
    con.close()
    index = 0
    for flight in legs:
        if index < len(legs)-1:
            leg = flight['leg']
            dep = flight['dep']
            arr = flight['arr']
            pax = flight['pax']
            depfbo = flight['depfbo']
            arrfbo = flight['arrfbo']
            print(f"{leg}       {dep}       {arr}       {pax}       {depfbo} / {arrfbo}")
            index += 1
    print()
    print("------------------LEG TO BE REMOVED -------------------------")
    lastLeg = legs[len(legs)-1]
    leg = lastLeg ['leg']
    dep = lastLeg['dep']
    arr = lastLeg['arr']
    pax = lastLeg['pax']
    depfbo = lastLeg['depfbo']
    arrfbo = lastLeg['arrfbo']
    print(f"{leg}       {dep}       {arr}       {pax}       {depfbo} / {arrfbo}")
    print("------------------LEG TO BE REMOVED -------------------------")
    print()
    print()
    confirm = input("Are you sure you want to delete this leg? (y/n): ")
    if confirm.lower() == 'y':
        #Time to deleteify!  We need to connect to the aircraft schedule table
        con = sqlite3.connect(f'data/schedules/{aircraft}.db')
        cur = con.cursor()
        sql = f"DELETE FROM '{trip}' WHERE leg = '{leg}'"
        cur.execute(sql)
        con.commit()
        print()
        print()
        print("Leg removed from trip")
        input("Press Enter to continue: ")

def deactivate_trip(aircraft, trip):
    #first confirm the user wants to deactivate this trip
    print()
    print()
    confirm = input(f"Are you sure you want to deactivate Trip #{trip} on {aircraft}? (y/n): ")
    if confirm.lower() == 'y':
        #Connect to the trips db
        con = sqlite3.connect('data/schedules/trips.db')
        cur = con.cursor()
        sql = f"UPDATE {aircraft} SET isactive = 0 WHERE num = {trip}"
        cur.execute(sql)
        con.commit()


def manage_aircraft_schedules():
    allAircraft = get_all_aircraft()
    blankspace(10)
    print("Please select the tail number you would like to manage:")
    print()
    count = 1
    for tail in allAircraft:
        print(f"{count}: {tail}")
        count += 1
    print(f"{count}: Go Back")
    selection = get_num_input(1, len(allAircraft) +1)
    if selection == len(allAircraft)+1:
        #return is useless, but it lets us immediately exit the function
        return False
    aircraft = allAircraft[selection-1]
    #now that we have an aircraft selected, let's fetch all of this aircrafts active trips,
    #and have the user select a trip to modify, or to create a new trip
    activeTrips = get_active_trips(aircraft)
    print()
    print()
    print(f"Active Trips on {aircraft}")
    print()
    count = 1
    for trip in activeTrips:
        tripString = get_legs_string(aircraft, trip)
        print(f"{count}: Open Trip #{trip}: {tripString}")
        count += 1
    print(f"{count}: Show all trips including inactive (hidden) trips")
    count += 1
    print(f"{count}: Create New Trip")
    count += 1
    print(f"{count}: Go back")
    #Now let's get the user's selection for which trip to pick out of the activeTrips list,
    #Or allow the user to create a new trip.
    choice = get_num_input(1, len(activeTrips)+3)
    if choice == len(activeTrips)+3:
        #Go back selected, let's return False and get out of the function
        return False
    if choice == len(activeTrips)+2:
        #Confirm user wants to open a new trip
        print()
        print()
        confirmtrip = input("Are you sure you want to open a new trip? (y/n): ")
        if confirmtrip.lower() == 'y':
            #First we need to determine the new trip number then add trip to the aircrafts
            #table in the trips db file
            con = sqlite3.connect('data/schedules/trips.db')
            cur = con.cursor()
            sql = f"SELECT num FROM {aircraft} ORDER BY num DESC"
            res = cur.execute(sql)
            num = res.fetchone()[0]
            #We need to increment the max trip number by 1 to get our new trip number]
            num += 1
            #num is what we are going to write into the list of trips and set active.
            #We also need to add it as a table to the aircrafts schedule db file
            sql = f"INSERT INTO {aircraft} VALUES ({num}, 1)"
            cur.execute(sql)
            con.commit()
            con.close()
            #Now we change over to the schedule/aircraft tail db and insert a new table for the trip
            con = sqlite3.connect(f'data/schedules/{aircraft}.db')
            cur = con.cursor()
            sql = f"CREATE TABLE '{num}'"
            sql = sql+" ('leg' INTEGER, 'dep' TEXT, 'arr' TEXT, 'pax' INTEGER, 'depfbo' TEXT, 'arrfbo' TEXT, 'quotekey' INTEGER,'flightlogged' INTEGER)"
            cur.execute(sql)
            con.commit()
            con.close()
            #We also need to make a logbook table for this new trip
            con = sqlite3.connect(f'data/logbooks/{aircraft}.db')
            cur = con.cursor()
            sql = f'''CREATE TABLE "{num}" (
                "leg"	INTEGER,
                "dep"	TEXT,
                "arr"	TEXT,
                "out"	TEXT,
                "off"	TEXT,
                "on"	TEXT,
                "in"	TEXT,
                "flight"	REAL,
                "block"	REAL,
                "inst"	REAL,
                "approach"	TEXT,
                "night"	REAL,
                "pax"	INTEGER
                )'''
            cur.execute(sql)
            con.commit()
            con.close()
            return False
        else:
            #If user selected no, we need to return out of the function to go back a menu
            return False
    #If user selects the option to show all hidden trips
    if choice == len(activeTrips)+1:
        blankspace(10)
        allTrips = []
        con = sqlite3.connect('data/schedules/trips.db')
        cur = con.cursor()
        sql = f"SELECT * FROM {aircraft}"
        for row in cur.execute(sql):
            allTrips.append(row[0])
        print(f"Displaying Active and Inactive trips on {aircraft}")
        print()
        for trip in allTrips:
            tripString = get_legs_string(aircraft, trip)
            print(f"Trip #{trip}: {tripString}")
        #Ask user if they would like to reactivate any trips
        print()
        print()
        print("Select an option:")
        print("1: Reactivate (unhide) a trip")
        print("2: Go back")
        unhideOption = get_num_input(1, 2)
        unhideTrip = -1
        if unhideOption == 1:
            print()
            print()
            try:
                unhideTrip = int(input("Enter trip number to unhide: "))
            except:
                print()
                print("Trip not found or a number wasn't entered...")
                input("Press Enter to continue: ")
                return False
            if unhideTrip > len(allTrips) or unhideTrip < 0:
                print()
                print("Trip not found or entered number out of range...")
                input("Press Enter to continue: ")
                return False
            confirm = input(f"Are you sure you want to reactivate (unhide) Trip #{unhideTrip} on {aircraft}? (y/n): ")
            if confirm.lower() == 'y':
            #This far in, we've now shown unhideTrip is an actual trip we can unhide, so lets reactivate it
            #by editing it's line in trips.db
            #We're already connected to trips.db, so let's just send it a new sql command for the selected trip.
                sql = f"UPDATE {aircraft} SET isactive = 1 WHERE num = {unhideTrip}"
                cur.execute(sql)
                con.commit()
                print()
                print("Trip reactivated")
                input("Press Enter to continue: ")
                return False
        else:
            #return from the function if the user doesn't select yes
            return False
        
        
    trip = activeTrips[choice-1]
    #Now that we have the trip number, let's print a trip summary
    while True:
        print_trip_summary(aircraft, trip)
        #With the schedule summary now printed, lets ask the user what they want to do
        #Add leg to trip, remove last leg of trip, print the trip summary, or go back
        print()
        print()
        print("Please select an option:")
        print("1: Add leg to this trip")
        print("2: Remove the last leg of this trip")
        print("3: Print trip summary")
        print("4: Deactivate (hide) trip")
        print("5: Go Back")
        selection = get_num_input(1,5)
        if selection == 1:
            add_leg(aircraft, trip)
        if selection == 2:
            remove_leg(aircraft, trip)
        if selection == 3:
            print_out_trip(aircraft, trip)
        if selection == 4:
            deactivate_trip(aircraft, trip)
            break
        if selection == 5:
            #break to go back
            break

#Prints trip information out to a text file        
def print_out_trip(aircraft, trip):
    blankspace(10)
    con = sqlite3.connect(f'data/schedules/{aircraft}.db')
    cur = con.cursor()
    sql = f"SELECT * FROM '{trip}'"
    print(f"Trip Summary for Trip #{trip} on {aircraft}:")
    print("Leg#    Dep:     Arr:    Pax:       Dep FBO/Arr FBO:")
    for row in cur.execute(sql):
        leg = row[0]
        dep = row[1]
        arr = row[2]
        pax = row[3]
        depfbo = row[4]
        arrfbo = row[5]
        print(f"{leg}       {dep}       {arr}       {pax}       {depfbo} / {arrfbo}")
    print()
    print()
    verify = input(f"Print trip out to file {aircraft} Trip {trip}.txt? (y/n): ")
    if verify.lower() == 'y':
        #Open the file for writing
        file = open(f'TripSheets/{aircraft} Trip {trip}.txt', 'w')
        #Re-execute the above SQL command and this time write to the file
        file.write(f"Trip Summary for Trip #{trip} on {aircraft}:\n \n \n")
        file.write("Leg#    Dep:     Arr:    Pax:       Dist:     \n")
        for row in cur.execute(sql):
            leg = row[0]
            dep = row[1]
            arr = row[2]
            pax = row[3]
            depfbo = row[4]
            arrfbo = row[5]
            dist = round(airport_distance(dep, arr))
            file.write(f"{leg}       {dep}       {arr}       {pax}       {dist}   \n")
            file.write(f"    Dep FBO: {depfbo}  /  Arr FBO: {arrfbo} \n \n")
        print(f"Trip Summary written successfully to TripSheets/{aircraft} Trip {trip}.txt")
        input("Press Enter to continue: ")
            
    
    

#Main function, module entry point
def main():   
    while True:
        blankspace(10)
        #Here we should print all active trips of all aircraft
        #Options should be to manage aircraft schedules or go back.
        print_active_schedules()
        print()
        print()
        print("Available Options:")
        print("1: Manage Aircraft Schedules")
        print("2: Go Back")
        selection = get_num_input(1, 2)
        #Option selected to manage aircraft schedules
        if selection == 1:
            manage_aircraft_schedules()
        if selection == 2:
            break
