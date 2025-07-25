from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Vault, Successor, User
from . import db
from datetime import datetime, timedelta
from .utils import encrypt_data, decrypt_data
from flask_mail import Message
from . import mail

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    vaults = Vault.query.filter_by(user_id=current_user.id).all()
    successors = Successor.query.filter_by(user_id=current_user.id).all()
    
    # Check inactivity
    last_login = current_user.last_login or datetime.utcnow()
    days_inactive = (datetime.utcnow() - last_login).days
    
    return render_template('dashboard.html', 
                         vaults=vaults, 
                         successors=successors,
                         days_inactive=days_inactive)

@main.route('/add_vault', methods=['GET', 'POST'])
@login_required
def add_vault():
    if request.method == 'POST':
        name = request.form.get('name')
        data = request.form.get('data')
        
        encrypted_data = encrypt_data(data, current_user.password)
        
        new_vault = Vault(
            user_id=current_user.id,
            name=name,
            data=encrypted_data
        )
        
        db.session.add(new_vault)
        db.session.commit()
        
        flash('Vault item added successfully!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_vault.html')

@main.route('/add_successor', methods=['GET', 'POST'])
@login_required
def add_successor():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        relationship = request.form.get('relationship')
        
        new_successor = Successor(
            user_id=current_user.id,
            email=email,
            name=name,
            relationship=relationship
        )
        
        db.session.add(new_successor)
        db.session.commit()
        
        flash('Successor added successfully!')
        return redirect(url_for('main.dashboard'))
    
    return render_template('successors.html')