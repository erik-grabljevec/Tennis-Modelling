'''
Script that builds whole database.
Set database connection information in file: settings.py
Read about database structure in docs.
Data is scrapped from next two sources:
- http://www.tennis-data.co.uk/alldata.php
- https://github.com/JeffSackmann/tennis_atp
'''

START_YEAR = 2003
END_YEAR = 2015


__author__ = 'riko'


import _mysql_exceptions
import MySQLdb
import xlrd

import settings as stg


################################################################################
#     Set-up database connection.                                              #
################################################################################


try:
    db_data = stg.MYSQL_SETTINGS
except AttributeError:
    print "Could not load the database settings! Make sure you set them in settings.py"
    raise

# Establish a MySQL connection.
database = MySQLdb.connect(**db_data)
database.set_character_set('utf8')

# Get the cursor and set UTF8 format.
cursor = database.cursor()
cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')


################################################################################
#     Functions.                                                               #
################################################################################


def add_id_to_table(table_name):
    '''
    Add Id column to table.

    :param table_name: Name of table we want to add ID to.
    :return: void.
    '''

    cursor.execute("ALTER TABLE %s ADD id MEDIUMINT NOT NULL AUTO_INCREMENT KEY" % table_name)
    cursor.execute("ALTER TABLE %s DROP primary key, add primary key(Id)" % table_name)


def drop_table(table_name):
    '''
    This function tries to drop table with name 'table_name'.

    :param table_name: Name of table we are trying to drop.
    :return: void.
    '''

    query = "DROP TABLE %s" % table_name
    try:
        cursor.execute(query)
    except _mysql_exceptions.OperationalError:
        print "Table %s doesn't exist yet!" % table_name


def get_short_name(name):
    '''
    This function is used to find shortened versions of names. We need them
    to join data with different name formats.

    :param name: Name of player we want to shorten.
    :return: Shortened name of a player.
    '''

    keep = ["De", "Del", "Estrella", "Huta"]

    name_split = name.split()
    if name_split[-2] in keep:
        begin = " ".join(name_split[-2:])
        name_split = name_split[:-2]
    else:
        begin = name_split[-1]
        name_split = name_split[:-1]

    end = " " + ".".join([x[0] for x in name_split]) + "."

    return begin + end


def parse_tennis_data(year):
    '''
    Long function that parses two excel files. It first parses each of them
    seperately and then combines them together.
    Very ugly, but no other way than to hard code it.

    :param year: Parse one year of data from .xls and .csv files.
    :return: void.
    '''

    # FIRST PART - get data from .xls file.

    year = str(year)
    excel_dir = stg.ROOT_PATH + "data/tennis_betting/" + year + ".xls"

    # Open the workbook and define the worksheet.
    book = xlrd.open_workbook(excel_dir)
    sheet = book.sheet_by_name(year)

    query = """
            CREATE TABLE temp_a
            (
            Location VARCHAR (255),
            Tournament VARCHAR (255),
            Date INT,
            Surface VARCHAR (255),
            Length INT ,
            Winner VARCHAR (255),
            Loser VARCHAR (255),
            Winner_points INT,
            Loser_points INT,
            Winner_odds FLOAT,
            Loser_odds FLOAT
            );
            """

    drop_table("temp_a")
    cursor.execute(query)

    query = """INSERT INTO temp_a (Location, Tournament, Date, Surface, Length, Winner, Loser, Winner_points, Loser_points, Winner_odds, Loser_odds) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    for r in xrange(1, sheet.nrows):
        location = sheet.cell(r,1).value
        tournament = sheet.cell(r,2).value
        date = sheet.cell(r,3).value
        surface = sheet.cell(r,6).value
        length = sheet.cell(r,8).value
        winner = sheet.cell(r,9).value
        loser = sheet.cell(r,10).value
        winner_points = sheet.cell(r,25).value
        loser_points =  sheet.cell(r,26).value
        winner_odds = 1.0
        loser_odds = 1.0
        for i in range(5):
            try:
                other_win = float(str(sheet.cell(r,28+2*i).value))
                other_lose = float(str(sheet.cell(r,29+2*i).value))
            except ValueError:
                other_win = 1.0
                other_lose = 1.0

            winner_odds = max(winner_odds, other_win)
            loser_odds = max(loser_odds, other_lose)

        values = (location, tournament, date, surface, length, winner, loser, winner_points, loser_points, winner_odds, loser_odds)

        cursor.execute(query, values)

    # SECOND PART - get data from .csv file

    query = """
        CREATE TABLE temp_b
        (
        Tournament VARCHAR (255),
        Surface VARCHAR (255),
        Size INT,
        Level VARCHAR (255),
        Date DATE,

        Winner VARCHAR (255),
        Winner_short VARCHAR (255),
        Winner_hand VARCHAR (255),
        Winner_ioc VARCHAR (255),
        Winner_rank VARCHAR (255),

        Loser VARCHAR (255),
        Loser_short VARCHAR (255),
        Loser_hand VARCHAR (255),
        Loser_ioc VARCHAR (255),
        Loser_rank VARCHAR (255),

        Score VARCHAR (255),
        Best_of INT,
        Round VARCHAR (255),
        Minutes INT,

        W_sv INT,
        W_1stIn INT,
        W_ace INT,
        W_1stWon INT,
        W_2ndWon INT,

        L_sv INT,
        L_1stIn INT,
        L_ace INT,
        L_1stWon INT,
        L_2ndWon INT
        );
        """

    drop_table("temp_b")
    cursor.execute(query)

    excel_dir = stg.ROOT_PATH + "data/tennis_atp/atp_matches_" + year + ".csv"

    query = """INSERT INTO temp_b (Tournament, Surface, Size, Level, Date, Winner, Winner_short, Winner_hand, Winner_ioc, Winner_rank, Loser, Loser_short, Loser_hand, Loser_ioc, Loser_rank, Score, Best_of, Round, Minutes, W_sv, W_1stIn, W_ace, W_1stWon, W_2ndWon, L_sv, L_1stIn, L_ace, L_1stWon, L_2ndWon) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    with open(excel_dir) as f:
        lines = f.readlines()

        for line in lines[1:]:
            values = line.split(",")

            Tournament = values[1]
            Surface = values[2]
            Size = values[3]
            Level = values[4]
            Date = values[5]

            Winner = values[10]
            Winner_short = get_short_name(Winner)
            Winner_hand = values[11]
            Winner_ioc = values[13]
            Winner_rank = values[15]

            Loser = values[20]
            Loser_short = get_short_name(Loser)
            Loser_hand = values[21]
            Loser_ioc = values[23]
            Loser_rank = values[25]

            Score = values[27]
            Best_of = values[28]
            Round = values[29]
            Minutes = values[30]

            W_sv = values[33]
            W_1stIn = values[34]
            W_ace = values[31]
            W_1stWon = values[35]
            W_2ndWon = values[36]

            L_sv = values[42]
            L_1stIn = values[43]
            L_ace = values[40]
            L_1stWon = values[44]
            L_2ndWon = values[45]

            values = (Tournament, Surface, Size, Level, Date, Winner, Winner_short, Winner_hand, Winner_ioc, Winner_rank, Loser, Loser_short, Loser_hand, Loser_ioc, Loser_rank, Score, Best_of, Round, Minutes, W_sv, W_1stIn, W_ace, W_1stWon, W_2ndWon, L_sv, L_1stIn, L_ace, L_1stWon, L_2ndWon)

            cursor.execute(query, values)

    # COMBINE BOTH TABLES
    query = '''
            CREATE TABLE new_table
            AS
            SELECT b.Location, a.Tournament, a.Level, a.Surface, a.Size, a.Date, a.Winner, a.Winner_hand, a.Winner_ioc, a.Winner_rank, a.Loser, a.Loser_short, a.Loser_hand, a.Loser_ioc, a.Loser_rank, a.Score, a.Best_of, a.Round, a.Minutes, a.W_sv, a.W_1stIn, a.W_ace, a.W_1stWon, a.W_2ndWon, a.L_sv, a.L_1stIn, L_ace, L_1stWon, L_2ndWon, b.Winner_odds, b.Loser_odds
            FROM tennis.temp_b a
            LEFT JOIN tennis.temp_a b
            ON a.Tournament=b.Tournament AND a.Winner_short=b.Winner AND a.Loser_short=b.Loser;
            '''

    drop_table("new_table")
    cursor.execute(query)


################################################################################
#     Building database step by step.                                          #
################################################################################


# CREATE TABLE base
print "Starting table 'Base' creation."

for year in xrange(START_YEAR, END_YEAR + 1):
    print "Parsing year %s." % year

    parse_tennis_data(year)

    if year == START_YEAR:
        drop_table("Base")
        cursor.execute("CREATE TABLE Base LIKE new_table")

    cursor.execute("INSERT INTO Base SELECT * FROM new_table")

# Adding ID to base table.
add_id_to_table("Base")

# Clear unneeded tables.
print "Table 'Base' done! Clearing left over tables."
drop_table("temp_a")
drop_table("temp_b")
drop_table("new_table")

# CREATE TABLE players
print "Starting table 'Players' creation."

drop_table("Players")

query = '''
        CREATE TABLE Players
        SELECT Winner as Name, Winner_hand as Hand, Winner_ioc as Country
        FROM Base
        GROUP BY Winner, Winner_hand, Winner_ioc
        UNION
        SELECT Loser, Loser_hand, Loser_ioc
        FROM Base
        GROUP BY Loser, Winner_hand, Winner_ioc
        '''

cursor.execute(query)
add_id_to_table("Players")

# CREATE TABLE tournaments
print "Starting table 'Tounaments' creation."

query = '''
        CREATE TABLE Tournaments
        SELECT Tournament, Surface, Size, min(Date) as Date, Best_of
        FROM Base
        GROUP BY Tournament, Surface, Size, Best_of
        '''

drop_table("Tournaments")
cursor.execute(query)
add_id_to_table("Tournaments")

# CREATE TABLE games
print "Starting table 'Games' creation."
"""
query = '''
        CREATE TABLE Games
        SELECT p1.Id as Winner_ID, p2.Id as Loser_ID, t.Id as Tournament_ID, b.Score, b.Minutes
        FROM Base b
        LEFT JOIN Players p1
        ON b.Winner=p1.Name and b.Winner_hand=p1.Hand and b.Winner_ioc=p1.Country
        LEFT JOIN Players p2
        ON b.Loser=p2.Name and b.Loser_hand=p2.Hand and b.Loser_ioc=p2.Country
        LEFT JOIN Tournaments t
        ON b.Tournament=t.Tournament and b.Surface=t.Surface and b.Size=t.Size and b.Date=t.Date and b.Best_of=t.Best_of
        '''

drop_table("Games")
cursor.execute(query)
add_id_to_table("Games")
"""

print "ALL DONE. Closing cursor and database."
cursor.close()
database.commit()
database.close()