from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, DateTime, Boolean
from datetime import datetime

Base = declarative_base()

class Carteirinha(Base):
    __tablename__ = 'carteirinhas'

    id = Column("id", Integer, primary_key=True)
    aluno_matricula = Column("aluno_matricula", Integer, ForeignKey("alunos.matricula"), nullable=False)
    email = Column(String, nullable=False)
    validade = Column("validade", Date, nullable=False)
    status = Column("status", String, default='Ativo')
    caminho_foto = Column("caminho_foto", Text)
    pdf_gerado = Column("pdf_gerado", Text)
    criado_em = Column("criado_em", DateTime, default=datetime.utcnow)

class Aluno(Base):
    __tablename__ = 'alunos'

    matricula = Column("matricula", Integer, primary_key=True)
    email = Column("email", String, nullable=False)
    nome = Column("nome", String, nullable=False)
