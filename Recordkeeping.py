#Recordkeeping module (log a flight)

import sqlite3
from Schedule import get_active_trips
from Schedule import get_all_aircraft
from Schedule import get_legs_string
from Schedule import print_trip_summary
from Tools import blankspace
from Tools import get_num_input
from Tools import airport_distance
from Tools import getFuel






def log_flight():
    blankspace(10)
    allAircraft = get_all_aircraft()
    blankspace(10)
    print("Please select the tail number you would like to log a trip for:")
    print()
    count = 1
    for tail in allAircraft:
        print(f"{count}: {tail}")
        count += 1
    print(f"{count}: Go Back")
    print()
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
        print(f"{count}: {aircraft} Trip #{trip}: {tripString}")
        count += 1
    print()
    print()
    selectTrip = get_num_input(1, len(activeTrips))
    trip = activeTrips[selectTrip-1]
    #Now that we have the trip number, let's print a trip summary
    while True:
        blankspace(10)
        con = sqlite3.connect(f'data/schedules/{aircraft}.db')
        cur = con.cursor()
        sql = f"SELECT * FROM '{trip}'"
        print(f"Trip Summary for Trip #{trip} on {aircraft}:")
        print("Leg#    Dep:     Arr:    Pax:       Distance:    Flight Logged(x):")
        print()
        count = 1
        for row in cur.execute(sql):
            leg = row[0]
            dep = row[1]
            arr = row[2]
            pax = row[3]
            logged = ''
            if row[7] == 1:
                logged = 'X'
            dist = round(airport_distance(dep, arr))
            print(f"{leg}       {dep}       {arr}       {pax}       {dist} NM        {logged}")
            print()
            count += 1
        print()
        print()
        print(f"{count}: Go Back")
        print()
        print()
        print(f"Select a leg to log, or select {count} to go back.")
        legSelect = get_num_input(1, count)
        if legSelect == count:
            break       #Go back selected, break loop
        blankspace(10)
        #Print leg information and verify the user would like to log this leg
        sql = f"SELECT * FROM '{trip}' WHERE leg = '{legSelect}'"
        res = cur.execute(sql)
        legList = res.fetchone()
        #We need to make sure the flight wasn't already logged.  This is tracked in the flightlogged column
        if legList[7] == 1:
            print("Flight was already logged")
            input("Press Enter to continue: ")
            break
        leg = legList[0]
        dep = legList[1]
        arr = legList[2]
        pax = legList[3]
        quotekey = legList[6]
        print(f"Ready to input information for the following leg?")
        print(f"Leg #{leg}:  {dep}-{arr}  {pax} pax")
        verify = input("Continue? (y/n): ")
        if verify.lower() != 'y':
            break
        #While loop to make sure this information is correct or redo it
        while True:
            out = enter_time('OUT')
            off = enter_time('OFF')
            on = enter_time('ON')
            inn = enter_time('IN')  #can't use in
            #Let's get the flight and block time using the calc_time() function
            block = calc_time(out, inn)
            flight = calc_time(off, on)
            blankspace(10)
            print("OUT     OFF     ON     IN")
            print(f"{out}   {off}   {on}    {inn}")
            print()
            print(f"Flight Time: {flight}")
            print(f"Block Time: {block}")
            print()
            verify = input("Verify this information is correct - (y/n): ")
            if verify.lower() == 'y':
                #Time to get the instrument time.  While loop runs to make sure it's less than
                #the flight time
                approach = get_approach()
                inst = 0
                night = 0
                while True:
                    inst = float(input("Please enter instrument time (hours and decimal hours): "))
                    if inst >= 0 and inst <= flight:
                        break
                    else:
                        print("Error, instrument time must be greater than or equal to zero")
                        print("And less than the total flight time.")
                        input("Press Enter to continue: ")

                while True:
                        night = float(input("Please enter night time (hours and decimal hours): "))
                        if night >= 0 and night <= flight:
                            break
                        else:
                            print("Error, night time must be greater than or equal to zero")
                            print("And less than the total flight time.")
                            input("Press Enter to continue: ")
                #Let's print a preview of the entry
                blankspace(10)
                print("Leg#    Dep    Arr    OUT   OFF  ON   IN   Flt Time   Block Time   Inst   App  Night   Pax")
                print(f"{leg}       {dep}    {arr}    {out}  {off} {on} {inn}    {flight}       {block}        {inst}    {approach}    {night}    {pax}")
                print()
                print("Verify above information")
                confirm = input("Ready to write above information to database?  This cannot be undone.  (y/n): ")
                if confirm.lower() == 'y':
                    #Connect to and write flight to the database
                    con = sqlite3.connect(f'data/logbooks/{aircraft}.db')
                    cur = con.cursor()
                    sql = f"INSERT INTO '{trip}' VALUES"
                    sql = sql+f"({leg}, '{dep}', '{arr}', '{out}', '{off}', '{on}', '{inn}', {flight}, {block}, {inst}, '{approach}', {night}, {pax})"
                    cur.execute(sql)
                    con.commit()
                    con.close()
                    print()
                    print()
                    #now we need to mark the flight as logged in the trip schedule db
                    con = sqlite3.connect(f'data/schedules/{aircraft}.db')
                    cur = con.cursor()
                    sql = f"UPDATE '{trip}' SET flightlogged = 1 WHERE leg = '{leg}'"
                    cur.execute(sql)
                    con.commit()
                    con.close()
                    #Finally, with the flight flown we can remove it from the bookedquotes table
                    con = sqlite3.connect(f'data/flights.db')
                    cur = con.cursor()
                    sql = f"DELETE FROM bookedquotes WHERE key = {quotekey}"
                    cur.execute(sql)
                    con.commit
                    con.close()
                    break

            #BEGIN NOLAN CHANGES - WRITING DATA TO MXLOGBOOK
            #Nolan's Functions below
        def getDiscrep():
        #Function to see if any discrepancy needs to be logged. 
        #If yes, user will write in the discrepancy (freetext)
        #If no, postflight/recordkeeping will continue.
            while True:
                blankspace(10)
                print("Do you need to log any discrepancies? ")
                print()
                print("Select an option below: ")
                print("1. Log or clear a discrepancy. ")
                print("2. Continue with postflight. ")
                print()
                print("NOTE: Logging a discrepancy will overwrite the current discrepancy")
                print("If you have multiple discrepancies, you will need to list them all...")
                print()

                selection = get_num_input(1, 2)
                if selection == 1:
                    #User wants to update discrepany in aml table
                    #We should allow a TEXT input to be added to the table
                    con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
                    cur = con.cursor() 
                    discrepancy = input("Enter the discrepancy or enter '0' to clear active discrepancy: ")
                    if input == 0:
                        sql = f"UPDATE aml set discrep = 'None' where tail = '{aircraft}'"
                    else:
                        sql = f"UPDATE aml set discrep = '{discrepancy}' where tail = '{aircraft}'"
                        cur.execute(sql)
                        con.commit()
                        con.close()
                    break
                if selection == 2:
                    break
    #Function to get the current AFTT and add this flight's flight time to it.
        def getTime():
            con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
            cur = con.cursor()
            sql = f"SELECT aftt from aml where tail = '{aircraft}'"
            cur.execute(sql)
            curtime = cur.fetchone()
            curtime = int(curtime[0])
            ftime = curtime+flight
            #print(ftime)
            con.commit()
            con.close()
            return ftime

        fob = getFuel()
        getDiscrep()
        ftime = getTime()
        print()
        print()
        con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
        cur = con.cursor()
        sql = f"UPDATE aml set location = '{arr}',fuel = '{fob}', AFTT = '{ftime}' where tail = '{aircraft}'"
        cur.execute(sql)

        con.commit()
        con.close()



        print("Flight logged successfully")
        input("Press Enter to continue: ")

                    
#Get's the type of approach the user flew
def get_approach():
    print()
    print()
    print("Please select type of approach flown: ")
    print("1: Visual")
    print("2: ILS")
    print("3: RNAV")
    print("4: GLS")
    print("5: LOC")
    print("6: VOR")
    print("7: LDA")
    print("8: NDB")
    print()
    appNum = get_num_input(1,8)
    approach = ''
    if appNum == 1:
        approach = 'VIS'
    if appNum == 2:
        approach = 'ILS'
    if appNum == 3:
        approach = 'RNAV'
    if appNum == 4:
        approach = 'GLS'
    if appNum == 5:
        approach = 'LOC'
    if appNum == 6:
        approach = 'VOR'
    if appNum == 7:
        approach = 'LDA'
    if appNum == 8:
        approach = 'NDB'
    return approach

#Takes user input for time to be out/off/on/in, validates it, and returns it.
def enter_time(timeString):
    while True:
        print()
        time = input(f"Please enter {timeString} time (zulu): ")
        if len(time) == 4:
            hours = time[0]
            hours = hours + time[1]
            minutes = time[2]
            minutes = minutes+time[3]
            timeIsNum = True
            timeIsValid = True
            #Need to verify that the time entered can be converted to ints
            try:
                hours = int(hours)
                minutes = int(minutes)

            except:
                timeIsNum = False
                print()
                print("Invalid time entered.  Please enter only numbers.")
                input("Press Enter to continue: ")
            #If numbers were entered, we can do some maths with the numbers to verify they are
            #valid times.  A Valid time should have less than 60 minutes, and less than 24 hours
            if timeIsNum:
                if hours > 24 or hours < 0 or minutes >= 60 or minutes < 0:
                    timeIsValid = False
                    print("Invalid time entered")
                    input("Press Enter to continue: ")
                if timeIsValid:
                    return time
        


        else:
            print("Invalid time entered (not enough/too many numbers).")
            print("Please be sure to enter 4 digits, including leading zeros")
            input("Press Enter to continue: ")

def calc_time(time1, time2):
    oneHrs = time1[0]
    oneHrs = oneHrs + time1[1]
    oneHrs = int(oneHrs)
    oneMins = time1[2]
    oneMins = oneMins+time1[3]
    oneMins = int(oneMins)

    twoHrs = time2[0]
    twoHrs = twoHrs + time2[1]
    twoHrs = int(twoHrs)
    twoMins = time2[2]
    twoMins = twoMins+time2[3]
    twoMins = int(twoMins)


    #Need to see if we went over midnight.  We know this if
    #time2 < time1, if so we need to add 24 hours to time2
    if twoHrs < oneHrs:
        twoHrs = twoHrs + 24
    #First let's subtract minutes
    #Need to make sure time 2's mins is greater than time 1
    #otherwise we need to borrow an hour from time 2 hrs
    if twoMins < oneMins:
        twoMins = twoMins+60
        twoHrs = twoHrs - 1
    #Now subtract the mins
    answerMins = twoMins - oneMins
    #now subtract hours
    answerHrs = twoHrs - oneHrs
    #Now convert minutes to a decimal by dividing by 60 and rounding
    #to the nearest tenth
    answerMins = round(answerMins/60, 1)
    answer = answerHrs+answerMins
    return answer


def view_logs():
    blankspace(10)
    allAircraft = get_all_aircraft()
    blankspace(10)
    print("Please select the tail number you would like to log a trip for:")
    print()
    count = 1
    for tail in allAircraft:
        print(f"{count}: {tail}")
        count += 1
    print(f"{count}: Go Back")
    print()
    selection = get_num_input(1, len(allAircraft) +1)
    if selection == len(allAircraft)+1:
        #return is useless, but it lets us immediately exit the function
        return False
    aircraft = allAircraft[selection-1]
    #Now that we have an aircraft, let's ask the user which trip they would like to view logs for
    trip = 0
    try:
        trip = int(input("Enter Trip Number you would like to view logs for: "))
    except:
        print("Please enter numbers only...")
        input("Press Enter to continue: ")
        return False
    #Let's make sure the trip the user wants to view actually exists
    con = sqlite3.connect('data/schedules/trips.db')
    cur = con.cursor()
    sql = f"SELECT * FROM {aircraft} WHERE num = {trip}"
    count = 0
    for row in cur.execute(sql):
        count += 1
    con.close()
    #If the trip exists, the count should be greater than zero, otherwise we should let the user know
    #and bug out by returning false
    if count == 0:
        print("Trip not found")
        input("Press Enter to continue: ")
        return False
    #Now let's connect to the aircrafts logbook db and pull up the trip.
    blankspace(10)
    flightTotal = 0
    con = sqlite3.connect(f'data/logbooks/{aircraft}.db')
    cur = con.cursor()
    sql = f"SELECT * FROM '{trip}'"
    print("Leg#    Dep    Arr    OUT   OFF  ON   IN   Flt Time   Block Time   Inst   App  Night   Pax")
    for row in cur.execute(sql):
        leg = row[0]
        dep = row[1]
        arr = row[2]
        out = row[3]
        off = row[4]
        on = row[5]
        inn = row[6]
        flight = row[7]
        block = row[8]
        inst = row[9]
        approach = row[10]
        night = row[11]
        pax = row[12]
        flightTotal = flightTotal + flight
        print(f"{leg}       {dep}    {arr}    {out}  {off} {on} {inn}    {flight}       {block}        {inst}    {approach}    {night}    {pax}")
    print()
    print()
    flightTotal = round(flightTotal, 1)
    print(f"Total Trip Flight Time: {flightTotal}")
    print()
    input("Press Enter to Continue: ")






    

#MAIN FUNCTION BELOW
########################
def main():
    while True:
        blankspace(10)
        print("Recordkeeping Main Menu")
        print()
        print()
        print("Select an option:")
        print("1: Log a completed flight")
        print("2: View logged flights")
        print("3: Go Back")
        selection = get_num_input(1,3)
        if selection == 3:
            break
        if selection == 2:
            view_logs()
        if selection == 1:
            log_flight()





