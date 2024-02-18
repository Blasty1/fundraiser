# import module
from flask import abort,Flask, render_template, request, redirect, url_for , flash
from flask_login import LoginManager, login_user , login_required , logout_user,current_user
import dao.user_dao
import dao.fund_dao
import dao.donation_dao
import dao.wallet_dao
import datetime
import html
from models import User
from werkzeug.security import generate_password_hash,check_password_hash
import os
# create the application
app = Flask(__name__)
app.config['SECRET_KEY']='secret'
login_manager = LoginManager()
login_manager.init_app(app)

# homepage
@app.route('/')
def index():
  funds=dao.fund_dao.getAllOpens()
  user=None
  if(current_user.is_authenticated):
    user=dao.user_dao.get_user_by_id(current_user.get_id())
  return render_template('index.html',funds=funds,user=user)

@app.route('/get/registration')
def get_registration():
  return render_template('auth/registration.html')

@app.route('/registration',methods=['POST'])
def registration():
  new_user = request.form.to_dict()
  errors=[]
  new_user['name']=html.escape(new_user['name'].strip())
  new_user['surname']=html.escape(new_user['surname'].strip())

  if new_user['name'] == '':
    errors.append("il campo nome non puo essere vuoto")
  
  if new_user['surname'] == '':
    errors.append("il campo cognome non puo essere vuoto")
    
  if new_user['email'] == '' or '@' not in new_user['email']:
    errors.append("il campo email non puo essere vuoto e deve avere un corretto formalismo 'xxx@xxx'")

  if new_user['password'] == '' or len(new_user['password']) <= 7:
    errors.append("La password deve avere una lunghezza maggiore di 7 caratteri")

  if len(errors) != 0:
    flash(errors)
    return redirect(url_for('get_registration'))

  new_user['password'] = generate_password_hash(new_user['password'])

  if(dao.user_dao.get_user_by_email(new_user['email'])):
    flash(['Errore nella creazione utente: l\'email utilizzata è già associata ad un altro account'])
    return redirect(url_for('get_registration'))

  if(dao.user_dao.store_user(new_user)):
    return redirect(url_for('get_login'))
  
  return abort(503,"database is not working for some reasons on creating a new user")
  

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
    fund['end_timestamp']=(datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
  else:
    fund['end_timestamp']=datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M")
  
  fund['start_timestamp']=fund['start_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
  if(dao.fund_dao.store_fund(fund)):
    if(request.files['image']):
      request.files['image'].save('static/img/'+fund['image'])
    return redirect(url_for('index'))
  
  return abort(503,"database is not working for some reasons on creating a new fund")

@app.route('/fund/<int:id_fund>')
def fund(id_fund):
  fund_found=dao.fund_dao.getFundByID(id_fund)
  privilege=False
  if(not fund_found):
    return abort(404,"Raccolta fondi non trovata")
  user=dao.user_dao.get_user_by_id(fund_found['id_user'])
  donations=dao.donation_dao.getDonationsByFound(id_fund)
  fund_found['full_name']=user['name'] + " " + user['surname']
  fund_found['status']= 'aperta' if datetime.datetime.strptime(fund_found['end_timestamp'],"%Y-%m-%d %H:%M:%S") > datetime.datetime.now() else "chiusa"
  widthProgressBar= '100' if donations['total']//fund_found['target'] > 1 else donations['total']/fund_found['target']*100

  if(current_user.is_authenticated and current_user.get_id() == fund_found['id_user']):
    privilege=True
  return render_template('show_fund.html',fund=fund_found,donations=donations,widthProgressBar=widthProgressBar,privilege=privilege)

@app.route('/fund/<int:id_fund>/donation')
def make_donation(id_fund):
  fund_found=dao.fund_dao.getFundByID(id_fund)
  if not fund_found:
      return abort(404,"Raccolta Fondi Non Trovata")

  if datetime.datetime.strptime(fund_found['end_timestamp'],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
    return abort(404,"Raccolta Fondi Chiusa")

  return render_template('make_donation.html',fund=fund_found)

@app.route('/fund/<int:id_fund>/donate',methods=['POST'])
def donate(id_fund):
  don = request.form.to_dict()
  fund = dao.fund_dao.getFundByID(id_fund)
  if not fund:
    return abort(404,"Raccolta Fondi Non Trovata")
  
  if datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now():
    return abort(404,"Raccolta Fondi Chiusa")
  
  errors=dao.donation_dao.checkForErrorsOnParams(don,fund['max_donation'],fund['min_donation'])

  if(len(errors) != 0):
    flash(errors)
    return redirect(url_for('make_donation',id_fund=id_fund))
  
  if(don['type'] == 'anonima'):
    don['name']="anonimo"
    don['surname']="anonimo"

  if(dao.donation_dao.store_donation(don,id_fund)):
    return redirect(url_for('fund',id_fund=id_fund))
  
  return abort(503,"database is not working for some reasons on creating a new donation")

@app.route('/funds/closed')
def funds_closed():
  funds=dao.fund_dao.getAllClosed()
  return render_template('funds_closed.html',funds=funds)


@app.route('/me/funds')
@login_required
def get_my_funds():
  funds=dao.fund_dao.getFundsByUserID(current_user.get_id())
  user=dao.user_dao.get_user_by_id(current_user.get_id())
  return render_template('index.html',funds=funds,user=user)

@app.route('/me/wallet')
@login_required
def get_my_wallet():
  user=dao.user_dao.get_user_by_id(current_user.get_id())
  if( not user ):
      return abort(404,"Utente Non Trovato")
  wallet=dao.wallet_dao.get_my_transactions(current_user.get_id())
  total=0
  last_update="Mai"
  for transaction in wallet:
    total+=transaction['totalReached']
  if(wallet):
    last_update=wallet[0]['created_at']

  info= {
    'total' : total,
    'last_update' : last_update
  }
  return render_template('wallet.html',wallet=wallet,user=user,info=info)

@app.route('/me/fund/<int:id_fund>/change')
@login_required
def change_fund(id_fund):
  fund=dao.fund_dao.getFundByID(id_fund)
  if( not fund ):
      return abort(404,"Raccolta Fondi Non Trovata")

  if(datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now() ):
    return abort(404,"Non puoi modificare una raccolta dati chiusa")
    
  if( fund['id_user'] != current_user.get_id() ):
    return abort(404,"Non puoi modificare una raccolta dati non tua")
  
  fund['end_timestamp'] = datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M")
  minDate=datetime.date.today() 
  maxDate=(datetime.datetime.strptime(fund['start_timestamp'],"%Y-%m-%d %H:%M:%S") + datetime.timedelta(days=14)).strftime("%Y-%m-%d")
  return render_template('change_fund.html',fund=fund,minDate=minDate,maxDate=maxDate)

@app.route('/me/fund/<int:id_fund>/update',methods=['POST'])
@login_required
def update(id_fund):
  fund_old=dao.fund_dao.getFundByID(id_fund)
  if( not fund_old ):
      return abort(404,"Raccolta Fondi Non Trovata")
  
  if( fund_old['id_user'] != current_user.get_id() ):
    return abort(404,"Non puoi modificare una raccolta dati non tua")

  if(datetime.datetime.strptime(fund_old['end_timestamp'],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now() ):
    return abort(404,"Non puoi modificare una raccolta dati chiusa")

  fund = request.form.to_dict()
  fund['image']=request.files['image'].filename
  fund['id_user']= current_user.get_id()
  fund['start_timestamp']=datetime.datetime.strptime(fund_old['start_timestamp'],"%Y-%m-%d %H:%M:%S")
  fund['id_fund']=id_fund

  errors=dao.fund_dao.checkForErrorsOnParams(fund)

  if(len(errors) != 0):
    flash(errors)
    return redirect(url_for('change_fund',id_fund=id_fund))

  if(fund['type'] == 'lampo'):
    fund['end_timestamp']=(fund['start_timestamp'] + datetime.timedelta(minutes=5))
    if(fund['end_timestamp'] < datetime.datetime.now()):
      flash(['Non puoi modificare la raccolta dati nella topologia lampo: è passato troppo tempo dalla creazione'])
      return redirect(url_for('change_fund',id_fund=id_fund))
    fund['end_timestamp'] = fund['end_timestamp'].strftime("%Y-%m-%d %H:%M:%S")
  else:
    fund['end_timestamp']=datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M")


  if(dao.fund_dao.update_found(fund)):
    if(request.files['image']):
      request.files['image'].save('static/img/'+fund['image'])
    return redirect(url_for('get_my_funds'))
  
  return abort(503,"database is not working for some reasons on updating a fund")



@app.route('/me/fund/<int:id_fund>/delete')
@login_required
def delete_fund(id_fund):
  fund=dao.fund_dao.getFundByID(id_fund)

  if not fund:
      return abort(404,"Raccolta Fondi Non Trovata")
  
  if( fund['id_user'] != current_user.get_id() ):
    return abort(404,"Non puoi cancellare una raccolta dati non tua")

  if(datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%d %H:%M:%S") < datetime.datetime.now() ):
    return abort(404,"Non puoi cancellare una raccolta dati chiusa")
  
  if(dao.fund_dao.deleteFund(id_fund)):
      if(fund['image']):
        os.remove(os.path.join(app.static_folder,f"img/{fund['image']}"))
      return redirect(url_for('index'))

  return abort(503,"database is not working for some reasons on deleting a fund")
 


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',e=e), 404

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('404.html',e={'description':"Accesso non autorizzato: è necessario eseguire il login"}), 404