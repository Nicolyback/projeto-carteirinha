from main import app
from flask import render_template, request

@app.route("/", methods=["GET", "POST"])
def homeindex():
    if request.method == "POST":
        matricula = request.form["matricula"]
        email = request.form["email"]

        if matricula == "12345" and email == "aluno@ifam.edu.br":
            resultado = "sucesso"
        else:
            resultado = "erro"
        return render_template("index.html", resultado=resultado)
    
    return render_template("index.html")

