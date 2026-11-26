from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = "chave-temporaria-sashimi-noku"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sashimi_noku.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Tabela de usuários
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), default="cliente", nullable=False)


# Página inicial
@app.route("/")
def inicio():
    return render_template("index.html")


# Cadastro de clientes
@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"].strip()
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        if not nome or not email or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for("cadastro"))

        if len(senha) < 6:
            flash("A senha precisa ter pelo menos 6 caracteres.")
            return redirect(url_for("cadastro"))

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("Este e-mail já está cadastrado.")
            return redirect(url_for("cadastro"))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            tipo="cliente"
        )

        db.session.add(novo_usuario)
        db.session.commit()

        flash("Cadastro realizado com sucesso!")
        return redirect(url_for("inicio"))

    return render_template("cadastro.html")

# Login de clientes e gestores
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        senha = request.form["senha"]

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            session["usuario_id"] = usuario.id
            session["usuario_tipo"] = usuario.tipo

            flash("Login realizado com sucesso!")
            return redirect(url_for("inicio"))

        flash("E-mail ou senha incorretos.")
        return redirect(url_for("login"))

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.pop("usuario_id", None)
    flash("Você saiu da sua conta.")
    return redirect(url_for("inicio"))

# Área do gestor
@app.route("/gestor")
def area_gestor():
    if "usuario_id" not in session:
        flash("Faça login para acessar esta página.")
        return redirect(url_for("login"))

    usuario = db.session.get(Usuario, session["usuario_id"])

    if not usuario or usuario.tipo != "gestor":
        flash("Você não tem permissão para acessar esta área.")
        return redirect(url_for("inicio"))

    return render_template("gestor.html")

# Criação automática das tabelas
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
