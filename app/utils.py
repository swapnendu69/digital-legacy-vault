from cryptography.fernet import Fernet
import base64
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime, timedelta
from flask_mail import Message
from . import mail

def encrypt_data(data, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return f"{salt.hex()}:{encrypted.decode()}"

def decrypt_data(encrypted_data, password):
    salt_hex, encrypted = encrypted_data.split(':')
    salt = bytes.fromhex(salt_hex)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key)
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()

def check_inactivity():
    from .models import User, Successor, Vault
    from . import db
    
    users = User.query.all()
    for user in users:
        if user.last_login:
            days_inactive = (datetime.utcnow() - user.last_login).days
            if days_inactive >= 90:  # 90 days of inactivity
                successors = Successor.query.filter_by(user_id=user.id).all()
                for successor in successors:
                    if not successor.is_activated:
                        # Send vault data to successor
                        vaults = Vault.query.filter_by(user_id=user.id).all()
                        vault_data = "\n\n".join([
                            f"Vault: {v.name}\nData: {decrypt_data(v.data, user.password)}"
                            for v in vaults
                        ])
                        
                        msg = Message(
                            "Digital Legacy Vault Access Granted",
                            recipients=[successor.email]
                        )
                        msg.body = f"""
                        You have been granted access to {user.email}'s Digital Legacy Vault.
                        
                        Here are the stored items:
                        
                        {vault_data}
                        """
                        
                        mail.send(msg)
                        
                        successor.is_activated = True
                        successor.activation_date = datetime.utcnow()
                        db.session.commit()