from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from models import Aluno, Carteirinha

from models import Base

engine = create_engine("sqlite:///studentidbank.db")


# Cria uma sessão
Session = sessionmaker(bind=engine)
session = Session()


# Cria as tabelas
Base.metadata.create_all(bind=engine)
