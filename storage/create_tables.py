import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS borrow_book
    (id INTEGER PRIMARY KEY ASC, 
     user_id VARCHAR(250) NOT NULL,
     book_id VARCHAR(250) NOT NULL,
     borrow_date VARCHAR(100) NOT NULL,
     borrower_name VARCHAR(250) NOT NULL,
     borrow_duration INTEGER NOT NULL,
     late_fee FLOAT NOT NULL,
     trace_id VARCHAR(36),  
     date_created VARCHAR(100) NOT NULL)
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS return_book
    (id INTEGER PRIMARY KEY ASC, 
     user_id VARCHAR(250) NOT NULL,
     book_id VARCHAR(250) NOT NULL,
     return_date VARCHAR(100) NOT NULL,
     returner_name VARCHAR(250) NOT NULL,
     return_duration INTEGER NOT NULL,
     late_fee FLOAT NOT NULL,
     trace_id VARCHAR(36),  
     date_created VARCHAR(100) NOT NULL)
''')

conn.commit()
conn.close()
