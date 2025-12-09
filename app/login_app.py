
import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "chave_secreta_troque_isto"

# Caminho do arquivo JSON de usuários
USUARIOS_JSON = os.path.join(os.path.dirname(__file__), 'banco_dados', 'usuarios.json')

def carregar_usuarios():
    if os.path.exists(USUARIOS_JSON):
        with open(USUARIOS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_usuarios(usuarios):
    with open(USUARIOS_JSON, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET","POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))


    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        usuarios = carregar_usuarios()
        user = next((u for u in usuarios if u["email"] == email), None)

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Bem-vindo(a), {user['name']}!", "success")
            return redirect(url_for("home"))
        else:
            flash("E-mail ou senha inválida.", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))


    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if password != confirm_password:
            flash("As senhas não conferem.", "danger")
            return redirect(url_for("register"))

        usuarios = carregar_usuarios()
        if any(u["email"] == email for u in usuarios):
            flash("E-mail já cadastrado.", "danger")
            return redirect(url_for("register"))

        # Gera um novo id
        new_id = max([u["id"] for u in usuarios], default=0) + 1
        password_hash = generate_password_hash(password)
        novo_usuario = {
            "id": new_id,
            "name": name,
            "email": email,
            "password_hash": password_hash
        }
        usuarios.append(novo_usuario)
        salvar_usuarios(usuarios)
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# Simulação de tela de esqueci a senha (não envia e-mail, apenas feedback)
@app.route("/forgot_password", methods=["GET"])
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/forgot_password", methods=["POST"])
def forgot_password_submit():
    email = request.form.get("email", "").strip()
    usuarios = carregar_usuarios()
    if any(u["email"] == email for u in usuarios):
        flash("Se o e-mail existir, você receberá um link para redefinir a senha.", "info")
    else:
        flash("Informe um e-mail válido.", "danger")
    return redirect(url_for("forgot_password"))

@app.route("/termos")
def termos():
    return "<h1>Termos de Uso</h1><p>Exemplo.</p>"

@app.route("/home")
def home():
    if "user_id" not in session:
        flash("Faça login para acessar.", "warning")
        return redirect(url_for("login"))
    return render_template("home.html", name=session.get("user_name"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))

 
if __name__ == "__main__":
    app.run(debug=True)
