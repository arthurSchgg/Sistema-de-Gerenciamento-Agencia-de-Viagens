from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='atendente', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Pacote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destino = db.Column(db.String(100), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    vagas_min = db.Column(db.Integer, nullable=False)
    vagas_max = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text)
    politicas_cancelamento = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservas = db.relationship('Reserva', backref='pacote', lazy=True, cascade='all, delete-orphan')

    @property
    def vagas_disponiveis(self):
        reservas_ativas = Reserva.query.filter_by(pacote_id=self.id, status='ativa').count()
        return self.vagas_max - reservas_ativas

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reservas = db.relationship('Reserva', backref='cliente', lazy=True, cascade='all, delete-orphan')

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    pacote_id = db.Column(db.Integer, db.ForeignKey('pacote.id'), nullable=False)
    data_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='ativa', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    pacote_id = db.Column(db.Integer, db.ForeignKey('pacote.id'), nullable=True)
    acao = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_acao = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.relationship('Usuario', backref='historicos')