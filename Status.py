import sqlite3
from Schedule import get_active_trips
from Schedule import get_all_aircraft
from Schedule import get_legs_string
from Schedule import print_trip_summary
from Tools import blankspace
from Tools import get_num_input
from Tools import airport_distance


#Get a report on a single aircraft
def singleReport():
    allAircraft = get_all_aircraft()
    print("What aircraft would you like a status report on? ")
    print()
    count = 1

    for tail in allAircraft:
        print(f"{count}: {tail}")
        count += 1
    print(f"{count}: Go Back")
    print()
    selection = get_num_input(1, len(allAircraft)+1)
    if selection == len(allAircraft)+1:
        return False
        #this part is useless but allows us to leave the function
    aircraft = allAircraft[selection-1]
    #now let's connect to the fleet db and find the correct row to print!
    con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
    cur = con.cursor()
    sql = f"select * from aml where tail = '{aircraft}'"
    cur.execute(sql)
    for row in cur:
        print()
        print("Tail Number: ", row[0])
        print("Type: ", row[1])
        print("Location: ", row[2])
        print("Fuel on Board: ", row[3])
        print("Airframe TT: ", row[4])
        print("Discrepancies: ", row[5])
        print()
    con.close()





#Get a report on all aircraft at once    
def fleetReport():
    allAircraft = get_all_aircraft()
    print()
    count = 1

    #printing fleet report
    con = sqlite3.connect(f'data/mxlogbooks/fleet.db')
    cur = con.cursor()
    sql = f"select * from aml"
    cur.execute(sql)
    for row in cur:
        print()
        print()
        print("Tail Number: ", row[0])
        print("Type: ", row[1])
        print("Location: ", row[2])
        print("Fuel on Board: ", row[3])
        print("Airframe TT: ", row[4])
        print("Discrepancies: ", row[5])
        print()
    con.close()
    



# Main function below
def main():
    while True:
        blankspace(10)
        print()
        print("Would you like a report for every aircraft")
        print("or just a specific airframe?")
        print()
        print("1. Just a specific tail")
        print("2. Every airframe")
        print("3. Go back")
        print()
        selection = get_num_input(1,3)
        if selection == 1:
            singleReport()
        if selection == 2:
            fleetReport()
        if selection == 3:
            break

