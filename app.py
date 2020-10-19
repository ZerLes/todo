# -*- coding: utf-8 -*-
from datetime import datetime, date
from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException


app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = '[secret]'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://[user]:[password]@[host]/todolistdb'
app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE'] = 180

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return db.session.query(User).get(user_id)



@app.route('/', methods=['GET', 'POST'])
def index():

	if current_user.is_authenticated:
		if request.method == "POST":
			delete_note_id = request.form.get('delete')
			done_note_id = request.form.get('done')
			if delete_note_id and db.session.query(Note.id).filter_by(user_id=current_user.get_id()).filter_by(id=delete_note_id).first()[0]:
				db.session.query(Note.id).filter_by(id=delete_note_id).delete()
				db.session.commit()
				return redirect('/')
			if done_note_id and db.session.query(Note.id).filter_by(user_id=current_user.get_id()).filter_by(id=done_note_id).first()[0]:
				print('done')
				note = db.session.query(Note).filter_by(id=done_note_id).first()
				note.isDone= not note.isDone
				db.session.commit()
				return redirect('/')
		notes_id = db.session.query(Note.id).filter_by(user_id=current_user.get_id()).order_by(Note.creationDate).all()
		notes_list = []
		for id in notes_id:
			notes_list.append(Note_show(id[0]))
		notes_list.reverse()
		return render_template('index.html', notes_list=notes_list)
	return render_template('index.html')

@app.route('/addnew', methods=['GET', 'POST'])
def addnew():
	if request.method == "POST":
		title = request.form['title']
		text = request.form['text']
		got_dueDate = request.form['dueDate']
		error=None
		if title=='': 
			error="Введите заголовок"
		if error:
			return render_template('addnew.html', title=title, error=error, text=text, dueDate=got_dueDate)
		if got_dueDate:
			dueDate = datetime.strptime(got_dueDate, '%Y-%m-%d')
		else:
			dueDate = None
		try:
			note = Note(title=title, text=text, dueDate=dueDate)
			db.session.add(note)
			db.session.commit()
			return redirect('/')
		except:
			return render_template('error.html')
	else:
		return render_template('addnew.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == "POST":
		got_login = request.form['login']
		got_password = request.form['password']
		
		login = User.query.filter_by(login=got_login).first()
		if login and login.check_password(password=got_password):
			login_user(login)
			return redirect('/')
		else:
			return render_template('login.html', error="Неверное имя пользователя или пароль")
			
	else:
		return render_template('login.html', error=None)
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == "POST":
		login = request.form['login']
		password1 = request.form['password1']
		password2 = request.form['password2']
		username = request.form['username']
		error=None
		login_db = User.query.filter_by(login=login).first()
		if len(login) < 5: 
			error="Логин не может быть меньше 5 символов"
		elif len(login) > 20: 
			error="Логин не может превышать 20 символов"
		elif login_db:
			error="Пользователь с таким логином уже зарегестрирован"
		elif username == '':
			error="Введите обращение"
		elif len(username) > 80:
			error="Обращение не может превышать 80 символов"
		elif len(password1) < 8: 
			error="Пароль не может быть меньше 8 символов"
		elif password1 != password2:
			error="Пароли не совпадают"
		if error:
			return render_template('register.html', error=error, login=login, password1=password1, password2=password2, username=username)
		try:
			user = User(login=login, password=password1, username=username)
			db.session.add(user)
			db.session.commit()
			return render_template('register_success.html')
		except:
			return render_template('error.html')
	else:
		return render_template('register.html', error=None)

@app.route('/logout')
def logout():
	logout_user()
	return redirect('/')

@app.route('/about')
def about():
	return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html', error = e)
	
@app.errorhandler(HTTPException)
def some_error(e):
	return render_template('error.html', error = e)
	


class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	login = db.Column(db.String(20), unique=True, nullable=False)
	username = db.Column(db.String(80), nullable=False)
	password_hash = db.Column(db.String(50), nullable=False)
	
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
		
	def __init__(self, login, username, password):
		self.login = login
		self.username = username
		self.set_password(password)

	def __repr__(self):
		return f'Note {self.login}'
		

class Note_show():
	
	def __init__(self, id):
		self.id = id
		self.title = db.session.query(Note.title).filter_by(id=id).order_by(Note.creationDate).first()[0]
		self.text = db.session.query(Note.text).filter_by(id=id).order_by(Note.creationDate).first()[0]
		self.creationDate = db.session.query(Note.creationDate).filter_by(id=id).order_by(Note.creationDate).first()[0]
		self.creationDate = self.creationDate.strftime("%Y-%m-%d %H:%M")
		self.dueDate = db.session.query(Note.dueDate).filter_by(id=id).order_by(Note.creationDate).first()[0]
		self.isDateExpired = False
		if self.dueDate:
			self.isDateExpired = self.dueDate < datetime.utcnow()
			self.dueDate = self.dueDate.strftime("%Y-%m-%d")
		self.isDone = db.session.query(Note.isDone).filter_by(id=id).order_by(Note.creationDate).first()[0]
		

class Note(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	title = db.Column(db.String(100), nullable=False)
	text = db.Column(db.Text)
	creationDate = db.Column(db.DateTime)
	dueDate = db.Column(db.DateTime)
	isDone = db.Column(db.Boolean, default=False)
	
	
	def __init__(self, title, text, dueDate, creationDate=None):
		self.title = title
		self.text = text
		if creationDate is None:
			creationDate = datetime.utcnow()
		self.creationDate = creationDate
		self.dueDate = dueDate
		self.isDone = False
		self.user_id = current_user.get_id()
	def __repr__(self):
		return f'Note "{self.title}" by user_id {self.user_id}'
		
		
		
if __name__ == '__main__':
	app.run(debug=False)
