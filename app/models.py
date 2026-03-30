from sqlalchemy import Column, BigInteger, Text, TIMESTAMP, func, Numeric, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Employer(Base):
    __tablename__ = "employers"

    user_id = Column(BigInteger, primary_key=True, nullable=False)
    cash = Column(BigInteger, nullable=True)
    posting_counter = Column(BigInteger, nullable=True)
    help_message_counter = Column(BigInteger, nullable=True)
    user_name = Column(Text, nullable=True)
    reting_employer = Column(BigInteger, nullable=True)
    returns_counter = Column(BigInteger, nullable=True)
    registered_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)


class Support(Base):
    __tablename__ = "supp"

    sup_id = Column(BigInteger, primary_key=True, nullable=False)
    cost_view = Column(BigInteger, nullable=True)
    cost_week = Column(BigInteger, nullable=True)
    k_dscnt = Column(Numeric(3, 2), nullable=True)

class Postings(Base):
    __tablename__ = "postings"
    posting_id = Column(BigInteger, primary_key=True, nullable=False)
    user_id = Column(BigInteger, nullable=True)
    posting_text = Column(Text, nullable=True)
    view_counter = Column(BigInteger, nullable=True)
    accept_counter = Column(BigInteger, nullable=True)
    rejected_counter = Column(BigInteger, nullable=True)
    life_time_accept = Column(BigInteger, nullable=True)
    life_time_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=True)
    cost = Column(BigInteger, nullable=True)
    active = Column(BigInteger, nullable=True)
    cena = Column(BigInteger, nullable=True)
