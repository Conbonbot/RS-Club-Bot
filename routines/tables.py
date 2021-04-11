import itertools

from sqlalchemy.sql.sqltypes import SmallInteger

from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.orm import declarative_base, relationship, backref

from sqlalchemy import (Column, Text, Integer, Boolean, String, BigInteger, SmallInteger)

Base = declarative_base()

class Queue(Base):
    __tablename__ = 'queue'
    server_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    amount = Column(SmallInteger, primary_key=True)
    level = Column(SmallInteger, primary_key=True)
    time = Column(BigInteger)
    length = Column(Integer)
    channel_id = Column(BigInteger)

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

class Temp(Base):
    __tablename__ = 'temp'
    server_id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger, primary_key=True)
    amount = Column(SmallInteger)
    level = Column(SmallInteger)
