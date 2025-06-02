from flask import render_template, request, flash, url_for, redirect
from main import app
from models import Aluno, Carteirinha
from database import session
from datetime import datetime
from PIL import Image
import os
# Importa as funções auxiliares de app_routes.py
from app_routes import verificar_carteirinha, validar_tamanho_foto



@app.route("/", methods=["GET", "POST"])
def homeindex():
   
    if request.method == "POST":
        matricula = int(request.form["matricula"])
        email = request.form["email"]

        resultado = verificar_carteirinha(matricula, email)

        if isinstance(resultado, str) and resultado.endswith(".pdf"):
            resultado = f"Carteirinha encontrada: <a href='{resultado}'>Baixar</a>"

        return render_template("index.html", resultado=resultado)

    return render_template("index.html")


@app.route("/cadastrar_aluno")
def cadastrar_aluno():
    return render_template("formulario.html")

@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form["nome"]
    matricula = int(request.form["matricula"])
    email = request.form["email"]
    cpf = request.form["cpf"]
    curso = request.form["curso"]
    responsavel = request.form.get("responsavel", None)
    validade_str = request.form["validade"]  # Exemplo: "2025-09"

    # Converter string "YYYY-MM" para objeto date (com dia fixo no primeiro do mês)
    validade = datetime.strptime(validade_str, "%Y-%m").date()

    # Cria e salva o aluno
    aluno = Aluno(
        matricula=matricula,
        nome=nome,
        email=email,
        cpf=cpf,
        curso=curso,
        responsavel=responsavel
    )
    session.add(aluno)
    session.commit()

    # Cria e salva a carteirinha associada
    carteirinha = Carteirinha(
        aluno_matricula=aluno.matricula,
        email=email,
        validade=validade,
        status='Ativo',
        caminho_foto=None,
        pdf_gerado=None
    )
    session.add(carteirinha)
    session.commit()

    flash("Aluno e carteirinha cadastrados com sucesso!", "sucesso")
    return redirect(url_for("upload"))

@app.route("/upload", methods=["GET", "POST"])
def upload():
    
    if request.method == "POST":
        imagem_arquivo = request.files["foto"]

        try:
            imagem = Image.open(imagem_arquivo)

            valido, mensagem = validar_tamanho_foto(imagem)
            if not valido:
                flash(mensagem, "erro")
                return redirect(url_for("upload"))

            # Você pode salvar a imagem aqui, se quiser
            # caminho = os.path.join("static/fotos", imagem_arquivo.filename)
            # imagem.save(caminho)

            flash("Foto enviada com sucesso!", "sucesso")
            # Exibe a mesma página, porém com o botão de visualizar aparecendo
            return render_template("upload.html", foto_enviada=True)

        except Exception as e:
            flash("Erro ao processar a imagem: " + str(e), "erro")
            return redirect(url_for("upload"))

    return render_template("upload.html", foto_enviada=False)

ADMIN_PASSWORD = "minha_senha_super_secreta"

@app.route('/admin')
def admin():
    return render_template('administrador.html')