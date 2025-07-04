from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, DateTime
from datetime import datetime
from database import Base  # Usa o Base criado em database.py
from sqlalchemy.orm import relationship

class Aluno(Base):
    __tablename__ = 'alunos'

    matricula = Column("matricula", Integer, primary_key=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    cpf = Column("cpf", String, unique=True, nullable=False)
    rg = Column("rg", String, unique=True, nullable=False)
    curso = Column("curso", String, nullable=False)
    responsavel = Column("responsavel", String)
    data_cadastro = Column("data_cadastro", DateTime, default=datetime.utcnow)
    data_nasc = Column("data_nasc", Date, nullable=True)
    validade = Column("validade", Date, nullable=True)

    # Relacionamento 1 para 1 com Carteirinha
    carteirinha = relationship("Carteirinha", back_populates="aluno", uselist=False)

    def __init__(self, matricula, nome, email, cpf, rg,  curso, responsavel=None, data_nasc=None,validade=None):
        self.matricula = matricula
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.rg= rg
        self.curso = curso
        self.responsavel = responsavel
        self.data_nasc = data_nasc
        self.validade = validade

class Carteirinha(Base):
    __tablename__ = 'carteirinhas'

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    aluno_matricula = Column("aluno_matricula", Integer, ForeignKey("alunos.matricula"), nullable=False)
    email = Column("email", String, nullable=False)
    validade = Column("validade", Date, nullable=False)
    status = Column("status", String, default='Ativo')
    caminho_foto = Column("caminho_foto", Text)
    pdf_gerado = Column("pdf_gerado", Text)
    criado_em = Column("criado_em", DateTime, default=datetime.utcnow)

    # Relacionamento 1 para 1 com Carteirinha
    aluno = relationship("Aluno", back_populates="carteirinha")

    def __init__(self, aluno_matricula, email, validade, status='Ativo', caminho_foto=None, pdf_gerado=None):
        self.aluno_matricula = aluno_matricula
        self.email = email
        self.validade = validade
        self.status = status
        self.caminho_foto = caminho_foto
        self.pdf_gerado = pdf_gerado

class Admin(Base):
    __tablename__ = 'admin'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    matricula = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)

    def __init__(self, matricula, email):
        self.matricula = matricula
        self.email = email