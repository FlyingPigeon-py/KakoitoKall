from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///users.db")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    status = Column(String)
    subscribe = Column(DateTime, nullable=True)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
