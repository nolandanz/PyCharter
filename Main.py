#Main function - runs the main menu and starts up the other various programs
#Starts with a while loop so that program doesn't exit unless user requests it.

import CharterSales
import Settings
import Schedule
import Recordkeeping
import Status
import sqlite3
from Tools import blankspace
from Tools import get_num_input
from Tools import tick
from Tools import refresh_quotes
from Settings import add_first_aircraft

#Checks for no aircraft.  If no aircraft in db, user must add aircraft to continue
def check_for_no_aircraft():
    con = sqlite3.connect('data/aircraft.db')
    cur = con.cursor()
    sql = "SELECT * FROM aircraft"
    count = 0
    for row in cur.execute(sql):
        count += 1
    if count == 0:
        #No aircraft yet, we need to have the user create one and we need to refresh quotes
        print("Welcome to PyCharter!")
        print("It looks like this is your first time running this program.")
        print("You'll need to add an aircraft to continue.")
        input("Press Enter to continue: ")
        add_first_aircraft()
        refresh_quotes()
        
    



#need to check for no aircraft in case this is a first run
check_for_no_aircraft()
print()
print()
tick()
while True:
    blankspace(10)
    print("Welcome to PyCharter!")
    print("Please select a below options")
    print()
    print("1. Charter Sales Module")
    print("2. Flight Scheduling Module")
    print("3. Recordkeeping")
    print("4. Settings")
    print("5. Advance Time")
    print("6. Status Report")
    print("7. Exit")
    print()
    selection = get_num_input(1,7)
    print()
    print()
    if selection == 1:
        CharterSales.main()
    if selection == 2:
        Schedule.main()
    if selection == 3:
        Recordkeeping.main()
    if selection == 4:
        Settings.main()
    if selection == 5:
        print("Advance time will answer your previously sent quotes, and refresh available quotes")
        adselect = input("Are you sure you want to continue?  (y/n): ")
        if adselect.lower() == 'y':
            tick()
    if selection == 6:
        Status.main()
    #Exit option
    if selection == 7:
        #Confirm user wants to exit.
        blankspace(10)
        confirm = input("Are you sure you want to Exit? (y/n): ")
        if confirm.lower() == 'y':
            exit()
    blankspace(10)
