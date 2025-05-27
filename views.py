from flask import render_template, request
from main import app



@app.route("/", methods=["GET", "POST"])
def homeindex():
    from app_routes import verificar_carteirinha
    if request.method == "POST":
        matricula = int(request.form["matricula"])
        email = request.form["email"]

        link = verificar_carteirinha(matricula, email)

        if link:
            resultado = f"Carteirinha encontrada: <a href='{link}'>Baixar</a>"
        else:
            resultado = "Dados inválidos ou carteirinha não encontrada."

        return render_template("index.html", resultado=resultado)
    
    return render_template("index.html")

