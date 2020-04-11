import sqlite3
import datetime

conn = sqlite3.connect('example.db')

c = conn.cursor()
#
# c.execute('''CREATE TABLE Users
#              (User_id integer not null PRIMARY KEY, Name text, Last_ans text,last_ans_count integer,
#              last_position integer,last_try_count integer,last_word text)''')
#
# c.execute('''CREATE TABLE Learning
#              (ID_learning integer not null  PRIMARY KEY autoincrement ,User_id integer,word text,
#              count_ integer,last_ans text,FOREIGN KEY (User_id) references Users(User_id))''')
#
#
# conn.commit()
# conn.close()

chatID = 1
word = {}
word['word'] = 'super'
sdf=str(datetime.datetime.now())
asd=f"13132138475687136  5876134568"
print(type(asd))
print(type(sdf))
print(sdf)
#
c.execute(f''' INSERT INTO Learning (User_id, word, count_, last_ans) VALUES ({chatID},'super',1,
'{sdf}') ''')
conn.commit()
conn.close()

