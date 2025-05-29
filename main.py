from flask import Flask

app= Flask(__name__)
app.secret_key = 'uma_chave_super_secreta_e_segura_aqui_123!' 


# Importa e inicializa o banco de dados (cria as tabelas)
from database import init_db
init_db()
from app_routes import *
from views import * 

if __name__ == "__main__":
    app.run(debug=True)
