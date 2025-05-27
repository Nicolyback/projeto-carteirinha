from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cria a base para os modelos
Base = declarative_base()

# Cria o engine de conexão com o banco SQLite
engine = create_engine("sqlite:///studentidbank.db", echo=True)

# Cria a sessão
Session = sessionmaker(bind=engine)
session = Session()

# Importa os modelos (Aluno e Carteirinha) para que as tabelas sejam registradas
from models import Aluno, Carteirinha

def init_db():
    print(">> Criando tabelas...")
    Base.metadata.create_all(bind=engine)

