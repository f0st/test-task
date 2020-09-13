from flask import Flask, request, g, render_template, flash, make_response, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)

#Настройки приложения

app.config['SECRET_KEY'] = '89274711641b8f44ed1aebcdf0ca5203c347f180' #os.urandom(20).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'testask.send@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'testask.send@gmail.com'  
app.config['MAIL_PASSWORD'] = '9AF32z4Fds'

db = SQLAlchemy(app)
mail = Mail(app)

#Модель представления пользователей
class Users(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer(), primary_key=True)
	email = db.Column(db.String(50), unique=True)
	token = db.Column(db.String(500), nullable=True)
	visits = db.Column(db.Integer(), nullable=True)
	access = db.Column(db.Boolean(), nullable=True)

	def __repr__(self):
		return f"<users {self.id}>"

@app.route('/visits')
def visits():
	if 'access' in session:
		if session.get('access'):
			res = db.session.query(Users).filter(Users.email == session.get('email')).first()
			return render_template('visits.html', access=True, email=session.get('email'), visits=res.visits)
		else:
			return render_template('visits.html',access=False)
	else:
		return render_template('visits.html',access=False)

@app.route('/index')
@app.route('/')
def index():
	if 'access' in session:
		if session.get('access'):
			return render_template('index.html', access=True, email=session.get('email'))
		else:
			return render_template('index.html',access=False)
	else:
		return render_template('index.html',access=False)

@app.route('/token/<token>')
def token(token):
	res = db.session.query(Users).filter(Users.token == str(token)).first()
	if res != None:
		if token == res.token:
			if res.access:
				session['access'] = True
				session['email'] = res.email
				try:
					res.visits += 1
					db.session.commit()
				except:
					return "Error, try again!" 
			return redirect('/')
	else:
		session['access'] = False
		return redirect(url_for('index', _external=True), code='403')

	return redirect('/')

@app.route('/logout')
def logout():
	session.pop('access', None)
	session.pop('email', None)
	return redirect('/')

@app.route('/get_access', methods=['POST', 'GET'])
def get_access():
	if request.method == 'POST':
		token = os.urandom(21).hex()
		email = request.form.get('email')
		try:
			u = Users(email=email, token=token, visits=0, access=True)
			db.session.add(u)
			db.session.commit()
		except:
			return "Error, try again!" 
		msg = Message('Magic url', recipients=[email])
		msg.html = "<h2>Great, you got access</h2>\n<p>To access, follow the <a href=" + url_for('token', token=token,  _external=True) + ">link</a></p>"
		mail.send(msg)
		return redirect('/')

		
if __name__ == "__main__":
    app.run(debug=True)
	