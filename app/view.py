from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models import Usuario, Pacote, Cliente, Reserva, Historico
from app.forms import LoginForm, CadastroForm, PacoteForm, ReservaForm, CancelarReservaForm, DeleteForm
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
import click
from sqlalchemy import func, exc

@app.route('/')
@login_required
def index():
    pacotes_ativos = Pacote.query.filter(Pacote.data_inicio >= date.today()).count()
    reservas_pendentes = Reserva.query.filter_by(status='ativa').count()
    
    subquery = db.session.query(
        Reserva.pacote_id,
        func.count(Reserva.id).label('reservas_count')
    ).filter(Reserva.status == 'ativa').group_by(Reserva.pacote_id).subquery()

    pacotes_com_alerta = db.session.query(
        Pacote,
        subquery.c.reservas_count
    ).outerjoin(subquery, Pacote.id == subquery.c.pacote_id).all()

    alertas = []
    for pacote, count in pacotes_com_alerta:
        reservas_count = count or 0
        if reservas_count < pacote.vagas_min:
            alertas.append(f"Insuficiente ({reservas_count}/{pacote.vagas_min}) em {pacote.destino}")
        if reservas_count > pacote.vagas_max:
            alertas.append(f"Overbooking em {pacote.destino} (excede {pacote.vagas_max} vagas)")
            
    return render_template('index.html', pacotes=pacotes_ativos, reservas=reservas_pendentes, alertas=alertas)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    login_form = LoginForm()
    cadastro_form = CadastroForm()

    if login_form.validate_on_submit():
        user = Usuario.query.filter_by(username=login_form.username.data).first()
        if user and check_password_hash(user.password, login_form.password.data):
            login_user(user)
            try:
                hist = Historico(usuario_id=user.id, acao='login', descricao=f'Usuário {user.username} logou no sistema.')
                db.session.add(hist)
                db.session.commit()
            except exc.SQLAlchemyError:
                db.session.rollback()
                flash('Erro ao registrar histórico de login.', 'danger')
            return redirect(url_for('index'))
        else:
            flash('Login inválido. Verifique seu usuário e senha.', 'danger')
            
    return render_template('login.html', login_form=login_form, cadastro_form=cadastro_form)

@app.route('/cadastro', methods=['POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = CadastroForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        
        user_role = 'atendente'
        if form.secret_code.data == app.config.get('SECRET_ADMIN_CODE', 'DEFAULT_CODE_DO_NOT_USE'):
            user_role = 'admin'

        novo_usuario = Usuario(
            username=form.username.data, 
            email=form.email.data, 
            password=hashed_password,
            role=user_role
        )
        
        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Por favor, faça o login.', 'success')
            return redirect(url_for('login'))
        except exc.IntegrityError:
            db.session.rollback()
            flash('Erro: Nome de usuário ou e-mail já cadastrado.', 'danger')
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ocorreu um erro inesperado no cadastro: {e}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')

    login_form = LoginForm()
    return render_template('login.html', login_form=login_form, cadastro_form=form)

@app.route('/logout')
@login_required
def logout():
    try:
        hist = Historico(usuario_id=current_user.id, acao='logout', descricao=f'Usuário {current_user.username} saiu do sistema.')
        db.session.add(hist)
        db.session.commit()
    except exc.SQLAlchemyError:
        db.session.rollback()

    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('login'))

@app.route('/pacotes')
@login_required
def listar_pacotes():
    page = request.args.get('page', 1, type=int)
    pacotes = Pacote.query.order_by(Pacote.data_inicio.asc()).paginate(page=page, per_page=10)
    
    edit_form = PacoteForm()
    delete_form = DeleteForm()
    return render_template('gerenciar_pacotes.html', pacotes=pacotes, edit_form=edit_form, delete_form=delete_form)

@app.route('/pacotes/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_pacote():
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    
    form = PacoteForm()
    if form.validate_on_submit():
        novo_pacote = Pacote()
        form.populate_obj(novo_pacote)
        
        try:
            db.session.add(novo_pacote)
            db.session.flush()

            hist = Historico(usuario_id=current_user.id, pacote_id=novo_pacote.id, acao='cadastrar_pacote', descricao=f'Pacote "{novo_pacote.destino}" cadastrado por {current_user.username}.')
            db.session.add(hist)
            db.session.commit()
            
            flash('Pacote cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_pacotes'))
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ocorreu um erro ao cadastrar o pacote: {e}', 'danger')
            
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')
            
    return render_template('cadastrar_pacote.html', form=form)

@app.route('/pacotes/editar/<int:pacote_id>', methods=['POST'])
@login_required
def editar_pacote(pacote_id):
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('listar_pacotes'))

    pacote = Pacote.query.get_or_404(pacote_id)
    form = PacoteForm()

    if form.validate_on_submit():
        try:
            form.populate_obj(pacote)
            hist = Historico(usuario_id=current_user.id, pacote_id=pacote.id, acao='edicao_pacote', descricao=f'Pacote "{pacote.destino}" editado por {current_user.username}.')
            db.session.add(hist)
            db.session.commit()
            flash('Pacote atualizado com sucesso!', 'success')
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o pacote: {e}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Erro no campo '{getattr(form, field).label.text}': {error}", 'danger')

    return redirect(url_for('listar_pacotes'))

@app.route('/pacotes/excluir/<int:pacote_id>', methods=['POST'])
@login_required
def excluir_pacote(pacote_id):
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('listar_pacotes'))

    pacote = Pacote.query.get_or_404(pacote_id)
    form = DeleteForm()

    if form.validate_on_submit():
        try:
            destino_pacote = pacote.destino
            hist = Historico(usuario_id=current_user.id, acao='exclusao_pacote', descricao=f'Pacote "{destino_pacote}" excluído por {current_user.username}.')
            db.session.add(hist)
            db.session.delete(pacote)
            db.session.commit()
            flash('Pacote excluído com sucesso!', 'success')
        except exc.SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Erro ao excluir o pacote: {e}', 'danger')
    
    return redirect(url_for('listar_pacotes'))

@app.route('/reservas', methods=['GET', 'POST'])
@login_required
def gerenciar_reservas():
    form = ReservaForm()
    cancel_form = CancelarReservaForm()
    
    page = request.args.get('page', 1, type=int)
    reservas_ativas = Reserva.query.filter_by(status='ativa').order_by(Reserva.data_reserva.desc()).paginate(page=page, per_page=10)
    
    if form.validate_on_submit():
        pacote = Pacote.query.get_or_404(form.pacote_id.data)
        if pacote.vagas_disponiveis <= 0:
            flash('Não há vagas disponíveis para este pacote.', 'danger')
        else:
            try:
                cliente = Cliente.query.filter_by(email=form.cliente_email.data).first()
                if not cliente:
                    cliente = Cliente(nome=form.cliente_nome.data, email=form.cliente_email.data)
                    db.session.add(cliente)
                    db.session.flush()

                reserva = Reserva(cliente_id=cliente.id, pacote_id=pacote.id, status='ativa')
                hist = Historico(usuario_id=current_user.id, cliente_id=cliente.id, pacote_id=pacote.id, acao='nova_reserva', descricao=f'Reserva para "{pacote.destino}" criada para o cliente {cliente.nome} por {current_user.username}.')
                db.session.add(reserva)
                db.session.add(hist)
                db.session.commit()
                flash('Reserva registrada com sucesso!', 'success')
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Erro ao registrar a reserva: {e}', 'danger')
        
        return redirect(url_for('gerenciar_reservas'))
    
    return render_template('gerenciar_reservas.html', form=form, reservas=reservas_ativas, cancel_form=cancel_form)

@app.route('/reservas/cancelar/<int:reserva_id>', methods=['POST'])
@login_required
def cancelar_reserva(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    form = CancelarReservaForm()

    if form.validate_on_submit():
        if reserva.status == 'cancelada':
            flash('Esta reserva já foi cancelada.', 'info')
        else:
            try:
                reserva.status = 'cancelada'
                hist = Historico(usuario_id=current_user.id, cliente_id=reserva.cliente_id, pacote_id=reserva.pacote_id, acao='cancelamento_reserva', descricao=f'Reserva para "{reserva.pacote.destino}" do cliente {reserva.cliente.nome} cancelada por {current_user.username}.')
                db.session.add(hist)
                db.session.commit()
                flash('Reserva cancelada com sucesso!', 'success')
            except exc.SQLAlchemyError as e:
                db.session.rollback()
                flash(f'Erro ao cancelar a reserva: {e}', 'danger')
            
    return redirect(url_for('gerenciar_reservas'))

@app.route('/historico')
@login_required
def historico():
    if current_user.role != 'admin':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    historicos = Historico.query.order_by(Historico.data_acao.desc()).paginate(page=page, per_page=20)
    
    return render_template('historico.html', historicos=historicos)

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("email")
@click.argument("password")
def create_admin(username, email, password):
    if Usuario.query.filter_by(username=username).first():
        print(f"Erro: Usuário '{username}' já existe.")
        return
    if Usuario.query.filter_by(email=email).first():
        print(f"Erro: Email '{email}' já existe.")
        return

    hashed_password = generate_password_hash(password)
    admin_user = Usuario(
        username=username,
        email=email,
        password=hashed_password,
        role='admin'
    )
    try:
        db.session.add(admin_user)
        db.session.commit()
        print(f"Usuário administrador '{username}' criado com sucesso!")
    except exc.SQLAlchemyError as e:
        db.session.rollback()
        print(f"Erro ao criar administrador: {e}")