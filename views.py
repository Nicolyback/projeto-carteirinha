from flask import render_template, request, flash, url_for, redirect
from main import app
from models import Aluno, Carteirinha
from database import session
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os
# Importa as funções auxiliares de app_routes.py
from app_routes import verificar_carteirinha, validar_tamanho_foto
from sqlalchemy import String


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
    rg = request.form["rg"]
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
        rg=rg,
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

    # Correção: passando matricula na query string para a rota 'upload'
    return redirect(url_for("upload", matricula=matricula))


@app.route('/upload/<matricula>', methods=['GET', 'POST'])


def upload(matricula):
    if request.method == "POST":
        if "foto" not in request.files:
            flash("Nenhuma foto enviada.", "erro")
            return redirect(url_for("upload", matricula=matricula))
        
        imagem_arquivo = request.files["foto"]

        if imagem_arquivo.filename == "":
            flash("Nenhuma foto selecionada.", "erro")
            return redirect(url_for("upload", matricula=matricula))

        try:
            imagem = Image.open(imagem_arquivo)

            valido, mensagem = validar_tamanho_foto(imagem)
            if not valido:
                flash(mensagem, "erro")
                return redirect(url_for("upload", matricula=matricula))

            # Salva a imagem na pasta estática, usando a matrícula como nome
            caminho = os.path.join("static", "imagensdosalunos", f"{matricula}.png")
            imagem.save(caminho)

            foto_url = url_for('static', filename=f'imagensdosalunos/{matricula}.png')
            flash("Foto enviada com sucesso!", "sucesso")

            # Renderiza a página com a foto e o botão "Visualizar Carteirinha"
            return render_template("upload.html", foto_enviada=True, foto_url=foto_url, matricula=matricula)

        except Exception as e:
            flash(f"Erro ao processar a imagem: {str(e)}", "erro")
            return redirect(url_for("upload", matricula=matricula))

    # Caso seja GET, só renderiza o formulário sem foto
    return render_template("upload.html", foto_enviada=False, matricula=matricula)


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


@app.route("/gerar_carteirinha/<int:matricula>")
def gerar_carteirinha(matricula):
    aluno = session.query(Aluno).filter_by(matricula=matricula).first()
    carteirinha = session.query(Carteirinha).filter_by(aluno_matricula=matricula).first()

    if not aluno or not carteirinha:
        flash("Aluno ou carteirinha não encontrados.", "erro")
        return redirect(url_for("listar"))

    caminho_modelo = os.path.join("static", "images", "modelo_carteirinha.png")  # frente do modelo
    caminho_verso = os.path.join("static", "images", "verso_padrao.png")         # verso padrão
    caminho_foto = os.path.join("static", "imagensdosalunos", f"{aluno.matricula}.png")  # foto do aluno
    caminho_saida_frente = os.path.join("static", "images", "carteirinhas", f"frente_{aluno.matricula}.png")

    try:
        imagem_base = Image.open(caminho_modelo).convert("RGBA")
        foto = Image.open(caminho_foto).resize((150, 180))
        imagem_base.paste(foto, (50, 50))  # ajuste a posição se necessário

        draw = ImageDraw.Draw(imagem_base)
        fonte = ImageFont.truetype("arial.ttf", 20)  # você pode mudar a fonte se quiser

        draw.text((250, 50), f"Nome: {aluno.nome}", fill="black", font=fonte)
        draw.text((250, 80), f"Matrícula: {aluno.matricula}", fill="black", font=fonte)
        draw.text((250, 110), f"Curso: {aluno.curso}", fill="black", font=fonte)
        draw.text((250, 140), f"CPF: {aluno.cpf}", fill="black", font=fonte)
        draw.text((250, 170), f"RG: {aluno.rg}", fill="black", font=fonte)
        draw.text((250, 200), f"Validade: {carteirinha.validade.strftime('%m/%Y')}", fill="black", font=fonte)

        imagem_base.save(caminho_saida_frente)

        carteirinha.pdf_gerado = caminho_saida_frente
        session.commit()

        url_frente = url_for("static", filename=f"images/carteirinhas/frente_{aluno.matricula}.png")
        url_verso = url_for("static", filename="images/verso_padrao.png")

        return render_template("carteirinha_gerada.html", imagem_frente=url_frente, imagem_verso=url_verso)

    except Exception as e:
        flash(f"Erro ao gerar carteirinha: {e}", "erro")
        return redirect(url_for("listar"))


ADMIN_PASSWORD = "minha_senha_super_secreta"

@app.route('/admin')
def admin():
    return render_template('administrador.html')
