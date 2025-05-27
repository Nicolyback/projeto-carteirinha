from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, DateTime
from datetime import datetime
from database import Base  # Usa o Base criado em database.py

class Aluno(Base):
    __tablename__ = 'alunos'

    matricula = Column("matricula", Integer, primary_key=True)
    email = Column("email", String, nullable=False)
    nome = Column("nome", String, nullable=False)

    def __init__(self, matricula, email, nome):
        super().__init__()
        self.matricula = matricula
        self.email = email
        self.nome = nome

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
        super().__init__()
        self.aluno_matricula = aluno_matricula
        self.email = email
        self.validade = validade
        self.status = status
        self.caminho_foto = caminho_foto
        self.pdf_gerado = pdf_gerado
