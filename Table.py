
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("mysql://root:#sqlpassword@localhost:3306/collegeproject")
Session = sessionmaker(bind=engine)
session = Session()

class File(Base):
    __tablename__ = 'file'
    id= Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    token = Column(String(16), unique=True, nullable=False)

class User(Base):
    __tablename__ = 'user'
    id=Column(Integer,primary_key=True)
    username=Column(String(255),nullable=False)
    password=Column(String(16),unique=True,nullable=False)
    emailid=Column(String(255),nullable=False)

Base.metadata.create_all(engine)