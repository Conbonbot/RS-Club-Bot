import itertools

from sqlalchemy.sql.sqltypes import INTEGER, SmallInteger, TIMESTAMP

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import declarative_base, relationship, backref

from sqlalchemy import (Column, Text, Integer, Boolean, String, BigInteger, SmallInteger, Time)

Base = declarative_base()

class Queue(Base):
    __tablename__ = 'queue'
    server_id = Column(BigInteger)
    user_id = Column(BigInteger, primary_key=True)
    amount = Column(SmallInteger, primary_key=True)
    level = Column(SmallInteger, primary_key=True)
    time = Column(BigInteger)
    length = Column(Integer)
    channel_id = Column(BigInteger)
    nickname = Column(Text)

class Data(Base):
    __tablename__ = 'data'
    user_id = Column(BigInteger, primary_key=True)
    croid = Column(Boolean)
    influence = Column(Boolean)
    nosanc = Column(Boolean)
    notele = Column(Boolean)
    rse = Column(Boolean)
    suppress = Column(Boolean)
    unity = Column(Boolean)
    veng = Column(Boolean)
    barrage = Column(Boolean)
    laser = Column(Boolean)
    battery = Column(Boolean)
    dart = Column(Boolean)
    solo = Column(Boolean)
    solo2 = Column(Boolean)
    mass = Column(Boolean)

class Temp(Base):
    __tablename__ = 'temp'
    server_id = Column(BigInteger)
    channel_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger, primary_key=True)
    amount = Column(SmallInteger)
    level = Column(SmallInteger)

class ExternalServer(Base):
    __tablename__ = 'externalserver'
    server_id = Column(BigInteger, primary_key=True)
    server_name = Column(Text)
    channel_id = Column(BigInteger)
    webhook = Column(Text)
    min_rs = Column(SmallInteger)
    max_rs = Column(SmallInteger)
    global_chat = Column(Boolean)
    rs5 = Column(BigInteger)
    rs6 = Column(BigInteger)
    rs7 = Column(BigInteger)
    rs8 = Column(BigInteger)
    rs9 = Column(BigInteger)
    rs10 = Column(BigInteger)
    rs11 = Column(BigInteger)

class Stats(Base):
    __tablename__= 'stats'
    user_id = Column(BigInteger, primary_key=True)
    timestamp = Column(BigInteger, primary_key=True)
    rs_level = Column(SmallInteger)
    run_id = Column(Integer)

class Event(Base):
    __tablename__ = 'event'
    run_id = Column(Integer, primary_key=True)
    score = Column(SmallInteger)
    timestamp = Column(BigInteger)

class Talking(Base):
    __tablename__ = 'talking'
    run_id = Column(Integer)
    server_id = Column(BigInteger)
    user_id = Column(BigInteger, primary_key=True)
    timestamp = Column(BigInteger)
    channel_id = Column(BigInteger)
    

    
    
