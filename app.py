# import module
from flask import Flask, render_template, request, redirect, url_for , flash
from flask_login import LoginManager, login_user , login_required , logout_user
from flask_session import Session
import dao.user_dao
from models import User
import json
from werkzeug.security import generate_password_hash,check_password_hash
# create the application

app = Flask(__name__)
app.config['SECRET_KEY']='secret'

login_manager = LoginManager()
login_manager.init_app(app)

# homepage
@app.route('/')
def index():
  return render_template('index.html')

@app.route('/get/registration')
def get_registration():
  return render_template('auth/registration.html')

@app.route('/registration',methods=['POST'])
def registration():
  new_user = request.form.to_dict()
  errors={}
  if new_user['name'] == '':
    errors['name']="il campo non puo essere vuoto"
  
  if new_user['surname'] == '':
    errors['surname']="il campo non puo essere vuoto"
    
  if new_user['email'] == '' or '@' not in new_user['email']:
    errors['email']="il campo non puo essere vuoto e deve avere un corretto formalismo 'xxx@xxx' "

  if new_user['password'] == '' or len(new_user['password']) <= 7:
    errors['password']="La password deve avere una lunghezza maggiore di 7 caratteri"

  if len(errors) != 0:
    flash(errors)
    return redirect(url_for('get_registration'))

  new_user['password'] = generate_password_hash(new_user['password'])

  if(dao.user_dao.store_user(new_user)):
    return redirect(url_for('get_login'))
  
  flash({'email' : 'Errore nella creazione utente: è necessario verificare che non si abbia già utilizzato questa email con un altro account'})
  return redirect(url_for('get_registration'))
  

@app.route('/login')
def get_login():
  return render_template('auth/login.html')

@app.route('/login',methods=['POST'])
def login():
  user = request.form.to_dict()

  user_db = dao.user_dao.get_user_by_email(user['email'])
  if not user_db or not check_password_hash(user_db['password'],user['password']):
    flash("Credenziali errate")
    return redirect(url_for('get_login'))
  else:
      #l'utente esiste e faccio il login
      #creo un istanza utente
      new = User(id_user=user_db['id_user'],
              name=user_db['name'],
              surname=user_db['surname'],
              email=user_db['email'],
              password=user_db['password'])
      login_user(new,True)
      return redirect(url_for('index'))
  
@login_manager.user_loader
def load_user(user_id):
  db_user=dao.user_dao.get_user_by_id(user_id)
  user = User(id_user=db_user['id_user'],
               name=db_user['name'],
               surname=db_user['surname'],
               email=db_user['email'],
               password=db_user['password'])
  return user

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))

