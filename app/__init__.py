from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from app.models import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_muito_forte_aqui_mude_para_producao'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agencia.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True

db.init_app(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar o sistema.'
login_manager.login_message_category = 'info'

from app.models import Usuario

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

from app import view