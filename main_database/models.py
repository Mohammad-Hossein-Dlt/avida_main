import uuid
from sqlalchemy import ForeignKey, Column, Text, Numeric, Boolean, Enum, Integer, BigInteger, DateTime, func
from main_database.database import Base


class Assistant(Base):
    __tablename__ = 'Assistant'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    DirectoryName = Column(Text, unique=True, nullable=False, default=lambda: uuid.uuid4().hex)
    Name = Column(Text, nullable=False)
    Image = Column(Text, nullable=True)
    Description = Column(Text, nullable=True)
    Prompt = Column(Text, nullable=True)
    Active = Column(Boolean, nullable=False, default=True)
    CreationDate = Column(DateTime, nullable=False, server_default=func.now())


class User(Base):
    __tablename__ = 'User'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    UserName = Column(Text, unique=True, default=lambda: uuid.uuid4().hex)
    Name = Column(Text, nullable=True)
    Phone = Column(Text, nullable=False)
    Password = Column(Text, nullable=True)
    CreationDate = Column(DateTime, nullable=False, server_default=func.now())


class UserTemp(Base):
    __tablename__ = 'UserTemp'
    Id = Column(BigInteger, primary_key=True, autoincrement=True)
    Phone = Column(Text, nullable=False)
    VerifyCode = Column(Text, nullable=False)
    ExpirationDate = Column(DateTime, nullable=False)
    CreationDate = Column(DateTime, nullable=False, server_default=func.now())
