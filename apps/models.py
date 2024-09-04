from database import Base
import enum
from sqlalchemy import TIMESTAMP, Column,\
String, Integer, Boolean, Enum, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime


class UserRole(enum.Enum):
    student = 'student'
    driver = 'driver'
    admin = 'admin'


class TransactionType(enum.Enum):
    COMPLETED = 'completed'
    FAILED = 'failed'
    PENDING = 'pending'


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone_number = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # is_student = Column(Boolean, default=False)
    # is_driver = Column(Boolean, default=False)
    # is_admin = Column(Boolean, default=False)

    role = Column(Enum(UserRole))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    unique_no = Column(String, unique=True)
    # matric_no = Column(String, unique=True)

    wallet = relationship('Wallet', back_populates='owner', uselist=False, cascade='all, delete')
    activities = relationship('Activity', back_populates='owner', cascade='all, delete')

    # profile = relationship('DriverProfile', back_populates='owner', uselist=False)


    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


    @classmethod
    def get_user_by_id(cls, id, db):
        return db.query(cls).filter(cls.id==id).first()


    @classmethod
    def get_user_by_email(cls, email, db):
        user = db.query(cls).filter(cls.email==email).first()
        return user
    
    @classmethod
    def get_user_by_username(cls, username, db):
        user = db.query(cls).filter(cls.username==username).first()
        return user


# class DriverProfile(Base):
#     __tablename__ = 'driverprofiles'
#     id = Column(Integer, primary_key=True)
#     plate_number = Column(String, unique=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     owner = relationship('User', back_populates='profile')


# class StudentProfile(Base):
#     __tablename__ = 'studentprofiles'
#     id = Column(Integer, primary_key=True)
#     matric_number = Column(String, unique=True)
#     owner_id = Column(Integer, ForeignKey('users.id'))
#     owner = relationship('User', back_populates='profile')


class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    balance = Column(Numeric(precision=10, scale=2), default=0.00)
    owner_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())

    owner = relationship('User', back_populates='wallet')


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id'))
    to_user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric(precision=10, scale=2))
    description = Column(String)
    status = Column(Enum(TransactionType))
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

    from_user = relationship('User', foreign_keys=[from_user_id], backref='sent_transactions')
    to_user = relationship('User', foreign_keys=[to_user_id], backref='received_transactions')


    @classmethod
    def get_transactions_for_user(cls, session, user_id):
        sent_transactions = session.query(cls).filter(cls.from_user_id == user_id).all()
        received_transactions = session.query(cls).filter(cls.to_user_id == user_id).all()
        all_transactions = sent_transactions + received_transactions
        return sorted(all_transactions, key=lambda x: x.date, reverse=True)
    

    class DebitCard(Base):
        __tablename__ = 'debitcards'
        id = Column(Integer, primary_key=True)
        card_number = Column(String, unique=True)
        cvv = Column(String, unique=True)
        expiry_date = Column(String)
        owner_id = Column(Integer, ForeignKey('users.id'))

        owner = relationship('User', backref='debit_card')


    class Notification(Base):
        __tablename__ = 'notifications'
        id = Column(Integer, primary_key=True)
        description = Column(String)
        owner_id = Column(Integer, ForeignKey('users.id'))
        is_read = Column(Boolean, default=False)
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

        owner = relationship('User', backref='notifications')


    class Activity(Base):
        __tablename__ = 'activity'
        id = Column(Integer, primary_key=True)
        description = Column(String)
        owner_id = Column(Integer, ForeignKey('users.id'))
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())

        owner = relationship('User', back_populates='activities')


    class QRCode(Base):
        __tablename__ = 'QRcode'
        id = Column(Integer, primary_key=True)
        qr_code_data = Column(String)
        driver_id = Column(Integer, ForeignKey('users.id'))
        created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=func.now())   
