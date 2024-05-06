import mysql.connector

# MySQL connection parameters
db_conn = mysql.connector.connect(host="ec2-44-230-165-6.us-west-2.compute.amazonaws.com", user="dbuser",
                                  password="Lh-729684251", database="events")

db_cursor = db_conn.cursor()

# Define SQL statements
create_borrow_book_table = '''
CREATE TABLE IF NOT EXISTS borrow_book (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(250) NOT NULL,
    book_id VARCHAR(250) NOT NULL,
    borrow_date VARCHAR(100) NOT NULL,
    borrower_name VARCHAR(250) NOT NULL,
    borrow_duration INTEGER NOT NULL,
    late_fee FLOAT NOT NULL,
    trace_id VARCHAR(36) NOT NULL,
    date_created VARCHAR(100) NOT NULL
)
'''

create_return_book_table = '''
CREATE TABLE IF NOT EXISTS return_book (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(250) NOT NULL,
    book_id VARCHAR(250) NOT NULL,
    return_date VARCHAR(100) NOT NULL,
    returner_name VARCHAR(250) NOT NULL,
    return_duration INTEGER NOT NULL,
    late_fee FLOAT NOT NULL,
    trace_id VARCHAR(36) NOT NULL,
    date_created VARCHAR(100) NOT NULL
)
'''

# Execute the SQL statements to create tables
db_cursor.execute(create_borrow_book_table)
db_cursor.execute(create_return_book_table)

# Commit the changes and close the cursor and connection
db_conn.commit()
db_conn.close()
