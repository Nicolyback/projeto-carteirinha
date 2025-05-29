from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, DateTime
from datetime import datetime
from database import Base  # Usa o Base criado em database.py

class Aluno(Base):
    __tablename__ = 'alunos'

    matricula = Column("matricula", Integer, primary_key=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    cpf = Column("cpf", String, unique=True, nullable=False)
    curso = Column("curso", String, nullable=False)
    responsavel = Column("responsavel", String)
    data_cadastro = Column("data_cadastro", DateTime, default=datetime.utcnow)

    def __init__(self, matricula, nome, email, cpf, curso, responsavel=None):
        self.matricula = matricula
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.curso = curso
        self.responsavel = responsavel


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

    def __init__(self, aluno_matricula, email, validade, status='Ativo', caminho_foto=None, pdf_gerado=None):
        self.aluno_matricula = aluno_matricula
        self.email = email
        self.validade = validade
        self.status = status
        self.caminho_foto = caminho_foto
        self.pdf_gerado = pdf_gerado