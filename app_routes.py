
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

def validar_tamanho_foto(imagem):
    LARGURA_ESPERADA = 115
    ALTURA_ESPERADA = 144
    TOLERANCIA = 5

    largura, altura = imagem.size
    if abs(largura - LARGURA_ESPERADA) > TOLERANCIA or abs(altura - ALTURA_ESPERADA) > TOLERANCIA:
        return False, f"A foto deve ter {LARGURA_ESPERADA}x{ALTURA_ESPERADA} pixels. Enviada: {largura}x{altura}."
    return True, "Tamanho válido."