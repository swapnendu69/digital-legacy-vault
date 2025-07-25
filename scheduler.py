from apscheduler.schedulers.background import BackgroundScheduler
from app.utils import check_inactivity
from app.models import User
from app import db, create_app, mail
from flask_mail import Message
from datetime import datetime, timedelta

app = create_app()

def send_reminders():
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.last_login:
                days_inactive = (datetime.utcnow() - user.last_login).days
                if days_inactive >= 7:  # Weekly reminders
                    msg = Message(
                        "Digital Legacy Vault Reminder",
                        recipients=[user.email]
                    )
                    msg.body = f"""
                    This is a reminder to log in to your Digital Legacy Vault.
                    
                    If you don't log in within 90 days, your successors will be granted access.
                    
                    Last login: {user.last_login.strftime('%Y-%m-%d')}
                    Days inactive: {days_inactive}
                    """
                    
                    mail.send(msg)

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_inactivity, trigger="interval", days=1)
scheduler.add_job(func=send_reminders, trigger="interval", days=7)
scheduler.start()