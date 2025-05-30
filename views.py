from flask import render_template, request, flash, url_for, redirect
from main import app
from models import Aluno, Carteirinha
from database import session
from datetime import datetime

@app.route("/", methods=["GET", "POST"])
def homeindex():
    from app_routes import verificar_carteirinha

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
    return redirect(url_for("cadastrar_aluno"))


ADMIN_PASSWORD = "minha_senha_super_secreta"

@app.route('/admin')
def admin():
    return render_template('administrador.html')