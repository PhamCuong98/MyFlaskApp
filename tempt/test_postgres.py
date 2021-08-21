import psycopg2

#Establishing the connection
conn = psycopg2.connect(
   database="postgres", 
   user='postgres', 
   password='ngoccuong1812', 
   host='127.0.0.1', 
   port= '5432'
)
#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Preparing SQL queries to INSERT a record into the database.
cursor.execute('''INSERT INTO users(name, username, email, password) VALUES ('Ramya', 'Rama priya', 'asdsdasdadsdasd', '123456')''')

# Commit your changes in the database
conn.commit()
print("Records inserted........")

# Closing the connection
conn.close()