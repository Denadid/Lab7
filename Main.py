from flask import Flask, Response
from flask import request
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import requests
import json
import random
import datetime

app = Flask(__name__)
Base = declarative_base()
engine = create_engine('sqlite:///example.db',connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)

Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()

TOKEN = "954911221:AAF12xXEVwl2KRsy1Qe0RvWcm-6bmd2MW7k"
URL = f"https://api.telegram.org/bot{TOKEN}"
getUpdates = URL + "/getUpdates"
proxies = {
    'http': '96.96.36.118:3128',
    'https': '96.96.36.118:3128'
}

with open('english_words.json', 'r', encoding='utf-8') as j:
    words = json.load(j)

with open("keyboard.json", 'r', encoding='utf-8') as kf:
    reply_markup = json.load(kf)

random.seed(version=2)
questions = []


class Settings(Base):
    __tablename__ = 'Settings'
    id = Column(Integer, primary_key=True)
    time = Column(Integer, nullable=True)
    count = Column(Integer, nullable=True)
    right = Column(Integer, nullable=True)



class Users(Base):
    __tablename__ = 'Users'
    User_id = Column(Integer, primary_key=True)
    Name = Column(String(50), nullable=False)
    last_ans = Column(String(50), nullable=True)
    last_ans_count = Column(Integer, nullable=True)
    last_position = Column(Integer, nullable=True)
    last_try_count = Column(Integer, nullable=True)
    last_word = Column(String(50), nullable=True)
    mutex = Column(Integer, nullable=True)

    def Create(self, User_id, Name, last_ans=None, last_ans_count=None, last_position=-1, last_try_count=0, last_word='', mutex=0):
        user = Users(User_id=User_id, Name=Name, last_ans=last_ans, last_ans_count=last_ans_count,
                     last_position=last_position, last_try_count=last_try_count,last_word=last_word, mutex=mutex)
        session.add(user)
        session.commit()
        return user

    def Find(self,User_id):
        FindUser = session.query(Users).filter_by(User_id=User_id).first()
        return FindUser

    def Update(self,User_id, last_ans=None, last_ans_count=None, last_position=None, last_try_count=None, last_word=None, mutex=None):
        FindUser = session.query(Users).filter_by(User_id=User_id).first()
        if FindUser is not None:
            if last_ans is not None:
                FindUser.last_ans = last_ans
            if last_ans_count is not None:
                FindUser.last_ans_count = last_ans_count
            if last_position is not None:
                FindUser.last_position = last_position
            if last_try_count is not None:
                FindUser.last_try_count = last_try_count
            if last_word is not None:
                FindUser.last_word = last_word
            if mutex is not None:
                FindUser.mutex = mutex
            session.add(FindUser)
            session.commit()
        return FindUser

class Learning(Base):
    __tablename__ = 'Learning'
    ID_learning = Column(Integer, primary_key=True)
    User_id = Column(Integer, ForeignKey('Users.User_id'))
    word = Column(String(50), nullable=True)
    count_ = Column(Integer, nullable=True)
    last_ans = Column(String(50), nullable=True)
    user_id = relationship(Users)

    def Create(self, User_id, word, count_, last_ans):
        learn = Learning(User_id=User_id, word=word, count_=count_, last_ans=last_ans)
        session.add(learn)
        session.commit()
        return learn

    def Find(self, User_id, word):
        FindLearn = session.query(Learning).filter_by(User_id=User_id, word=word).first()
        return FindLearn

    def Update(self, User_id, word, count_=None, last_ans=None):
        FindLearn = session.query(Learning).filter_by(User_id=User_id, word=word).first()
        if FindLearn is not None:
            if count_ is not None:
                FindLearn.count_ = count_
            if last_ans is not None:
                FindLearn.last_ans = last_ans
            session.add(FindLearn)
            session.commit()
        return FindLearn

UsersDB = Users()
LearningDB = Learning()

@app.route('/incoming', methods=['POST', 'GET'])
def incoming():
    if request.method == 'POST':
        result = request.json
    massage = result["message"]
    chat = massage["chat"]
    chatID = chat["id"]
    text = massage["text"]
    FName = chat["first_name"]
    LName = chat["last_name"]
    params = {
        "chat_id": chatID,
        "text": ''
    }
    stgs = session.query(Settings).first()
    #return Response(status=200)
    #Session = sessionmaker(bind=engine)
    #session = Session()
    IsFind = False
    FindUser = ''
    # FindUser = query.execute(f''' Select* from Users where User_id = {chatID} ''').fetchone()
    FindUser = UsersDB.Find(User_id = chatID)
    if not FindUser:
        # query.execute(f''' INSERT INTO Users  VALUES ({chatID},'{FName}',null,null,-1,0,null) ''')
        FindUser = UsersDB.Create(User_id=chatID,Name= FName)
        # conn.commit()
        # FindUser = query.execute(f''' Select* from Users where User_id = {chatID} ''').fetchone()
    if FindUser.mutex != 0:
        return "end"
    else:
        FindUser = UsersDB.Update(chatID,mutex=1)
    go_button = {"keyboard": [["Начать игру"],["Просмотр прогресса"]], "resize_keyboard": True}
    if text == '/start' and FindUser.last_position == -1:
        params["text"] = f'Привет {FName}, давай сыграем в игру, где я буду давать тебе какое-нибудь слово на ' \
                         f'английском, а ты в свою очередь будешь отгадывать его перевод. ' \
                         f'Всего будет {stgs.count} слов, после чего ты узнаешь сколько слов было отгадано. ' \
                         f'Не переживай, я буду тебе подсказывать, но только на английском хихи =)'
        params['reply_markup'] = json.dumps(go_button)
        requests.get(URL + "/sendMessage", params=params, proxies=proxies)
    if text == '/start' and FindUser.last_position != -1:
        FindUser = UsersDB.Update(chatID, mutex=0)
        return Response(status=200)
    print(text)
    if text == "Отложить":
        FindUser = UsersDB.Update(chatID, mutex=0)
        return "end"

    if text == "Начать игру" and FindUser.last_position == -1:

        # query.execute(f'''UPDATE Users SET  last_ans_count = 0,
        #                                     last_try_count = {FindUser[5] + 1},
        #                                     last_position = 0
        #                                     WHERE User_id = {FindUser[0]}''')
        FindUser = UsersDB.Update(User_id=FindUser.User_id,last_ans_count= 0,last_try_count=FindUser.last_try_count +1 ,last_position= 0)
        # conn.commit()
    if text == "Начать игру" and FindUser.last_position > 0:
        FindUser = UsersDB.Update(chatID, mutex=0)
        return Response(status=200)

    if FindUser.last_word != '' and FindUser.last_word is not None:
        word = ""
        for item in words:
            if item['word'] == FindUser.last_word:
                word = item
                break
        if text == "привести пример":
            params['text'] = random.choice(word['examples'])
            requests.get(URL + "/sendMessage", params=params, proxies=proxies)
            FindUser = UsersDB.Update(chatID, mutex=0)
            return 'end'
        else:
            if text== word['translation']:
                params['text'] = 'А ты молодец) Правильный ответ!'
                requests.get(URL + "/sendMessage", params=params, proxies=proxies)

                # query.execute(f'''UPDATE Users SET last_ans = '{str(datetime.datetime.now())}',
                #                                    last_ans_count = {FindUser[3]+1},
                #                                    last_position = {FindUser[4]+1}
                #                                    WHERE User_id = {FindUser[0]}''')
                FindUser = UsersDB.Update(User_id=FindUser.User_id,
                               last_ans_count=(FindUser.last_ans_count+1),
                               last_ans = str(datetime.datetime.now()))
                # conn.commit()

                # count = query.execute(f''' Select *
                #                    FROM Learning
                #                    WHERE User_id = {chatID}
                #                    AND word = '{word['word']}'
                #                    ''').fetchone()
                count = LearningDB.Find(User_id= chatID,word = word['word'])
                if not count:
                    # query.execute(f''' INSERT INTO Learning(User_id, word, count_, last_ans) VALUES ({chatID},'{word['word']}',1,'{str(datetime.datetime.now())}') ''')
                    # conn.commit()
                    LearningDB.Create(User_id= chatID,word=word['word'],count_=1,last_ans=str(datetime.datetime.now()))
                else:
                    # query.execute(f'''UPDATE Learning SET count_ = {count[3]+1},
                    #                                       last_ans = '{str(datetime.datetime.now())}'
                    #                                       WHERE ID_learning = {count[0]}''')
                    # conn.commit()
                    LearningDB.Update(User_id=chatID,word = word['word'],count_=count.count_+1,last_ans=str(datetime.datetime.now()) )
            else:
                params['text'] = f'К сожалению это неправильный ответ =( ' \
                                 f'На самом деле это: {word["translation"]}'
                requests.get(URL + "/sendMessage", params=params, proxies=proxies)

                # query.execute(f'''UPDATE Users SET last_ans = '{str(datetime.datetime.now())}',
                #                                                    last_position = {FindUser[4]+1}
                #                                                    WHERE User_id = {FindUser[0]}''')
                # conn.commit()
                FindUser = UsersDB.Update(User_id= chatID,last_ans= str(datetime.datetime.now()))

    if FindUser.last_position in range(0, stgs.count):
        isFind = False
        while not isFind:
            word = random.choice(words)
            # count = query.execute(f''' Select *
            #                            FROM Learning
            #                            WHERE User_id = {chatID}
            #                            AND word = '{word['word']}'
            #                         ''').fetchone()
            count = LearningDB.Find(User_id= chatID,word = word['word'])
            if count and count.count_ < FindUser.last_ans_count-1 and count.count_ <= stgs.right:
                isFind = True
            if not count:
                isFind = True

        ansvers = []
        ansvers.append(word["translation"])
        n = 1
        while n < 4:
            wordIsFind = False
            get = random.choice(words)
            for var in ansvers:
                if var == get["translation"]:
                    wordIsFind = True
            if not wordIsFind:
                ansvers.append(get["translation"])
                n += 1
        random.shuffle(ansvers)
        reply_markup["keyboard"][0][0] = ansvers[0]
        reply_markup["keyboard"][0][1] = ansvers[1]
        reply_markup["keyboard"][1][0] = ansvers[2]
        reply_markup["keyboard"][1][1] = ansvers[3]
        params['reply_markup'] = json.dumps(reply_markup)
        params['text'] = word['word']

        # query.execute(f'''UPDATE Users SET last_word = '{word['word']}'
        #                                WHERE User_id = {FindUser[0]}''')
        # conn.commit()
        # FindUser = query.execute(f''' Select* from Users where User_id = {chatID} ''').fetchone()
        FindUser = UsersDB.Update(User_id=chatID,last_word=word['word'], last_position=FindUser.last_position+1)
        requests.get(URL + "/sendMessage", params=params, proxies=proxies)
        FindUser = UsersDB.Update(chatID, mutex=0)
        return "end"
    if FindUser.last_position >= stgs.count:
        # query.execute(f'''UPDATE Users SET last_ans_count = 0,
        #                                last_position = -1,
        #                                last_word = null
        #                                WHERE User_id = {FindUser[0]}''')
        # conn.commit()

        params["text"] = f'Игра закончена, {FName}, ты ответил(а) правильно на {FindUser.last_ans_count} из {stgs.count} возможных. ' \
                         f'Хочешь сыграть еще раз? =)'
        params['reply_markup'] = json.dumps(go_button)
        requests.get(URL + "/sendMessage", params=params, proxies=proxies)
        UsersDB.Update(User_id=chatID, last_word='', last_position=-1, last_ans_count=0)
        FindUser = UsersDB.Update(chatID, mutex=0)
        return "end"

    if text == "Просмотр прогресса":
        # learned_words = query.execute(f'''SELECT * FROM Learning WHERE count_ >= {max_level}''').fetchall()
        learned_words = session.query(Learning).filter(Learning.count_ >= stgs.right).all()
        # learning_words = query.execute(f'''SELECT * FROM Learning WHERE count_ < {max_level}''').fetchall()
        learning_words = session.query(Learning).filter(Learning.count_ < stgs.right).all()
        last_ans = FindUser.last_ans
        count_learned_words = len(learned_words)
        count_learning_words = len(learning_words)
        params['text'] = f'{FName}, ты находишься в разделе прогресса \n' \
                         f'Слов уже выучено: {count_learned_words} \n' \
                         f'Слов изучается: {count_learning_words} \n' \
                         f'Последнее время прохождения теста: \n' \
                         f'{last_ans}'
        requests.get(URL + "/sendMessage", params=params, proxies=proxies)
    FindUser = UsersDB.Update(chatID, mutex=0)
    return "end"

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/settings')
def settings():
    stgs = session.query(Settings).first()
    return render_template("settings.html", time=stgs.time,count=stgs.count,right=stgs.right)


@app.route('/setup', methods=['POST'])
def setup():
    time = int(request.form.get('time'))
    count = int(request.form.get('count'))
    right = int(request.form.get('right'))
    stgs = session.query(Settings).first()
    stgs.time=time
    stgs.count=count
    stgs.right=right
    session.add(stgs)
    session.commit()
    return "200"

if __name__ == '__main__':
    app.run();
