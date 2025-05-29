from main import app
from database import session
from models import Aluno, Carteirinha
from datetime import date

# Função para verificar se o aluno e sua carteirinha existem e validar email
def verificar_carteirinha(matricula, email):
    aluno = session.query(Aluno).filter_by(matricula=matricula).first()
    if aluno:
        if aluno.email == email:
            carteirinha = session.query(Carteirinha).filter_by(aluno_matricula=matricula).first()
            if carteirinha:
                return carteirinha.pdf_gerado  
            else:
                return "Aluno válido, mas não tem carteirinha."  
        else:
            return "Email não confere." 
    else:
        return "Matrícula não encontrada." 

# Rota para criar aluno fixo (apenas para teste)
@app.route("/criar_aluno")
def criar_aluno():
    if session.query(Aluno).filter_by(matricula=2023304038).first():
        return "Aluno já existe no banco."
    aluno = Aluno(matricula=2023304038, email="2023304038@ifam.edu.br", nome="Nicoly Lima de Souza")
    session.add(aluno)
    session.commit()
    return "Aluno criado com sucesso!"

@app.route("/criar_carteirinha")
def criar_carteirinha():
    if session.query(Carteirinha).filter_by(aluno_matricula=2023304038).first():
        return "A carteirinha do aluno já existe."
    carteirinha=Carteirinha(aluno_matricula=2023304038, email="2023304038@ifam.edu.br", validade=date(2025, 12, 1), status="ativo", caminho_foto="fotos/nicoly.jpg", pdf_gerado="pdfs/carteirinha_nicoly.pdf")
    session.add(carteirinha)
    session.commit()
    return "Carteirinhs criada com sucesso!"