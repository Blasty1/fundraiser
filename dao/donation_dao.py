import sqlite3
def store_fund(donation):
    connection = sqlite3.connect('db/database.db')
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 

    cursor = connection.cursor()
    sql = "INSERT INTO donation(id_fund,amount,created_at,type,name,surname) VALUES(?,?,?,?,?,?)"
    success = False
    try:
        cursor.execute(sql,(donation['id_fund'],donation['amount'],donation['created_at'],donation['type'],donation['name'],donation['surname']))
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