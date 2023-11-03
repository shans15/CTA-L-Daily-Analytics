import sqlite3
import matplotlib.pyplot as plt

##################################################################
#
# Function to execute SQL and return results
#
def execute_sql(db_conn, sql, parameters=None):
    db_cursor = db_conn.cursor()
    if parameters:
        db_cursor.execute(sql, parameters)
    else:
        db_cursor.execute(sql)
    rows = db_cursor.fetchall()
    db_cursor.close()
    return rows

##################################################################
#
# Command One
#
# Output all stations that correspond with the input string
#
def command_one(db_conn):
    print()
    user_input = input("Enter partial station name (wildcards _ and %): ")
    sql = "SELECT Station_id, Station_name FROM Stations WHERE Station_name LIKE ? GROUP BY Station_name ORDER BY Station_name;"
    rows = execute_sql(db_conn, sql, (user_input,))

    if rows:
        for station_id, name in rows:
            print(f"{station_id} : {name}")
    else:
        print("**No stations found...")

##################################################################
#
# Command Two
#
# Output all stations and their total number of riders
#
def command_two(db_conn):
    print("** ridership all stations **")
    sql = """
    SELECT station_name, SUM(ridership.num_riders), (SELECT SUM(num_riders) FROM ridership)
    FROM stations
    JOIN ridership ON stations.station_id = ridership.station_id
    GROUP BY station_name
    ORDER BY station_name ASC;
    """
    rows = execute_sql(db_conn, sql)

    for name, num_riders, total_riders in rows:
        percentage = num_riders * 100 / total_riders
        print(f"{name} : {num_riders:,} ({percentage:.2f}%)")

##################################################################
#
# Commands Three and Four (combined due to similarity)
#
# Output the top 10 busiest/least busiest stations by total number of riders
#
def command_three_four(db_conn, command):
    direction = 'DESC' if command == 3 else 'ASC'
    print(f"** top-10 stations **" if command == 3 else "** least-10 stations **")
    sql = f"""
    SELECT station_name, SUM(ridership.num_riders) as totRiders, (SELECT SUM(num_riders) FROM ridership)
    FROM stations
    JOIN ridership ON stations.station_id = ridership.station_id
    GROUP BY station_name
    ORDER BY totRiders {direction}
    LIMIT 10;
    """
    rows = execute_sql(db_conn, sql)

    for name, num_riders, total_riders in rows:
        percentage = num_riders * 100 / total_riders
        print(f"{name} : {num_riders:,} ({percentage:.2f}%)")

##################################################################
#
# Command Five
#
# Output stops for a given line color
#
def command_five(db_conn):
    print()
    user_input = input("Enter a line color (e.g. Red or Yellow): ").title().replace("Express", "-Express")
    sql = """
    SELECT stop_name, direction, ada
    FROM Stops
    JOIN StopDetails ON Stops.stop_id = StopDetails.stop_id
    JOIN Lines ON StopDetails.line_id = Lines.line_id
    WHERE Lines.color = ?
    GROUP BY stop_name
    ORDER BY stop_name;
    """
    rows = execute_sql(db_conn, sql, (user_input,))

    if rows:
        for stop_name, direction, ada in rows:
            accessible = "yes" if ada == 1 else "no"
            print(f"{stop_name} : direction = {direction} (accessible? {accessible})")
    else:
        print("**No such line...")

##################################################################
#
# Command Six
#
# Output number of riders by month and plotting it's graph
#
def command_six(db_conn):
    print("** ridership by month **")
    sql = "SELECT strftime('%m', ride_date) as months, SUM(num_riders) FROM ridership GROUP BY months ORDER BY months;"
    rows = execute_sql(db_conn, sql)

    if rows:
        riders_list = []
        month_list = []
        for month, num_riders in rows:
            print(f"{month} : {num_riders:,}")
            riders_list.append(num_riders)
            month_list.append(month)

        user_plot = input("Plot? (y/n) ")
        if user_plot.lower() == "y":
            plt.xlabel("Month")
            plt.ylabel("Number of riders")
            plt.title("Monthly Ridership")
            plt.plot(month_list, riders_list)
            plt.show()

##################################################################
#
def command_seven(db_conn):
    print("** ridership by year **")
    sql = "SELECT strftime('%Y', ride_date) as year, SUM(num_riders) FROM ridership GROUP BY year ORDER BY year;"
    rows = execute_sql(db_conn, sql)

    if rows:
        riders_list = []
        year_list = []
        for year, num_riders in rows:
            print(f"{year} : {num_riders:,}")
            riders_list.append(num_riders)
            year_list.append(year)

        user_plot = input("Plot? (y/n) ")
        if user_plot.lower() == "y":
            plt.xlabel("Year")
            plt.ylabel("Number of Riders")
            plt.title("Yearly Ridership")
            plt.bar(year_list, riders_list)
            plt.show()

##################################################################
#
# Main Program
#
def main():
    # Connect to the SQLite database
    db_conn = sqlite3.connect('cta_ridership.db')
    
    while True:
        print("""
        *** CTA Ridership Analysis ***
        1. List stations that match a partial name
        2. List stations by total ridership
        3. List top 10 busiest stations
        4. List top 10 least busy stations
        5. List stops for a line
        6. Monthly ridership figures
        7. Yearly ridership figures
        X. Exit
        """)
        
        command = input("Enter command: ")
        
        if command == '1':
            command_one(db_conn)
        elif command == '2':
            command_two(db_conn)
        elif command == '3':
            command_three_four(db_conn, 3)
        elif command == '4':
            command_three_four(db_conn, 4)
        elif command == '5':
            command_five(db_conn)
        elif command == '6':
            command_six(db_conn)
        elif command == '7':
            command_seven(db_conn)
        elif command.lower() == 'x':
            break
        else:
            print("Invalid command. Please try again.")

    # Close the database connection before exiting
    db_conn.close()

if __name__ == "__main__":
    main()

