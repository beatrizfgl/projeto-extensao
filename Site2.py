from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

#import json

# Criação do app em flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projeto.db.sqlite'
app.app_context().push()

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Base de dados
db = SQLAlchemy()
db.init_app(app)

# Definicao da tabela de usuários na base de dados 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    department = db.Column(db.String(1000))

@login_manager.user_loader
def load_user(user_id):
    # since the email is the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

#def salvar_usuario(usuario):
#    with open('usuarios.json', 'r+') as arquivo:
#        data = json.load(arquivo)
#        data.append(usuario)
#        arquivo.seek(0)
#        json.dump(data, arquivo)

#def carregar_usuarios():
#    try:
#        with open('usuarios.json', 'r') as arquivo:
#            return json.load(arquivo)
#    except FileNotFoundError:
#        return []

@app.route("/") 
def homepage():
    return render_template("homepage.html") 

@app.route("/login", methods=["GET", "POST"]) # Agora aceita tanto GET quanto POST
def login():
    if request.method == "POST":
        # Lógica de autenticação aqui
        email = request.form.get('email')
        password = request.form.get('password')

        # procura este usuario na base de dados
        # se existir, o objeto "user" será uma estrutura de dados contendo os dados do usuario que vieram da base de dados
        user = User.query.filter_by(email=email).first()

        # verifica se usuario existe
        # pega a senha fornecida, calcula o hash e compara com o hash guardado no banco de dados
        if not user or not check_password_hash(user.password, password):
            return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page

        # se chegou aqui, o usuário é valido
        login_user(user)
        return redirect(url_for('usuarios', nome_usuario=user.email))  # Redireciona para a página inicial após o login

    return render_template("login.html") 

@app.route("/usuarios/<nome_usuario>")
@login_required
def usuarios(nome_usuario):
    return render_template("usuarios.html", nome_usuario = nome_usuario) 

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        department = request.form["department"]

        user = User.query.filter_by(email=username).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again  
            return redirect(url_for('cadastro'))

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(email=username, password=generate_password_hash(password, method='pbkdf2'), department=department)
        #new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), admin=admin)

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        #usuario = {'username': username, 'password': password, 'department': department}
        #salvar_usuario(usuario)
        #return "Usuário cadastrado com sucesso!"

        return redirect(url_for("login"))

    return render_template("cadastro.html") 

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":

    # Inicializar/atualizar base de dados antes de iniciar a aplicacao
    db.create_all()

    # Inicia a aplicacao
    app.run(debug=True)
