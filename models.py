from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app import app

db = SQLAlchemy(app)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(120), nullable=False)
  todos = db.relationship('Todo', backref='user', lazy=True, cascade="all, delete-orphan")

  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.set_password(password)

  def create_todo(self, text):
    new_todo = Todo(text)
    self.todos.append(new_todo)
    return new_todo
    
  def set_password(self, password):
    """Create hashed password."""
    self.password = generate_password_hash(password)

  def __repr__(self):
    return f'<User {self.id} {self.username} - {self.email}>'

class Todo(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #set userid as a foreign key to user.id 
  text = db.Column(db.String(255), nullable=False)
  done = db.Column(db.Boolean, default=False)
  #user = <user object>

  def toggle(self):
    self.done = not self.done
    db.session.add(self)
    db.session.commit()

  def __init__(self, text):
      self.text = text

  def __repr__(self):
    
    return f'<Todo: {self.id} | {self.user.username} | {self.text} | { "done" if self.done else "not done" }>'