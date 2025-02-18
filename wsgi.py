import click
from models import db, User, Todo, Category, TodoCategory
from app import app
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func


@app.cli.command("init", help="Creates and initializes the database")
def initialize():
    db.drop_all()
    db.init_app(app)
    db.create_all()

    # Create a user
    bob = User('bob', 'bob@mail.com', 'bobpass')
    
    # Create a todo and associate it with the user
    new_todo = bob.create_todo("wash car")
    
    # Add user to the session first, then the todo
    db.session.add(bob)
    db.session.add(new_todo)
    
    # Commit both to the database
    db.session.commit()

    print(bob, new_todo)
    print('Database initialized')


@app.cli.command("get-user", help="Retrieves a User")
@click.argument('username', default='bob')
def get_user(username):
    bob = User.query.filter_by(username=username).first()
    if not bob:
        print(f'{username} not found!')
        return
    print(bob)


@app.cli.command("change-email")
@click.argument('username', default='bob')
@click.argument('email', default='bob@mail.com')
def change_email(username, email):
    bob = User.query.filter_by(username=username).first()
    if not bob:
        print(f'{username} not found!')
        return
    bob.email = email
    db.session.add(bob)
    db.session.commit()
    print(bob)


@app.cli.command('delete-user')
@click.argument('username', default='bob')
def delete_user(username):
    bob = User.query.filter_by(username=username).first()
    if not bob:
        print(f'{username} not found!')
        return
    db.session.delete(bob)
    db.session.commit()
    print(f'{username} deleted')


@app.cli.command('add-todo')
@click.argument('username', default='bob')
@click.argument('text', default='clean room')
def add_task(username, text):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return
    user.create_todo(text)
    db.session.add(user)
    db.session.commit()


@app.cli.command('get-todos')
def get_todos():
    todos = Todo.query.all()
    print(todos)


@app.cli.command('toggle-todo')
@click.argument('todo_id', default=1)
@click.argument('username', default='bob')
def toggle_todo_command(todo_id, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f'{username} not found!')
        return

    todo = Todo.query.filter_by(id=todo_id, user_id=user.id).first()
    if not todo:
        print(f'{username} has no todo id {todo_id}')
        return

    todo.toggle()
    print(f'{todo.text} is {"done" if todo.done else "not done"}!')


# Define the TodoCategory model outside any function
class TodoCategory(db.Model):
    __tablename__ = 'todo_category'
    id = db.Column(db.Integer, primary_key=True)
    todo_id = db.Column(db.Integer, db.ForeignKey('todo.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    last_modified = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<TodoCategory last modified {self.last_modified.strftime("%Y/%m/%d, %H:%M:%S")}>'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    user = db.relationship('User', backref=db.backref('categories', lazy='joined'))
    todos = db.relationship('Todo', secondary='todo_category', backref=db.backref('categories', lazy=True))

    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text

    def __repr__(self):
        return f'<Category user:{self.user.username} - {self.text}>'
