import sqlite3
import html
import datetime
def store_fund(fund):
    connection = sqlite3.connect('db/database.db')
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 

    cursor = connection.cursor()
    sql = "INSERT INTO funds(title,description,image,target,type,max_donation,min_donation,start_timestamp,end_timestamp,id_user) VALUES(?,?,?,?,?,?,?,?,?,?)"
    success = False
    try:
        cursor.execute(sql,(fund['title'],fund['description'],fund['image'],fund['target'],fund['type'],fund['max'],fund['min'],fund['start_timestamp'],fund['end_timestamp'],fund['id_user']))
        connection.commit()
        success = True
    except Exception as e:
        print("error",str(e))
        connection.rollback()
    
    cursor.close()
    connection.close()

    return success

def checkForErrorsOnParams(fund):
    errors={}
    fund['type']=html.escape(fund['type']).strip().lower()
    fund['title']=html.escape(fund['title']).strip()
    fund['description']=html.escape(fund['description']).strip()
    fund['end_timestamp']=html.escape(fund['end_timestamp']).strip()

    if  fund['title'] == '':
        errors['title_']="il campo non puo essere vuoto"
    if fund['description'] == '':
        errors['description']="il campo non puo essere vuoto"
    if fund['type'] != 'lampo' and fund['type'] != 'normale':
        errors['type']="Selezionare una voce corretta"
    if not fund['min'].replace(".", "").isnumeric():
        errors['min']="il campo deve essere un numero reale positivo"
    if not fund['max'].replace(".", "").isnumeric():
        errors['max']="il campo deve essere un numero reale positivo"
    if not fund['target'].replace(".", "").isnumeric():
        errors['target']="il campo deve essere un numero reale positivo"
    if fund['type'] == 'normale' and fund['end_timestamp'] == '':
        errors['end_timestamp']="Con la modalità raccoltà fondo normale è necessario specificare una data di chiusura"

    if len(errors) != 0:
        return errors
    
    fund['min']=float(fund['min'])
    fund['max']=float(fund['max'])
    fund['target']=float(fund['target'])

    if fund['min'] < 0:
        errors['min']="il campo non puo essere negativo"
    if fund['max'] < 0:
        errors['min']="il campo non puo essere negativo"
    if fund['target'] < 0:
        errors['target']="il campo non puo essere negativo"
    if fund['max'] < fund['min']:
        errors['max'] = "Questo valore deve essere più grande del valore minimo"
    if fund['type'] == 'normale' and (datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M") - fund['start_timestamp']).days > 14:
        errors['end_timestamp']="La data deve essere entro 14 giorni da oggi"
    
    if fund['image'] and ( fund['image'].split('.')[-1] not in ['jpeg','jpg','png','gif'] ):
        errors['image']="L'immagine non ha un estensione accettata"

    return errors
                        
def getAllOpens():
    query = 'SELECT * FROM funds WHERE datetime(end_timestamp) > datetime("now","localtime") ORDER BY datetime(end_timestamp)'
    connection = sqlite3.connect('db/database.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query)
    result = [dict(row) for row in cursor]

    # : crea una copia dell'array cosi che possa eliminare l'elemento durante 
    for fund in result[:]:
        fund['remaining_time']=(datetime.datetime.strptime(fund['end_timestamp'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.now())

    cursor.close()
    connection.close()

    return result

def getFundByID(id_fund):
    connection = sqlite3.connect('db/database.db')
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 
    cursor = connection.cursor()
    sql = "SELECT * FROM funds WHERE id_fund = ?"
    cursor.execute(sql,(id_fund,))

    fund  = cursor.fetchone()

    if(fund):
        fund = dict(fund)

    cursor.close()
    connection.close()

    return fund
