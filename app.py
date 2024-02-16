# import module
from flask import abort,Flask, render_template, request, redirect, url_for , flash
from flask_login import LoginManager, login_user , login_required , logout_user,current_user
from flask_session import Session
import dao.user_dao
import dao.fund_dao
import datetime
from models import User
from werkzeug.security import generate_password_hash,check_password_hash
# create the application
app = Flask(__name__)
app.config['SECRET_KEY']='secret'
login_manager = LoginManager()
login_manager.init_app(app)

# homepage
@app.route('/')
def index():
  funds=dao.fund_dao.getAllOpens()
  return render_template('index.html',funds=funds)

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

@app.route('/new_fund')
@login_required
def get_new_fund():
  minDate=datetime.date.today() 
  maxDate=(datetime.date.today() + datetime.timedelta(days=14))
  return render_template('new_fund.html',minDate=minDate,maxDate=maxDate)

@app.route('/new_fund',methods=['POST'])
@login_required
def new_fund():
  fund = request.form.to_dict()
  fund['image']=request.files['image'].filename
  fund['id_user']= current_user.get_id()
  fund['start_timestamp']=datetime.datetime.now()

  errors=dao.fund_dao.checkForErrorsOnParams(fund)

  if(len(errors) != 0):
    flash(errors)
    return redirect(url_for('get_new_fund'))
  
  if(fund['type'] == 'lampo'):
    fund['end_timestamp']=datetime.datetime.now() + datetime.timedelta(minutes=5)
  else:
    fund['end_timestamp']=datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M")

  if(dao.fund_dao.store_fund(fund)):
    if(request.files['image']):
      request.files['image'].save('static/img/'+fund['image'])
    return redirect(url_for('index'))
  
  return abort(503,{"message" : "database is not working for some reasons on creating a new fund"})

@app.route('/fund/<int:id_fund>')
def fund(id_fund):
  fund_found=dao.fund_dao.getFundByID(id_fund)
  user=dao.user_dao.get_user_by_id(fund_found['id_user'])
  fund_found['full_name']=user['name'] + " " + user['surname']
  return render_template('show_fund.html',fund=fund_found)

@app.route('/fund/<int:id_fund>/donation')
def make_donation(id_fund):
  fund_found=dao.fund_dao.getFundByID(id_fund)
  return render_template('make_donation.html',fund=fund_found)

@app.route('/fund/<int:id_fund>/donate',methods=['POST'])
def donate(id_fund):
  fund = request.form.to_dict()
  fund['image']=request.files['image'].filename
  fund['id_user']= current_user.get_id()
  fund['start_timestamp']=datetime.datetime.now()

  errors=dao.fund_dao.checkForErrorsOnParams(fund)

  if(len(errors) != 0):
    flash(errors)
    return redirect(url_for('get_new_fund'))
  
  if(fund['type'] == 'lampo'):
    fund['end_timestamp']=datetime.datetime.now() + datetime.timedelta(minutes=5)
  else:
    fund['end_timestamp']=datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M")

  if(dao.fund_dao.store_fund(fund)):
    if(request.files['image']):
      request.files['image'].save('static/img/'+fund['image'])
    return redirect(url_for('index'))
  
  return abort(503,{"message" : "database is not working for some reasons on creating a new fund"})
