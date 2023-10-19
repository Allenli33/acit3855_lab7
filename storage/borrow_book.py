from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime
import uuid


class BorrowRecord(Base):
    """ Borrow Book Class """

    __tablename__ = "borrow_book"

    id = Column(Integer, primary_key=True)
    # Assuming user_id is a UUID, change the length accordingly
    user_id = Column(String(250), nullable=False)
    book_id = Column(String(250), nullable=False)
    borrow_date = Column(String(100), nullable=False)
    borrower_name = Column(String(250), nullable=False)
    borrow_duration = Column(Integer, nullable=False)
    # Assuming late_fee is a floating-point number
    late_fee = Column(Float, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)

    def __init__(self, user_id, book_id, borrow_date, borrower_name, borrow_duration, late_fee, trace_id):
        """ Initializes a borrow book record """
        self.user_id = user_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.borrower_name = borrower_name
        self.borrow_duration = borrow_duration
        self.late_fee = late_fee
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a borrow book record """
        dict = {}
        dict['id'] = self.id
        dict['user_id'] = self.user_id
        dict['book_id'] = self.book_id
        dict['borrow_date'] = self.borrow_date
        dict['borrower_name'] = self.borrower_name
        dict['borrow_duration'] = self.borrow_duration
        dict['late_fee'] = self.late_fee
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
