
from getpass import getpass
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    nome = input("Nome do gestor: ").strip()
    email = input("E-mail do gestor: ").strip().lower()
    senha = getpass("Senha do gestor: ")

    if not nome or not email or len(senha) < 6:
        print("Preencha os dados corretamente. A senha precisa ter 6 caracteres.")
    elif Usuario.query.filter_by(email=email).first():
        print("Este e-mail já está cadastrado.")
    else:
        gestor = Usuario(
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            tipo="gestor"
        )

        db.session.add(gestor)
        db.session.commit()

        print("Conta de gestor criada com sucesso!")
