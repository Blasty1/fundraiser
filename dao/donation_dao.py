import sqlite3
import html
from datetime import datetime
import config
def store_donation(donation,id_fund):
    connection = sqlite3.connect(config.DB_PATH)
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 

    cursor = connection.cursor()
    sql = "INSERT INTO donations(id_fund,amount,created_at,type,name,surname) VALUES(?,?,?,?,?,?)"
    success = False
    try:
        cursor.execute(sql,(id_fund,donation['amount'],datetime.now().strftime("%Y-%m-%d %H:%M:%S"),donation['type'],donation['name'],donation['surname']))
        connection.commit()
        success = True
    except Exception as e:
        print("error",str(e))
        connection.rollback()
    
    cursor.close()
    connection.close()

    return success
def getDonationsByFound(id_fund):
    query = 'SELECT * FROM donations WHERE id_fund == ? ORDER BY amount DESC'
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query,(id_fund,))
    result = [dict(row) for row in cursor]
    donations={
        'donations' : result,
        'total': 0
    }
    for donation in donations['donations']:
        donations['total']+=donation['amount']
    cursor.close()
    connection.close()

    return donations
def checkForErrorsOnParams(don,max,min):
    errors=[]
    don['type']=html.escape(don['type']).strip().lower()
    don['amount']=html.escape(don['amount']).strip()
    don['address']=html.escape(don['address']).strip()
    don['name']=html.escape(don['name']).strip()
    don['surname']=html.escape(don['surname']).strip()

    if don['name'] == '':
        errors.append("il campo nome non puo essere vuoto")
    if don['surname'] == '':
        errors.append("il campo cognome non puo essere vuoto")
    if don['address'] == '':
        errors.append('Il campo indirizzo non puo essere vuoto')
    if not don['cardNumber'].replace(" ","").isnumeric() or len(don['cardNumber'].replace(" ","")) != 16:
        errors.append('Il campo Numero di Carta non ha un formato corretto')
    if not don['cardPin'].isdigit():
        errors.append('Il campo Pin non ha un formato corretto')
    try:
        expire=datetime.strptime(don['cardDeadline'],"%Y-%m")
        if( expire < datetime.now() ):
            errors.append('La carta risulta essere scaduta')
    except Exception as e:
        print(str(e))
        errors.append('Il formato del campo Scadenza non è corretto')

    if don['type'] != 'anonima' and don['type'] != 'pubblica':
        errors.append("Selezionare una donazione corretta")
    
    if not don['amount'].replace(".", "").isnumeric():
        errors.append("il campo deve essere un numero reale positivo")
   
    if len(errors) != 0:
        return errors
    
    don['amount']=float(don['amount'])

    if don['amount'] < 0:
        errors.append("il campo Importo Donazione non puo essere negativo")
    if don['amount'] > max:
        errors.append(f"La donazione massima ammessa è {max}")
    if don['amount'] < min:
        errors.append(f"la donazione minima ammessa è {min}")
    
    return errors
    