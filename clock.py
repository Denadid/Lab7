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
engine = create_engine('postgres://xuqqymsjxtdnvr:75ab50a3f24b78fc6bca57b53132af6e0cf5bb3d8421f079f8d0fe9e064dabc7@ec2-54-247-94-127.eu-west-1.compute.amazonaws.com:5432/dcep7u764ksdbe',echo=True)
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
    requests.get("https://telebotdenis.herokuapp.com/", params=params)

@sched.scheduled_job('interval', seconds=5)
def timed_job():
    session = Session()
    stgs = session.query(Settings).first()
    timering = session.query(Users).order_by(Users.last_ans.asc()).first()
    if timering is not None:
        if ((datetime.datetime.now()-datetime.datetime.strptime(timering.last_ans,'%Y-%m-%d %H:%M:%S.%f')) > datetime.timedelta(minutes=stgs.time)):
            params = {"chat_id": timering.User_id, "text": 'Я думаю пора позаниматься английским!',
                      'reply_markup': '{"keyboard": [["Начать игру"],["Отложить"]],"resize_keyboard":true}'}
            timering.last_word=''
            timering.last_position=-1
            timering.last_ans_count=0
            timering.last_ans = datetime.datetime.now()
            session.add(timering)
            session.commit()
            requests.get(URL + "/sendMessage", params=params)
    session.close()

sched.start()
