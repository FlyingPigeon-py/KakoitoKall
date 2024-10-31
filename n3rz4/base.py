from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Integer, String, create_engine
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
    requests = Column(Integer, default=15)
    last_request_time = Column(DateTime, nullable=True)
    last_reset_date = Column(DateTime, nullable=True)

    def can_make_request(self):
        now = datetime.now()
        self.reset_daily_request_limit()
        time_until_reset = self.get_time_until_reset()
        if self.requests <= 0:
            return {
                "can_request": False,
                "time_until_next_request": None,
                "time_until_reset": time_until_reset,
            }
        if self.last_request_time:
            time_since_last_request = now - self.last_request_time
            time_until_next_request = timedelta(minutes=5) - time_since_last_request

            if time_until_next_request > timedelta(0):
                return {
                    "can_request": False,
                    "time_until_next_request": time_until_next_request,
                    "time_until_reset": time_until_reset,
                }
        self.last_request_time = now
        session.add(self)
        session.commit()

        return {
            "can_request": True,
            "time_until_next_request": timedelta(minutes=5),
            "time_until_reset": time_until_reset,
            "message": "Запрос выполнен успешно",
        }

    def set_last_request_time(self):
        now = datetime.now()
        self.last_request_time = now
        session.add(self)
        session.commit()

    def get_requests(self):
        return self.reset_daily_request_limit()

    def spend_request(self):
        self.requests -= 1
        if self.requests < 0:
            self.requests = 0
        session.add(self)
        session.commit()

    def get_time_until_reset(self):
        now = datetime.now()
        next_reset_date = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        return next_reset_date - now

    def reset_daily_request_limit(self):
        now = datetime.now()

        if not self.last_reset_date or self.last_reset_date.date() < now.date():
            self.requests = 15
            self.last_reset_date = now.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            session.add(self)
            session.commit()

        return self.requests


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
