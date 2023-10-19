from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime
import uuid


class ReturnRecord(Base):
    """ Return Book Class """

    __tablename__ = "return_book"

    id = Column(Integer, primary_key=True)
    # Assuming user_id is a UUID, change the length accordingly
    user_id = Column(String(250), nullable=False)
    book_id = Column(String(250), nullable=False)
    return_date = Column(String(100), nullable=False)
    returner_name = Column(String(250), nullable=False)
    return_duration = Column(Integer, nullable=False)
    # Assuming late_fee is a floating-point number
    late_fee = Column(Float, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)

    def __init__(self, user_id, book_id, return_date, returner_name, return_duration, late_fee, trace_id):
        """ Initializes a return book record """
        self.user_id = user_id
        self.book_id = book_id
        self.return_date = return_date
        self.returner_name = returner_name
        self.return_duration = return_duration
        self.late_fee = late_fee
        # Sets the date/time record is created
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a return book record """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['book_id'] = self.book_id
        dict['return_date'] = self.return_date
        dict['returner_name'] = self.returner_name
        dict['return_duration'] = self.return_duration
        dict['late_fee'] = self.late_fee
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
