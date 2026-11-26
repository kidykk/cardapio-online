
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)

app.config["SECRET_KEY"] = "chave-temporaria-sashimi-noku"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sashimi_noku.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================
# MODELOS DO BANCO DE DADOS
# =========================

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), default="cliente", nullable=False)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    data = db.Column(db.DateTime, default=datetime.now)
    total = db.Column(db.Float, nullable=False)
    forma_pagamento = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), default="Recebido", nullable=False)

    usuario = db.relationship("Usuario")
    itens = db.relationship("ItemPedido", backref="pedido", cascade="all, delete-orphan")


class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"), nullable=False)
    nome_produto = db.Column(db.String(120), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)


# =========================
# PRODUTOS DO CARDÁPIO
# =========================

CARDAPIO = [
    ("BARCA NOKU", 60.00),
    ("COMBINADO TRADICIONAL", 48.00),
    ("SASHIMI DE SALMÃO", 34.00),
    ("TEMAKI DE SALMÃO", 26.00),
    ("HOT ROLL PHILADELPHIA", 28.00),
    ("URAMAKI CALIFÓRNIA", 24.00),
    ("NIGIRI DE ATUM", 22.00),
    ("GYOZA DE PORCO", 24.00),
    ("TEMPURA DE CAMARÃO", 36.00),
    ("YAKISSOBA DE FRANGO", 38.00),
    ("LAMEN SHOYU", 42.00),
    ("MISSOSHIRO", 14.00),
    ("NIGIRI DE SALMÃO", 22.00),
    ("SHIMEJI NA MANTEIGA", 26.00),
    ("MOCHI DE CHÁ VERDE", 16.00)
]


def criar_banco():
    db.create_all()

    # Cadastra o cardápio inicial somente se ainda não existir
    if Produto.query.count() == 0:
        for nome, preco in CARDAPIO:
            db.session.add(Produto(nome=nome, preco=preco))

        db.session.commit()


# =========================
# CONTROLE DE ACESSO
# =========================

def gestor_obrigatorio(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar esta página.")
            return redirect(url_for("login"))

        usuario = db.session.get(Usuario, session["usuario_id"])

        if not usuario or usuario.tipo != "gestor":
            flash("Você não tem permissão para acessar esta área.")
            return redirect(url_for("inicio"))

        return funcao(*args, **kwargs)

    return verificar


# =========================
# PÁGINA INICIAL
# =========================

@app.route("/")
def inicio():
    produtos = Produto.query.order_by(Produto.id).all()
    return render_template("index.html", produtos=produtos)


# =========================
# CADASTRO
# =========================

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not nome or not email or not senha:
            flash("Preencha todos os campos.")
            return redirect(url_for("cadastro"))

        if len(senha) < 6:
            flash("A senha precisa ter pelo menos 6 caracteres.")
            return redirect(url_for("cadastro"))

        if Usuario.query.filter_by(email=email).first():
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


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.senha_hash, senha):
            session["usuario_id"] = usuario.id
            session["usuario_tipo"] = usuario.tipo

            flash("Login realizado com sucesso!")
            return redirect(url_for("inicio"))

        flash("E-mail ou senha incorretos.")
        return redirect(url_for("login"))

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu da sua conta.")
    return redirect(url_for("inicio"))


# =========================
# REGISTRO DE PEDIDOS
# =========================

@app.route("/api/pedidos", methods=["POST"])
def registrar_pedido():

    if "usuario_id" not in session:
        return jsonify({
            "sucesso": False,
            "mensagem": "Faça login para realizar um pedido."
        }), 401

    dados = request.get_json(silent=True) or {}

    itens = dados.get("itens", [])
    pagamento = dados.get("pagamento", "")

    if not itens:
        return jsonify({
            "sucesso": False,
            "mensagem": "O pedido está vazio."
        }), 400

    if pagamento not in ["pix", "credito", "debito"]:
        return jsonify({
            "sucesso": False,
            "mensagem": "Forma de pagamento inválida."
        }), 400

    novo_pedido = Pedido(
        usuario_id=session["usuario_id"],
        total=0,
        forma_pagamento=pagamento,
        status="Recebido"
    )

    total = 0

    try:
        for item in itens:
            produto_id = int(item.get("id", 0))
            quantidade = int(item.get("qtd", 0))

            if quantidade <= 0:
                raise ValueError("Quantidade inválida.")

            produto = db.session.get(Produto, produto_id)

            if not produto or not produto.ativo:
                raise ValueError("Produto não encontrado ou indisponível.")

            subtotal = produto.preco * quantidade
            total += subtotal

            novo_item = ItemPedido(
                produto_id=produto.id,
                nome_produto=produto.nome,
                quantidade=quantidade,
                preco_unitario=produto.preco
            )

            novo_pedido.itens.append(novo_item)

        novo_pedido.total = round(total, 2)

        db.session.add(novo_pedido)
        db.session.commit()

        return jsonify({
            "sucesso": True,
            "mensagem": "Pedido registrado com sucesso!",
            "pedido_id": novo_pedido.id
        }), 201

    except (ValueError, TypeError) as erro:
        db.session.rollback()

        return jsonify({
            "sucesso": False,
            "mensagem": str(erro)
        }), 400

    except Exception:
        db.session.rollback()

        return jsonify({
            "sucesso": False,
            "mensagem": "Não foi possível registrar o pedido."
        }), 500


# =========================
# ÁREA DO GESTOR
# =========================

@app.route("/gestor")
@gestor_obrigatorio
def area_gestor():

    pedidos = Pedido.query.order_by(Pedido.data.desc()).all()
    produtos = Produto.query.order_by(Produto.id).all()

    return render_template(
        "gestor.html",
        pedidos=pedidos,
        produtos=produtos
    )


# =========================
# ALTERAR STATUS DO PEDIDO
# =========================

@app.route("/gestor/pedido/<int:pedido_id>", methods=["POST"])
@gestor_obrigatorio
def atualizar_pedido(pedido_id):

    pedido = db.session.get(Pedido, pedido_id)

    if not pedido:
        flash("Pedido não encontrado.")
        return redirect(url_for("area_gestor"))

    novo_status = request.form.get("status")

    status_permitidos = [
        "Recebido",
        "Em preparo",
        "Concluído",
        "Cancelado"
    ]

    if novo_status not in status_permitidos:
        flash("Status inválido.")
        return redirect(url_for("area_gestor"))

    pedido.status = novo_status
    db.session.commit()

    flash("Pedido atualizado com sucesso!")
    return redirect(url_for("area_gestor"))


# =========================
# GERENCIAR PRODUTOS
# =========================

@app.route("/gestor/produto/<int:produto_id>", methods=["POST"])
@gestor_obrigatorio
def atualizar_produto(produto_id):

    produto = db.session.get(Produto, produto_id)

    if not produto:
        flash("Produto não encontrado.")
        return redirect(url_for("area_gestor"))

    nome = request.form.get("nome", "").strip()
    preco_texto = request.form.get("preco", "").replace(",", ".")

    try:
        preco = float(preco_texto)

        if not nome or preco < 0:
            raise ValueError

    except ValueError:
        flash("Informe um nome e um preço válido.")
        return redirect(url_for("area_gestor"))

    produto.nome = nome
    produto.preco = preco

    db.session.commit()

    flash("Produto atualizado com sucesso!")
    return redirect(url_for("area_gestor"))


# =========================
# CRIAÇÃO DAS TABELAS
# =========================

with app.app_context():
    criar_banco()


if __name__ == "__main__":
    app.run(debug=True)
