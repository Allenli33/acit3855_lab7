import mysql.connector

db_conn = mysql.connector.connect(host="allenliacit3855.eastus.cloudapp.azure.com", user="dbuser",
                                  password="Lh-729684251", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''
DROP TABLE borrow_book, return_book
''')
db_conn.commit()
db_conn.close()
