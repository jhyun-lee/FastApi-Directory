from sqlalchemy import Column, Text, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(Text, nullable=False)
#     password = Column(Text, nullable=False)





class User(Base):
    __tablename__ = 'idDatabase'


    num = Column(Integer, primary_key=True, index=True)
    username = Column(Text, nullable=False)

    id = Column(Text, nullable=False)
    password = Column(Text, nullable=False)

    memo = Column(Text)