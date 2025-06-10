from database import session
from models import Admin


# Cria uma instância do administrador
novo_admin = Admin(matricula="1234", email="4321@gmail.com")

# Adiciona ao banco e salva
session.add(novo_admin)
session.commit()

print("Admin inserido com sucesso!")