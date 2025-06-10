from flask import render_template, request, flash, url_for, redirect, jsonify
from main import app
from models import Aluno, Carteirinha, Admin
from database import session
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.exc import IntegrityError
import os
# Importa as funções auxiliares de app_routes.py
from app_routes import verificar_carteirinha, validar_tamanho_foto
from sqlalchemy import String
from werkzeug.utils import secure_filename


# Pastas para salvar arquivos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
CARTEIRINHA_FOLDER = os.path.join('static', 'imagensdealuno')

def data_brasileira_para_iso(data_str):
    if data_str:
        return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    return None

@app.route("/", methods=["GET", "POST"])
def homeindex():
    if request.method == "POST":
        try:
            matricula = int(request.form["matricula"])
            email = request.form["email"]

            # Verificar se é admin
            admin = session.query(Admin).filter_by(matricula=matricula, email=email).first()
            if admin:
                return render_template("index.html", resultado="admin")

            # Verificar carteirinha do aluno
            resultado_verificacao = verificar_carteirinha(matricula, email)

            if isinstance(resultado_verificacao, str) and resultado_verificacao.endswith(".pdf"):
                caminho_pdf = resultado_verificacao
                return render_template("index.html", resultado="sucesso", caminho_pdf=caminho_pdf)

            return render_template("index.html", resultado="nao_cadastrada")

        except (ValueError, KeyError):
            return render_template("index.html", resultado="erro_dados")

    return render_template("index.html")


@app.route("/cadastrar_aluno")
def cadastrar_aluno():
    return render_template("formulario.html")



@app.route("/enviar", methods=["POST"])
def enviar():
    nome = request.form["nome"]
    matricula_str = request.form["matricula"]
    email = request.form.get("email", None)
    cpf = request.form["cpf"]
    rg = request.form.get("rg")
    curso = request.form["curso"]
    responsavel = request.form.get("responsavel", None)
    validade_str = request.form["validade"]
    data_nasc_str = request.form.get("data_nasc", None)

    erros = []

    # Tentar converter matrícula em inteiro
    try:
        matricula = int(matricula_str)
    except ValueError:
        erros.append("❌ Matrícula inválida.")

    # Verificar se já existem registros com mesmo nome, matrícula ou cpf
    if session.query(Aluno).filter_by(nome=nome).first():
        erros.append('❌ Nome já cadastrado.')
    if session.query(Aluno).filter_by(matricula=matricula).first():
        erros.append('❌ Matrícula já cadastrada.')
    if session.query(Aluno).filter_by(cpf=cpf).first():
        erros.append('❌ CPF já cadastrado.')

    # Lidar com erros iniciais
    if erros:
        for erro in erros:
            flash(erro, 'erro')
        return render_template('formulario.html',
                               nome=nome,
                               matricula=matricula_str,
                               email=email,
                               cpf=cpf,
                               rg=rg,
                               curso=curso,
                               responsavel=responsavel,
                               validade=validade_str,
                               data_nasc=data_nasc_str)

    # Conversão da validade
    try:
        if len(validade_str) == 7:  # formato YYYY-MM
            validade = datetime.strptime(validade_str, "%Y-%m").date()
        else:  # formato completo YYYY-MM-DD
            validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
    except ValueError:
        flash("❌ Data de validade inválida.", "erro")
        return redirect(url_for("cadastrar_aluno"))

    # Conversão da data de nascimento (opcional)
    data_nasc = None
    if data_nasc_str:
        try:
            data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d").date()
        except ValueError:
            flash("❌ Data de nascimento inválida.", "erro")
            return redirect(url_for("cadastrar_aluno"))

    # Criação do aluno
    aluno = Aluno(
        matricula=matricula,
        nome=nome,
        email=email,
        cpf=cpf,
        rg=rg,
        curso=curso,
        responsavel=responsavel,
        data_nasc=data_nasc,
        validade=validade
    )

    try:
        session.add(aluno)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        flash(f"❌ Erro ao cadastrar aluno: {e.orig}", "erro")
        return redirect(url_for("cadastrar_aluno"))

    # Criação da carteirinha
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


    return redirect(url_for("upload", matricula=matricula))

@app.route("/upload/<int:matricula>", methods=["GET", "POST"])
def upload(matricula):
    if request.method == "GET":
        # Exibe a página para tirar a foto
        aluno = session.query(Aluno).filter_by(matricula=matricula).first()
        if not aluno:
            flash("Aluno não encontrado.", "erro")
            return redirect(url_for("formulario"))

        return render_template("upload.html", matricula=matricula, aluno=aluno)

    # POST: Recebe a foto
    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nome de arquivo vazio"}), 400

    aluno = session.query(Aluno).filter_by(matricula=matricula).first()
    if not aluno:
        return jsonify({"error": "Aluno não encontrado"}), 404

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(CARTEIRINHA_FOLDER, exist_ok=True)

    temp_filename = secure_filename(file.filename)
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)

    try:
        file.save(temp_path)

        modelo_path = os.path.join("static", "images", "identidadeestudantilfrente.png")
        output_filename = f"{matricula}.png"
        output_path = os.path.join(CARTEIRINHA_FOLDER, output_filename)

        modelo = Image.open(modelo_path).convert("RGBA")
        foto = Image.open(temp_path).convert("RGBA")
        foto = foto.resize((100, 130))

        modelo.paste(foto, (350, 80), foto)
        modelo.save(output_path)

        os.remove(temp_path)

        carteirinha_url = url_for('static', filename=f'imagensdosalunos/{output_filename}')

        return jsonify({
            "success": True,
            "matricula": matricula,
            "preview_url": carteirinha_url,
            "image_path": output_filename
        })

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": f"Erro ao gerar carteirinha: {str(e)}"}), 500

@app.route("/confirmar_foto", methods=["POST"])
def confirmar_foto():
    image_path = request.form.get("image_path")
    if not image_path:
        flash("Nenhuma imagem confirmada.", "erro")
        return redirect(url_for("formulario"))

    # Aqui você pode extrair a matrícula do nome do arquivo, que foi salvo como <matricula>.png
    matricula_str = image_path.split(".")[0]
    try:
        matricula = int(matricula_str)
    except ValueError:
        flash("Matrícula inválida.", "erro")
        return redirect(url_for("formulario"))

    # Redireciona para mostrar a carteirinha
    return redirect(url_for("mostrar_carteirinha", matricula=matricula))


@app.route("/mostrar_carteirinha/<int:matricula>")
def mostrar_carteirinha(matricula):
    aluno = session.query(Aluno).filter_by(matricula=matricula).first()
    if not aluno:
        flash("Aluno não encontrado.", "erro")
        return redirect(url_for("formulario"))

    nome_arquivo = f"{matricula}.png"
    caminho = os.path.join(CARTEIRINHA_FOLDER, nome_arquivo)

    if not os.path.exists(caminho):
        flash("Carteirinha ainda não foi gerada.", "erro")
        return redirect(url_for("upload", matricula=matricula))

    url_carteirinha = url_for("static", filename=f"imagensdosalunos/{nome_arquivo}")

    return render_template("carteirinhagerada.html", imagem_carteirinha=url_carteirinha, aluno=aluno)




@app.route("/listar", methods=["GET", "POST"])
def listar():
    termo_busca = request.args.get("busca", "").strip()  # pega o termo da query string

    query = session.query(Aluno).join(Carteirinha)

    if termo_busca:
        # Filtrar alunos pelo nome, matrícula ou curso contendo o termo (case-insensitive)
        filtro = f"%{termo_busca}%"
        query = query.filter(
            (Aluno.nome.ilike(filtro)) |
            (Aluno.curso.ilike(filtro)) |
            (Aluno.matricula.cast(String).ilike(filtro))
        )

    alunos = query.all()
    return render_template("listas.html", alunos=alunos, termo_busca=termo_busca)

import sqlite3

@app.route('/editar_aluno', methods=['POST'])
def editar_aluno():
    matricula = request.form.get('matricula')

    conn = sqlite3.connect('studentidbank.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, curso, data_nasc, validade, cpf FROM alunos WHERE matricula = ?", (matricula,))
    dados = cursor.fetchone()
    conn.close()

    if dados:
        # Mude o formato de entrada para "%d/%m/%Y"
        data_nasc = (
            datetime.strptime(dados[2], "%Y-%m-%d").date()
            if dados[2] else None
        )

        validade = (
            datetime.strptime(dados[3], "%Y-%m-%d").date()
            if dados[3] else None
        )

        aluno = {
            'matricula': matricula,
            'nome': dados[0],
            'curso': dados[1],
            'data_nasc': data_nasc,
            'validade': validade,
            'cpf': dados[4]
        }

        return render_template('administrador.html', aluno=aluno)
    else:
        return "Aluno não encontrado", 404

@app.route("/excluir_aluno", methods=["POST"])
def excluir_aluno():
    matricula = request.form.get("matricula")
    if not matricula:
        flash("Matrícula não recebida.")
        return redirect(url_for("listar"))

    aluno = session.query(Aluno).filter_by(matricula=matricula).first()

    if aluno:
        # Deleta primeiro a(s) carteirinha(s) associada(s)
        carteirinhas = session.query(Carteirinha).filter_by(
            aluno_matricula=matricula).all()
        for c in carteirinhas:
            session.delete(c)

        session.delete(aluno)
        session.commit()
        # flash(f"Aluno {matricula} e carteirinha(s) excluídos com sucesso!")
        return redirect(url_for("admin"))
    else:
        flash("Aluno não encontrado.")

    return redirect(url_for("listar"))

@app.route('/salvar_aluno', methods=['POST'])
def salvar_aluno():
    matricula = request.form.get("matricula")
    nome = request.form.get("nome")
    curso = request.form.get("curso")
    data_nasc = request.form.get("data_nasc")
    validade = request.form.get("validade")
    cpf = request.form.get("cpf")

    # Converter para ISO antes de salvar
    data_nasc_iso = data_brasileira_para_iso(data_nasc)
    validade_iso = data_brasileira_para_iso(validade)

    conn = sqlite3.connect('studentidbank.db')
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE alunos
        SET nome = ?, curso = ?, data_nasc = ?, validade = ?, cpf = ?
        WHERE matricula = ?
    """, (nome, curso, data_nasc_iso, validade_iso, cpf, matricula))

    conn.commit()
    conn.close()

    flash("Dados do aluno atualizados com sucesso!", "sucesso")
    return redirect(url_for("admin"))





ADMIN_PASSWORD = "minha_senha_super_secreta"

@app.route('/admin')
def admin():
    return render_template('administrador.html')
