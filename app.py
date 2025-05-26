from database import session
from models import Aluno, Carteirinha

def verificar_carteirinha(matricula, email):
    aluno = session.query(Aluno).filter_by(matricula=matricula).first()

    if aluno:
        if aluno.email == email:
            carteirinha = session.query(Carteirinha).filter_by(aluno_matricula=matricula).first()
            if carteirinha:
                return carteirinha.pdf_gerado  
            else:
                return None  # Aluno válido, mas não tem carteirinha
        else:
            return None  # Email não confere
    else:
        return None  # Matrícula não encontrada