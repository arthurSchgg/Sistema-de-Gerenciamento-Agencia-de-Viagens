from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, EqualTo
from datetime import date
from app.models import Pacote, Cliente, Usuario

class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(min=4, max=80)])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class CadastroForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    secret_code = StringField('Código de Administrador (Opcional)')
    submit = SubmitField('Cadastrar')

    def validate_username(self, username):
        user = Usuario.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já está em uso.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado.')

class PacoteForm(FlaskForm):
    destino = StringField('Destino', validators=[DataRequired(), Length(min=3, max=100)])
    data_inicio = DateField('Data Início', format='%Y-%m-%d', validators=[DataRequired()])
    data_fim = DateField('Data Fim', format='%Y-%m-%d', validators=[DataRequired()])
    preco = FloatField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0.01)])
    vagas_min = IntegerField('Vagas Mínimas', validators=[DataRequired(), NumberRange(min=1)])
    vagas_max = IntegerField('Vagas Máximas', validators=[DataRequired(), NumberRange(min=1)])
    categoria = SelectField('Categoria', choices=[('Luxo', 'Luxo'), ('Padrão', 'Padrão'), ('Econômico', 'Econômico')], validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[Length(max=500)])
    politicas_cancelamento = TextAreaField('Políticas de Cancelamento', validators=[Length(max=500)])
    submit = SubmitField('Cadastrar Pacote')

    def validate_data_inicio(self, field):
        if field.data < date.today():
            raise ValidationError('Data de início deve ser futura.')

    def validate_data_fim(self, field):
        if self.data_inicio.data and field.data <= self.data_inicio.data:
            raise ValidationError('Data de fim deve ser posterior à data de início.')

    def validate_vagas_max(self, field):
        if self.vagas_min.data and field.data < self.vagas_min.data:
            raise ValidationError('Vagas máximas devem ser maiores ou iguais às mínimas.')

class ReservaForm(FlaskForm):
    cliente_nome = StringField('Nome do Cliente', validators=[DataRequired(), Length(min=3, max=100)])
    cliente_email = StringField('Email do Cliente', validators=[DataRequired(), Email()])
    pacote_id = SelectField('Pacote', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Registrar Reserva')

    def __init__(self, *args, **kwargs):
        super(ReservaForm, self).__init__(*args, **kwargs)
        self.pacote_id.choices = [(p.id, f"{p.destino} ({p.data_inicio.strftime('%d/%m/%Y')})") for p in Pacote.query.filter(Pacote.data_inicio >= date.today()).order_by(Pacote.destino).all()]

class CancelarReservaForm(FlaskForm):
    motivo = TextAreaField('Motivo do Cancelamento (opcional)', validators=[Length(max=200)])
    submit = SubmitField('Confirmar Cancelamento')
    
class DeleteForm(FlaskForm):
    submit = SubmitField('Confirmar Exclusão')