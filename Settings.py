#Settings program to modify user data, company data, airports, and aircraft.

import sqlite3
import os
from Tools import get_airport_coord
from Tools import blankspace
from Tools import get_num_input
from Tools import refresh_quotes
from Tools import get_charter_min
from Tools import get_charter_max

#Adds an airport to the sql database.  Arguments are the strings for the
#airport name and region.

#Ask the user to enter FBO information for the airport.  Returns a list object
#Containing fbo strings.
def get_fbo_info():
    fbos = []
    #Starts with a loop until user says they're done adding fbo's
    while True:
        #Let's first print the airports entered so far to the terminal
        print("FBO's added: ")
        print()
        for fbo in fbos:
            print(fbo)
        #Next lets ask the user for the FBO name
        print()
        print("Please enter FBO name")
        newfbo = input("or type DONE when done: ")
        print()
        #If user didn't type DONE, let's add this fbo to the list
        if newfbo.upper() == 'DONE':
            #Let's make sure the user added at least 1 FBO
            if len(fbos) > 0:
                break
            else:
                print()
                print("At least one FBO is required to be entered")
                input("Press Enter to continue: ")
        elif newfbo.upper() == '':
            print("Nothing was entered...")
            print()
        else:
            fbos.append(newfbo)
    return fbos

#Returns true if an airport is already in the database.
def airport_in_database(airport):
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = f"SELECT * FROM airports WHERE code = '{airport}'"
    count = 0
    for row in cur.execute(sql):
        count += 1
    if count > 0:
        return True
    else:
        return False

#User prompted way to remove an airport from the flights database
def remove_airport():
    airport = input("Enter the airport you would like to remove: ")
    print()
    airport = airport.upper()
    #Drop the k if user included it
    if len(airport) > 3 and airport[0] == 'K':
        airport = airport.replace('K', '', 1)
    #For an airport removal, we first need to check if it is already in the database
    if airport_in_database(airport):
        #Print airport information to terminal and prompt user to confirm
        #they want to delete the airport
        #Let's pull this data from the db
        lat = 0.1
        long = 0.1
        fbos = []
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = f"SELECT * FROM airports WHERE code = '{airport}'"
        for row in cur.execute(sql):
            lat = row[1]
            long = row[2]
        con.close()
        #Now let's grab the FBO data
        con = sqlite3.connect('data/fbo.db')
        cur = con.cursor()
        sql = f"SELECT * FROM {airport}"
        for row in cur.execute(sql):
            fbos.append(row[0])
        con.close()
        print("Airport found in database.")
        print("Airport info:")
        print()
        print(f"{airport}, {lat}, {long}")
        print()
        print("FBO('s):")
        for fbo in fbos:
            print(fbo)
        #Confirm the user wants to remove this airport
        print()
        confirm = input("Are you sure you would like to remove this airport? (y/n): ")
        if confirm.lower() == 'y':
            #To remove the airport, we need to remove it from the airports table, as well as remove
            #The respective table in the fbo database.
            con = sqlite3.connect('data/flights.db')
            cur = con.cursor()
            sql = f"DELETE FROM airports WHERE code = '{airport}'"
            cur.execute(sql)
            con.commit()
            con.close()

            #Next let's remove the airports table from the fbo database
            con = sqlite3.connect('data/fbo.db')
            cur = con.cursor()
            sql = f"DROP TABLE {airport}"
            cur.execute(sql)
            con.commit()
            print("Airport removed!")
            input("Press Enter to continue: ")
            #Now that the airport is removed, we need to refresh the avilable
            #quotes so that they don't reference a non-existent airport.
            refresh_quotes()
    else:
        #Airport wasn't already in database
        print("Airport not found in the database...")
        input("Press Enter to continue: ")

#User prompted way to add an airport to the flights database
def add_user_airport():
    airport = input("Enter the airport you would like to add: ")
    print()
    airport = airport.upper()
    #Drop the k if user included it
    if len(airport) > 3:
        airport = airport.replace('K', '', 1)
    #Returns the airport coordinates and if it was found (index 0 for found)
    latlong = get_airport_coord(airport)
    #If airport was found:
    #First need to check if airport is already in the database
    if airport_in_database(airport):
        print("Airport is already in database...")
        input("Press Enter to continue: ")
    elif latlong[0]:
        print("Airport not yet in database")
        print()
        lat = latlong[1]
        long = latlong[2]
        print(f"Airport Code: {airport}")
        print(f"Airport Coordinates: {lat} , {long}")

        #We need to get airport FBO information from the user
        #expected to return a list object containing FBO name strings.
        fbos = get_fbo_info()
        #Print confirmation window
        blankspace(10)
        print(f"Airport Code: {airport}")
        print(f"Airport Coordinates: {lat} , {long}")
        print()
        print("Fbo('s): ")
        for fbo in fbos:
              print(fbo)
        print()
        print()
        ready = input("Save airport to database? (y/n): ")
        if ready.lower() == 'y':
            #First connect to db
            con = sqlite3.connect('data/flights.db')
            cur = con.cursor()
            sql = f"INSERT INTO airports VALUES ('{airport}', '{lat}', '{long}')"
            cur.execute(sql)
            con.commit()
            con.close()
            #Now let's write in the fbo's to the fbo database.
            #Start by creating a new table with the airport name as the title
            con = sqlite3.connect('data/fbo.db')
            cur = con.cursor()
            sql = f"CREATE TABLE {airport} ('name' TEXT)"
            cur.execute(sql)
            con.commit()
            #Now let's write in the fbo's to the new table
            for fbo in fbos:
                sql = f"INSERT INTO {airport} VALUES('{fbo}')"
                cur.execute(sql)
                con.commit()
            print()
            print("Airport added to database!")
            input("Press enter to continue...: ")
    else:
        print("Airport not found")
        input("Press Enter to continue: ")

#Argument defined way to add an airport.  Already assumes the airport was
#not found in the db file.  Returns true if airport added to database, returns false if user aborts
def add_airport(airport):
    #Returns the airport coordinates and if it was found (index 0 for found)
    latlong = get_airport_coord(airport)
    lat = latlong[1]
    long = latlong[2]
    print(f"Airport Code: {airport}")
    print(f"Airport Coordinates: {lat} , {long}")
    #We need to get airport FBO information from the user
    #expected to return a list object containing FBO name strings.
    fbos = get_fbo_info()
    #Print confirmation window
    blankspace(10)
    print(f"Airport Code: {airport}")
    print(f"Airport Coordinates: {lat} , {long}")
    print()
    print("Fbo('s): ")
    for fbo in fbos:
        print(fbo)
    print()
    print()
    ready = input("Save airport to database? (y/n): ")
    if ready.lower() == 'y':
        #First connect to db
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = f"INSERT INTO airports VALUES ('{airport}', '{lat}', '{long}')"
        cur.execute(sql)
        con.commit()
        con.close()
        #Now let's write in the fbo's to the fbo database.
        #Start by creating a new table with the airport name as the title
        con = sqlite3.connect('data/fbo.db')
        cur = con.cursor()
        sql = f"CREATE TABLE {airport} ('name' TEXT)"
        cur.execute(sql)
        con.commit()
        #Now let's write in the fbo's to the new table
        for fbo in fbos:
            sql = f"INSERT INTO {airport} VALUES('{fbo}')"
            cur.execute(sql)
            con.commit()
        print()
        print("Airport added to database!")
        input("Press enter to continue...: ")
        return True
    else:
        return False




#Shows all airports in the database
def show_all_airports():
    con = sqlite3.connect('data/flights.db')
    cur = con.cursor()
    sql = "SELECT * FROM airports ORDER BY code"
    blankspace(10)
    count = 1
    print("All airports in the database:")
    for row in cur.execute(sql):
        code = row[0]
        lat = row[1]
        long = row[2]
        print(f"{count}: {code}, {lat}, {long}")
        fbocon = sqlite3.connect('data/fbo.db')
        fbocur = fbocon.cursor()
        fbosql = f"SELECT * FROM {code}"
        for fbo in fbocur.execute(fbosql):
            print(fbo[0])
        print()
        count += 1

def manage_aircraft():
    #Print list of all aircraft and whether they are active or inactive
    blankspace(10)
    print("Manage Aircraft Settings")
    print()
    con = sqlite3.connect('data/aircraft.db')
    cur = con.cursor()
    sql = "SELECT * FROM aircraft"
    allAircraft = []
    for row in cur.execute(sql):
        aircraft = {
            'tail':row[0],
            'type':row[1],
            'isactive':row[2],
            'home':row[3],
            }
        allAircraft.append(aircraft)
    print("List of Aircraft in the database:")
    print()
    print("Tail Num:     Type:    Home:     Currently Active (X)")
    for aircraft in allAircraft:
        tail = aircraft['tail']
        typ = aircraft['type']
        active = aircraft['isactive']
        home = aircraft['home']
        activeMark = ''
        if active == 1:
            activeMark = 'X'
        print(f"{tail}          {typ}      {home}       {activeMark}")
    print()
    print("Select an option:")
    print("1: Add Aircraft to operations")
    print("2: Modify Aircraft active status")
    print("3: Modify Aircraft Homebase")
    print("4: Go back")
    selection = get_num_input(1,4)
    if selection == 1:
        add_aircraft()
    if selection == 2:
        modify_aircraft()
    if selection == 3:
        modify_home()
    if selection == 4:
        return False

#Returns users home airport preference after ensuring that it exists in the database
def get_home_airport():
    while True:
        print()
        print()
        airport = input("Please enter new aircraft home base: ")
        #If length > 3, strip the first K and let's make it all uppercase
        airport = airport.upper()
        if len(airport) > 3:
            airport = airport.replace('K', '', 1)
        #Verify airport is in the database
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = f"SELECT * FROM airports WHERE code = '{airport}'"
        count = 0
        for row in cur.execute(sql):
            count += 1
        #If count still equals zero, airport not in database.  Let's check if it's in the airport db.  If it is, let's add
        #it do the db
        if count == 0:
            coord = get_airport_coord(airport)
            #If index 0 of coord False, airport wasn't found at all and we should return false
            if coord[0] == False:
                print()
                print("Airport not found...")
                input("Press Enter to continue: ")
            else:
                print()
                print("New homebase not yet in database, so we will add it.")
                print("You will next be asked to enter FBO information for this airport")
                input("Press Enter to continue: ")
                if add_airport(airport):
                    return airport
        else:
            return airport

def modify_home():
    #Let's first get the list of aircraft and have the user select one.
    blankspace(10)
    con = sqlite3.connect('data/aircraft.db')
    cur = con.cursor()
    sql = "SELECT * FROM aircraft WHERE isactive = 1"
    count = 1
    allAircraft = []
    for row in cur.execute(sql):
        tail = row[0]
        typ = row[1]
        home = row[3]
        print(f"{count}: {tail} - {typ} - {home}")
        count += 1
        allAircraft.append(row[0])
    print(f"{count}: Go Back")
    print()
    selection = get_num_input(1, len(allAircraft)+1)
    if selection == len(allAircraft)+1:
        return False
    aircraft = allAircraft[selection-1]
    airport = get_home_airport()
    print()
    print()
    verify = input(f"Confirm ready to save {airport} as new home for {aircraft}?  (y/n): ")
    if verify.lower() == 'y':
        sql = f"UPDATE aircraft SET home = '{airport}' WHERE tail = '{aircraft}'"
        cur.execute(sql)
        con.commit()
    
    
def add_aircraft():
    blankspace(10)
    tail = input("Enter aircraft tail number: ")
    tail = tail.upper()
    typ = input("Enter aircraft type code: ")
    typ = typ.upper()
    home = get_home_airport()
    print()
    print()
    print("Aircraft to add:")
    print(f"Tail: {tail}    Type: {typ}")
    print()
    verify = input("Ready to add above aircraft to operations?  (y/n): ")
    if verify.lower() == 'y':
        #Add aircraft to the list of aircraft, create a aircraft schedule db file and trip 1
        con = sqlite3.connect('data/aircraft.db')
        cur = con.cursor()
        sql = f"INSERT INTO aircraft VALUES('{tail}', '{typ}', 1, '{home}')"
        cur.execute(sql)
        con.commit()
        con.close()
        #Add an aircraft tail number table to the trips db file and set insert trip 1 and set it to active
        con = sqlite3.connect('data/schedules/trips.db')
        cur = con.cursor()
        sql = f"CREATE TABLE {tail} ('num' INTEGER, 'isactive' INTEGER)"
        cur.execute(sql)
        con.commit()
        sql = f"INSERT INTO {tail} VALUES (1, 1)"
        cur.execute(sql)
        con.commit()
        con.close()
        #Now create the tails db in data/schedules by connecting to it, and creating table 1
        con = sqlite3.connect(f'data/schedules/{tail}.db')
        cur=con.cursor()
        sql = f"CREATE TABLE '1' ('leg' INTEGER, 'dep' TEXT, 'arr' TEXT, 'pax' INTEGER, 'depfbo' TEXT, 'arrfbo' TEXT, 'quotekey' INTEGER, 'flightlogged' INTEGER)"
        cur.execute(sql)
        con.commit()
        con.close()
        #Now create tails logbook db by connecting to it and creating table 1
        con = sqlite3.connect(f'data/logbooks/{tail}.db')
        cur = con.cursor()
        sql = f'''CREATE TABLE "1" (
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

        #BEGIN NOLAN'S CHANGES
        #Now add new aircraft to aml table - We don't need to create a new table, just enter into existing one
        con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
        cur = con.cursor()
        #sql = f"CREATE TABLE aml ('tail' TEXT PRIMARY KEY, 'type' TEXT, 'location' TEXT, 'fuel' INTEGER, 'AFTT' INTEGER, 'discrep' TEXT)"
        #cur.execute(sql)
        sql = f"INSERT INTO aml (tail,type,location,fuel,AFTT,discrep) VALUES ('{tail}', '{typ}','{home}', 0.0, 0.0, 'None')"
        cur.execute(sql)
        con.commit()
        con.close()

        print("Aircraft added to database")
        input("Press Enter to continue: ")


#similar to add_aircraft, but loops to force user to add aircraft.
def add_first_aircraft():
    while True:
        blankspace(10)
        tail = input("Enter aircraft tail number: ")
        tail = tail.upper()
        typ = input("Enter aircraft type code: ")
        typ = typ.upper()
        home = get_home_airport()
        print()
        print()
        print("Aircraft to add:")
        print(f"Tail: {tail}    Type: {typ}   Home:{home}")
        print()
        verify = input("Ready to add above aircraft to operations?  (y/n): ")
        if verify.lower() == 'y':
            #Add aircraft to the list of aircraft, create a aircraft schedule db file and trip 1
            con = sqlite3.connect('data/aircraft.db')
            cur = con.cursor()
            sql = f"INSERT INTO aircraft VALUES('{tail}', '{typ}', 1, '{home}')"
            cur.execute(sql)
            con.commit()
            con.close()
            #Creates the trips db file, adds the aircraft to it and sets it to active.
            con = sqlite3.connect('data/schedules/trips.db')
            cur = con.cursor()
            sql = f"CREATE TABLE {tail} ('num' INTEGER, 'isactive' INTEGER)"
            cur.execute(sql)
            con.commit()
            sql = f"INSERT INTO {tail} VALUES (1, 1)"
            cur.execute(sql)
            con.commit()
            con.close()
            #Now create the tails db in data/schedules by connecting to it, and creating table 1
            con = sqlite3.connect(f'data/schedules/{tail}.db')
            cur=con.cursor()
            sql = f"CREATE TABLE '1' ('leg' INTEGER, 'dep' TEXT, 'arr' TEXT, 'pax' INTEGER, 'depfbo' TEXT, 'arrfbo' TEXT, 'quotekey' INTEGER, 'flightlogged' INTEGER)"
            cur.execute(sql)
            con.commit()
            con.close()
            con = sqlite3.connect(f'data/logbooks/{tail}.db')
            cur = con.cursor()
            sql = f'''CREATE TABLE "1" (
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

            #BEGIN NOLAN'S CHANGES
            #Now create airplane mx logbook/status report
            con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
            cur = con.cursor()
            sql = f"CREATE TABLE aml ('tail' TEXT, 'type' TEXT, 'location' TEXT, 'fuel' INTEGER, 'AFTT' INTEGER, 'discrep' TEXT)"
            cur.execute(sql)
            sql = f"INSERT INTO aml (tail,type,location,fuel,AFTT,discrep) VALUES ('{tail}', '{typ}','{home}', 0.0, 0.0, 'None')"
            cur.execute(sql)
            con.commit()
            con.close()

            print("Aircraft added to database")
            input("Press Enter to continue: ")
            break



def modify_aircraft():
    blankspace(10)
    #Start by getting all aircraft
    con = sqlite3.connect('data/aircraft.db')
    cur = con.cursor()
    sql = "SELECT * FROM aircraft"
    allAircraft = []
    for row in cur.execute(sql):
        aircraft = {
            'tail':row[0],
            'type':row[1],
            'isactive':row[2]
            }
        allAircraft.append(aircraft)
    print("List of Aircraft in the database:")
    print()
    print("  Tail Num:     Type:     Currently Active (X)")
    count = 1
    for aircraft in allAircraft:
        tail = aircraft['tail']
        typ = aircraft['type']
        active = aircraft['isactive']
        activeMark = ''
        if active == 1:
            activeMark = 'X'
        print(f"{count}: {tail}          {typ}         {activeMark}")
        count += 1
    print(f"{count}: Go back")
    print()
    print("Select aircraft from above list")
    selection = get_num_input(1, len(allAircraft)+1)
    if selection == len(allAircraft)+1:
        #Go back selected, return False to break out of function
        return False
    aircraft = allAircraft[selection-1]
    tail = aircraft['tail']
    typ = aircraft['type']
    act = aircraft['isactive']
    #If is active, let user know it's active and ask if they want to make aircraft inactive
    if act == 1:
        print()
        print()
        print("Aircraft currently active, would you like to make the aircraft inactive?")
        print("This will hide the aircraft, but will not delete any records")
        verify = input("Make aircraft inactive? (y/n): ")
        if verify.lower() == 'y':
            #Pretty simple, just write a 0 into isactive column of aircraft db for tail
            sql = f"UPDATE aircraft SET isactive = 0 WHERE tail = '{tail}'"
            cur.execute(sql)
            con.commit()
    if act == 0:
        print()
        print()
        print("Aircraft is currently inactive.  Would you like to bring aircraft back to active status?")
        verify = input("Make aircraft active? (y/n): ")
        if verify.lower() == 'y':
            #Pretty simple, just write a 0 into isactive column of aircraft db for tail
            sql = f"UPDATE aircraft SET isactive = 1 WHERE tail = '{tail}'"
            cur.execute(sql)
            con.commit()    

def manage_dist_settings():
    #Quote distance settings
    #Let's start by getting the quote min dist and quote max dist and displaying them to the user
    #This function already exists in the Tools module, so let's call it
    while True:
        minDist = get_charter_min()
        maxDist = get_charter_max()
        blankspace(10)
        print("Current distance settings for randomly generated quote airport pairs:")
        print(f"Minimum distance between airports: {minDist}")
        print(f"Maximum distance between airports: {maxDist}")
        print()
        print()
        print("Please select an option:")
        print("1: Change Minimum distance settings")
        print("2: Change Maximum distance settings")
        print("3: Go back")
        print()
        selection = get_num_input(1,3)
        print()
        print()
        if selection == 3:
            break
        if selection == 1:
            #Need a while loop to ensure we get a valid distance
            newDist = -1
            while newDist < 0:
                try:
                    newDist = int(input("Please enter a new minimum distance: "))
                except:
                    print("Please enter numbers only...")
                    input("Press Enter to continue: ")
            print()
            print()
            print(f"New Minimum distance settings will be: {newDist} NM.")
            verify = input("Save new minimum distance? (y/n): ")
            if verify.lower() == 'y':
                con = sqlite3.connect('data/flights.db')
                cur = con.cursor()
                sql = f"UPDATE settings SET num = {newDist} WHERE name = 'quotemindist'"
                cur.execute(sql)
                con.commit()
                refresh_quotes_prompt()
        if selection == 2:
            #Need a while loop to ensure we get a valid distance
            newDist = -1
            while newDist < 0:
                try:
                    newDist = int(input("Please enter a new maximum distance: "))
                except:
                    print("Please enter numbers only...")
                    input("Press Enter to continue: ")
            print()
            print()
            print(f"New Maximum distance settings will be: {newDist} NM.")
            verify = input("Save new Maximum distance? (y/n): ")
            if verify.lower() == 'y':
                con = sqlite3.connect('data/flights.db')
                cur = con.cursor()
                sql = f"UPDATE settings SET num = {newDist} WHERE name = 'quotemaxdist'"
                cur.execute(sql)
                con.commit()
                refresh_quotes_prompt()
            
def refresh_quotes_prompt():
    print()
    print()
    print("Would you like to refresh the available quotes using this new distance parameter?")
    confirm = input("Refresh quote list?(y/n): ")
    if confirm.lower() == 'y':
        refresh_quotes()

def clear_booked_quotes():
    blankspace(10)
    print("Clearing booked quotes will lose any quotes that you've accepted.")
    verify = input("Are you sure you want to continue? (y/n): ")
    if verify.lower() == 'y':
        con = sqlite3.connect('data/flights.db')
        cur = con.cursor()
        sql = "DELETE FROM bookedquotes"
        cur.execute(sql)
        con.commit()
        

#####################
#Main function below
def main():
    #Start of while loop for user to select menu functions
    while True:
        blankspace(10)
        print("Settings Main Menu - select an option")
        print()
        print("1: Manage Aircraft Settings")
        print("2: Manage Airport Settings")
        print("3: Manage Quoteable Flight Distance Settings")
        print("4: Clear Booked Quotes List")
        print("5: Go Back")
        print()
        mainChoice = get_num_input(1,5)
        if mainChoice == 1:
            manage_aircraft()
        if mainChoice == 2:
            while True:
                blankspace(10)
                print("Manage Airport Settings - select an option")
                print("1. View all airports in the database")
                print("2. Add an airport to the database")
                print("3. Remove an airport from the database")
                print("4. Go Back")
                print()
                selection = get_num_input(1,4)
                print()
                if selection == 1:
                    show_all_airports()
                if selection == 2:
                    add_user_airport()
                if selection == 3:
                    remove_airport()
                if selection == 4:
                    break
        if mainChoice == 3:
            manage_dist_settings()
        if mainChoice == 4:
            clear_booked_quotes()

        if mainChoice == 5:
            break

