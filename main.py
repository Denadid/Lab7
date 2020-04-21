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
engine = create_engine('postgres://enxkniceyqqomp:e191eb2cfd81e6311cb78104205e3fde97ebb8aab36e76013320bf34d6a9ff41@ec2-46-137-156-205.eu-west-1.compute.amazonaws.com:5432/d1e5a7pi1nolg1',echo=True)


Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()

TOKEN = "954911221:AAF12xXEVwl2KRsy1Qe0RvWcm-6bmd2MW7k"
URL = f"https://api.telegram.org/bot{TOKEN}"
getUpdates = URL + "/getUpdates"

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
        session = Session()
        user = Users(User_id=User_id, Name=Name, last_ans=last_ans, last_ans_count=last_ans_count,
                     last_position=last_position, last_try_count=last_try_count,last_word=last_word, mutex=mutex)
        print("Юзер в креате !:")
        print(user.Name)
        session.add(user)
        session.commit()
        print("Юзер в креате перед close !:")
        print(user.Name)
        session.close()
        print("тип юзера в креате перед ретурном !:")
        print(type(user))
        print("Юзер в креате перед ретурном !:")
        if user.Name is None:
            print("мы в жопе")
        else:    
            print(user)
        return user

    def Find(self,User_id):
        session = Session()
        FindUser = session.query(Users).filter_by(User_id=User_id).first()
        session.close()
        return FindUser

    def Update(self,User_id, last_ans=None, last_ans_count=None, last_position=None, last_try_count=None, last_word=None, mutex=None):
        session = Session()
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
        session.close()
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
        session = Session()
        learn = Learning(User_id=User_id, word=word, count_=count_, last_ans=last_ans)
        session.add(learn)
        session.commit()
        session.close()
        return learn

    def Find(self, User_id, word):
        session = Session()
        FindLearn = session.query(Learning).filter_by(User_id=User_id, word=word).first()
        session.close()
        return FindLearn

    def Update(self, User_id, word, count_=None, last_ans=None):
        session = Session()
        FindLearn = session.query(Learning).filter_by(User_id=User_id, word=word).first()
        if FindLearn is not None:
            if count_ is not None:
                FindLearn.count_ = count_
            if last_ans is not None:
                FindLearn.last_ans = last_ans
            session.add(FindLearn)
            session.commit()
        session.close()
        return FindLearn

Base.metadata.create_all(engine)
    
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
    print("Начало")
    session = Session()
    stgs = session.query(Settings).first()
    session.close()
    print("Получили Сеттингс")
    IsFind = False
    FindUser = ''
    FindUser = UsersDB.Find(User_id = chatID)
    print("Ищем юзера")
    if not FindUser:
        print("Создаем нового юзера")
        FindUser = UsersDB.Create(User_id=chatID,Name= FName)
        print(FindUser.Name)
        print(FindUser.mutex)
        print("Создали")
    print("Чекаем мутекс")
    print(FindUser.mutex)
    if FindUser.mutex != 0:
        print("Мутекс не ноль, выкинули запрос")
        return "end"
    else:
        print("Лочим мутекс обновляем пользователя в бд")
        FindUser = UsersDB.Update(chatID,mutex=1)
        print("Обновили")
    go_button = {"keyboard": [["Начать игру"],["Просмотр прогресса"]], "resize_keyboard": True}
    print("чек ласт позишона")
     print(FindUser.last_position)
    if text == '/start' and FindUser.last_position == -1:
        print("Реакция на СТАРТ")
        params["text"] = f'Привет {FName}, давай сыграем в игру, где я буду давать тебе какое-нибудь слово на ' \
                         f'английском, а ты в свою очередь будешь отгадывать его перевод. ' \
                         f'Всего будет {stgs.count} слов, после чего ты узнаешь сколько слов было отгадано. ' \
                         f'Не переживай, я буду тебе подсказывать, но только на английском хихи =)'
        params['reply_markup'] = json.dumps(go_button)
        requests.get(URL + "/sendMessage", params=params)
        print("Реакция на СТАРТ Конец")
    if text == '/start' and FindUser.last_position != -1:
        print("Освобождаем мутекс и выкидываем запрос из за повторного нажатия старт")
        FindUser = UsersDB.Update(chatID, mutex=0)
        print("Успешно")
        return Response(status=200)
    print(text)
    if text == "Отложить":
        print("Откладываем игру на потом, освобождаем мутекс")
        FindUser = UsersDB.Update(chatID, mutex=0)
        print("Готово")
        return "end"

    if text == "Начать игру" and FindUser.last_position == -1:
        print("Начинаем игру, обновляем БД юзера")
        FindUser = UsersDB.Update(User_id=FindUser.User_id,last_ans_count= 0,last_try_count=FindUser.last_try_count +1 ,last_position= 0)
        print("Обновили")
    if text == "Начать игру" and FindUser.last_position > 0:
        print("Повторная попытка начать игру, выкидываем запрос в мусорку")
        FindUser = UsersDB.Update(chatID, mutex=0)
        print("Выкинули")
        return Response(status=200)

    if FindUser.last_word != '' and FindUser.last_word is not None:
        word = ""
        for item in words:
            if item['word'] == FindUser.last_word:
                word = item
                break
        if text == "привести пример":
            params['text'] = random.choice(word['examples'])
            requests.get(URL + "/sendMessage", params=params)
            FindUser = UsersDB.Update(chatID, mutex=0)
            return 'end'
        else:
            if text== word['translation']:
                params['text'] = 'А ты молодец) Правильный ответ!'
                requests.get(URL + "/sendMessage", params=params, proxies=proxies)
                FindUser = UsersDB.Update(User_id=FindUser.User_id,
                               last_ans_count=(FindUser.last_ans_count+1),
                               last_ans = str(datetime.datetime.now()))
                count = LearningDB.Find(User_id= chatID,word = word['word'])
                if not count:
                    LearningDB.Create(User_id= chatID,word=word['word'],count_=1,last_ans=str(datetime.datetime.now()))
                else:
                    LearningDB.Update(User_id=chatID,word = word['word'],count_=count.count_+1,last_ans=str(datetime.datetime.now()) )
            else:
                params['text'] = f'К сожалению это неправильный ответ =( ' \
                                 f'На самом деле это: {word["translation"]}'
                requests.get(URL + "/sendMessage", params=params)
                FindUser = UsersDB.Update(User_id= chatID,last_ans= str(datetime.datetime.now()))

    if FindUser.last_position in range(0, stgs.count):
        isFind = False
        while not isFind:
            word = random.choice(words)
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

        FindUser = UsersDB.Update(User_id=chatID,last_word=word['word'], last_position=FindUser.last_position+1)
        requests.get(URL + "/sendMessage", params=params)
        FindUser = UsersDB.Update(chatID, mutex=0)
        return "end"
    if FindUser.last_position >= stgs.count:

        params["text"] = f'Игра закончена, {FName}, ты ответил(а) правильно на {FindUser.last_ans_count} из {stgs.count} возможных. ' \
                         f'Хочешь сыграть еще раз? =)'
        params['reply_markup'] = json.dumps(go_button)
        requests.get(URL + "/sendMessage", params=params)
        UsersDB.Update(User_id=chatID, last_word='', last_position=-1, last_ans_count=0)
        FindUser = UsersDB.Update(chatID, mutex=0)
        return "end"

    if text == "Просмотр прогресса":
        session = Session()
        learned_words = session.query(Learning).filter(Learning.count_ >= stgs.right).all()
        learning_words = session.query(Learning).filter(Learning.count_ < stgs.right).all()
        last_ans = FindUser.last_ans
        count_learned_words = len(learned_words)
        count_learning_words = len(learning_words)
        params['text'] = f'{FName}, ты находишься в разделе прогресса \n' \
                         f'Слов уже выучено: {count_learned_words} \n' \
                         f'Слов изучается: {count_learning_words} \n' \
                         f'Последнее время прохождения теста: \n' \
                         f'{last_ans}'
        session.close()
        requests.get(URL + "/sendMessage", params=params)
    FindUser = UsersDB.Update(chatID, mutex=0)
    return "end"

@app.route('/', methods=['GET'])
def index():
    return render_template("index.html")


@app.route('/settings')
def settings():
    session = Session()
    stgs = session.query(Settings).first()
    session.close()
    if stgs is not None: 
        return render_template("settings.html", time=stgs.time,count=stgs.count,right=stgs.right)
    else:
        return render_template("settings.html", time=2,count=2,right=2)

@app.route('/setup', methods=['POST'])
def setup():
    print("Start !!!!!!!!")
    session = Session()
    time = int(request.form.get('time'))
    count = int(request.form.get('count'))
    right = int(request.form.get('right'))
    stgs = session.query(Settings).first()
    if stgs is not None:
        stgs.time=time
        stgs.count=count
        stgs.right=right
        session.add(stgs)
        session.commit()
        print("Не Пустой сеттингс")
    else:
        stgsCr = Settings(id=1, time=time, count=count, right=right)
        session.add(stgsCr)
        session.commit()
        print("Пустой сеттингс")
    session.close()
    print("Done !!!!!!!!!!")
    return "Done"

if __name__ == '__main__':
    app.run();
