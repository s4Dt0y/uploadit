import sqlalchemy as sa
import sqlalchemy.orm as so
from time import time
from uploadit import db, app
from typing import Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import jwt

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = db.Column(db.String(256))

    uploads: so.WriteOnlyMapped['File'] = so.relationship(back_populates='uploader')


    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'
        )
    
    @staticmethod 
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')['reset_password']
        except:
            return
        
        return db.session.get(User, id)
    
class File(db.Model):
    __tablename__ = "files"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    filekey: so.Mapped[str] = so.mapped_column(db.String(50), index=True, unique=True) 
    filename: so.Mapped[str] = so.mapped_column(db.String())
    secure_filename: so.Mapped[str] = so.mapped_column(db.String(), unique=True)
    is_public: so.Mapped[bool] = so.mapped_column(db.Boolean())
    timestamp: so.Mapped[str] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)    
    uploader: so.Mapped[User] = so.relationship(back_populates='uploads')

    def __repr__(self):
        return f"<File: {self.filename}"    
    