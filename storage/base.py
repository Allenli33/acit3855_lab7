from sqlalchemy.ext.declarative import declarative_base
# Import the necessary SQLAlchemy modules for defining the column
from sqlalchemy import Column, String


Base = declarative_base()

# Add the trace_id column to the Base class


class BaseModel(Base):
    # This marks this class as abstract and will not create a table for it in the database
    __abstract__ = True

    # Define the trace_id column
    trace_id = Column(String(36))
