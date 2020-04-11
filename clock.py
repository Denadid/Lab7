from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import relationship
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask, Response
from flask import request
import requests
from datetime import date
import datetime

Base = declarative_base()
engine = create_engine('sqlite:///example.db',connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)

TOKEN = "954911221:AAF12xXEVwl2KRsy1Qe0RvWcm-6bmd2MW7k"
URL = f"https://api.telegram.org/bot{TOKEN}"
getUpdates = URL + "/getUpdates"

Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()

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

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=30)
def timed_job1():
    params = {"text": 'Не спать!'}
    print('Не спать!')
    requests.get("https://65db1cf0.ngrok.io", params=params)

@sched.scheduled_job('interval', minutes=1)
def timed_job():
    stgs = session.query(Settings).first()
    timering = session.query(Users).order_by(Users.last_ans.asc()).first()
    if timering is not None:
        if ((datetime.datetime.now()-datetime.datetime.strptime(timering.last_ans,'%Y-%m-%d %H:%M:%S.%f')) > datetime.timedelta(minutes=stgs.time)):
            params = {"chat_id": timering.User_id, "text": 'Я думаю пора позаниматься английским!',
                      'reply_markup': '{"keyboard": [["Начать игру"],["Отложить"]],"resize_keyboard":true}'}
            timering.last_word=''
            timering.last_position=-1
            timering.last_ans_count=0
            session.add(timering)
            session.commit()
            requests.get(URL + "/sendMessage", params=params)


sched.start()
