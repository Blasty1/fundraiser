import sqlite3
import html
import datetime
import config
def store_fund(fund):
    connection = sqlite3.connect(config.DB_PATH)
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

def update_found(fund):
    connection = sqlite3.connect(config.DB_PATH)
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 

    cursor = connection.cursor()
    sql = """ UPDATE funds
              SET title = ?,description = ?,image = ?,target = ?,type = ?,max_donation = ?,min_donation = ?,end_timestamp = ?
              WHERE id_fund = ?; """
    success = False
    try:
        cursor.execute(sql,(fund['title'],fund['description'],fund['image'],fund['target'],fund['type'],fund['max'],fund['min'],fund['end_timestamp'],fund['id_fund']))
        connection.commit()
        success = True
    except Exception as e:
        print("error",str(e))
        connection.rollback()
    
    cursor.close()
    connection.close()
    return success

def checkForErrorsOnParams(fund):
    errors=[]
    fund['type']=html.escape(fund['type']).strip().lower()
    fund['title']=html.escape(fund['title']).strip()
    fund['description']=html.escape(fund['description']).strip()
    fund['end_timestamp']=html.escape(fund['end_timestamp']).strip()

    if  fund['title'] == '':
        errors.append("il campo titolo non puo essere vuoto")
    if fund['description'] == '':
        errors.append("il campo descrizione non puo essere vuoto")
    if fund['type'] != 'lampo' and fund['type'] != 'normale':
        errors.append("il campo tipo di raccolta non puo essere vuoto")
    if not fund['min'].replace(".", "").isnumeric():
        errors.append("il campo donazione minima deve essere un numero reale positivo")
    if not fund['max'].replace(".", "").isnumeric():
        errors.append("il campo donazione massima deve essere un numero reale positivo")
    if not fund['target'].replace(".", "").isnumeric():
        errors.append("il campo obiettivo da raggiungere deve essere un numero reale positivo")
    if fund['type'] == 'normale' and fund['end_timestamp'] == '':
        errors.append("Con la modalità raccoltà fondo normale è necessario specificare una data di chiusura")

    if len(errors) != 0:
        return errors
    
    fund['min']=float(fund['min'])
    fund['max']=float(fund['max'])
    fund['target']=float(fund['target'])

    if fund['min'] < 0:
        errors.append("il campo donazione minima deve essere un numero positivo")
    if fund['max'] < 0:
        errors.append("il campo donazione massima deve essere un numero positivo")
    if fund['target'] < 0:
        errors.append("il campo obiettivo da raggiungere deve essere un numero positivo")
    if fund['max'] < fund['min']:
        errors.append("il campo donazione massima deve essere un numero maggiore del campo donazione minima")
    if fund['type'] == 'normale' and ( (datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M") - fund['start_timestamp']).days > 14  or datetime.datetime.strptime(fund['end_timestamp'],"%Y-%m-%dT%H:%M") < fund['start_timestamp']) :
        errors.append("il campo data chiusura deve contenere una data al più distante 14 giorni da quella di creazione e mai antecedente")
    
    if fund['image'] and ( fund['image'].split('.')[-1] not in ['jpeg','jpg','png','gif'] ):
        errors.append("il campo immagine deve contenere un immagine con estensione accettata")

    return errors

def checkForErrorsForSearching(search):
    errors=[]
    print(search)
    if search['type']:
        search['type']=html.escape(search['type']).strip().lower()
    if search['title']:
        search['title']=html.escape(search['title']).strip()
    if search['start_timestamp_s']:
        search['start_timestamp_s']=html.escape(search['start_timestamp_s']).strip()
    if search['start_timestamp_e']:
        search['start_timestamp_e']=html.escape(search['start_timestamp_e']).strip()

    if search['type'] and search['type'] != 'lampo' and search['type'] != 'normale':
        errors.append("il campo tipo di raccolta non puo essere vuoto")
    if search['min'] and not search['min'].replace(".", "").isnumeric():
        errors.append("il campo donazione minima deve essere un numero reale positivo")
    if search['max'] and (not search['max'].replace(".", "").isnumeric()):
        errors.append("il campo donazione massima deve essere un numero reale positivo")
    if search['target'] and (not search['target'].replace(".", "").isnumeric()):
        errors.append("il campo obiettivo da raggiungere deve essere un numero reale positivo")

    if len(errors) != 0:
        return errors
    
    if search['min']:
        search['min']=float(search['min'])
        if search['min'] < 0:
            errors.append("il campo donazione minima deve essere un numero positivo")
    if search['max']:
        search['max']=float(search['max'])
        if search['max'] < 0:
            errors.append("il campo donazione massima deve essere un numero positivo")
    if search['target']:
        search['target']=float(search['target'])
        if search['target'] < 0:
            errors.append("il campo obiettivo da raggiungere deve essere un numero positivo")

    if search['min'] and search['max'] and search['max'] < search['min']:
        errors.append("il campo donazione massima deve essere un numero maggiore del campo donazione minima")
    if search['start_timestamp_s'] and search['start_timestamp_e'] and datetime.datetime.strptime(search['start_timestamp_e'],"%Y-%m-%dT%H:%M") < datetime.datetime.strptime(search['start_timestamp_s'],"%Y-%m-%dT%H:%M"):
        errors.append("il campo Intervallo Data di Creazione deve essere coerente: la prima data deve essere più piccola della seconda")
    
    return errors



def getAllOpens():
    query = 'SELECT * FROM funds WHERE datetime(end_timestamp) > datetime("now","localtime") ORDER BY datetime(end_timestamp)'
    print("test",config.DB_PATH)

    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(query)
    result = [dict(row) for row in cursor]

    # : crea una copia dell'array cosi che possa eliminare l'elemento durante 
    for fund in result[:]:
        rem_time=datetime.datetime.strptime(fund['end_timestamp'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.now()
        if(rem_time.days != 1):
            diffFormatting = str(rem_time).split("days,")[1] if len(str(rem_time).split("days,")) == 2 else str(rem_time)
        else:
            diffFormatting = str(rem_time).split("day,")[1] if len(str(rem_time).split("day,")) == 2 else str(rem_time)

        fund['remaining_time']={
            'days' : rem_time.days,
            'hours' :  diffFormatting.split(":")[0],
            'minutes' : diffFormatting.split(":")[1],
            'seconds' : diffFormatting.split(":")[2].split(".")[0]
        }
    
    cursor.close()
    connection.close()

    return result

def getFundByID(id_fund):
    connection = sqlite3.connect(config.DB_PATH)
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
                     
def getAllClosed():
    queryInner = 'SELECT funds.id_fund,SUM(amount) AS totalReached FROM funds,donations WHERE donations.id_fund = funds.id_fund AND datetime(end_timestamp) < datetime("now","localtime") GROUP BY funds.id_fund'
    queryOuter= f"SELECT * FROM funds LEFT JOIN ({queryInner}) AS innerQuery ON funds.id_fund = innerQuery.id_fund WHERE datetime(end_timestamp) < datetime('now','localtime') ORDER BY (totalReached - target) DESC"

    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(queryOuter)
    result=cursor.fetchall()

    cursor.close()
    connection.close()

    return result

def getFundsByUserID(id_user):
    query = 'SELECT * FROM funds WHERE datetime(end_timestamp) > datetime("now","localtime") AND id_user = ? ORDER BY datetime(end_timestamp)'
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query,(id_user,))
    result = [dict(row) for row in cursor]

    # : crea una copia dell'array cosi che possa eliminare l'elemento durante 
    for fund in result[:]:
        rem_time=datetime.datetime.strptime(fund['end_timestamp'], '%Y-%m-%d %H:%M:%S') - datetime.datetime.now()
        print(str(rem_time).split("days,"))
        if(rem_time.days != 1):
            diffFormatting = str(rem_time).split("days,")[1] if len(str(rem_time).split("days,")) == 2 else str(rem_time)
        else:
            diffFormatting = str(rem_time).split("day,")[1] if len(str(rem_time).split("day,")) == 2 else str(rem_time)

        fund['remaining_time']={
            'days' : rem_time.days,
            'hours' :  diffFormatting.split(":")[0],
            'minutes' : diffFormatting.split(":")[1],
            'seconds' : diffFormatting.split(":")[2].split(".")[0]
        }
    
    cursor.close()
    connection.close()

    return result

def deleteFund(fund_id):
    connection = sqlite3.connect(config.DB_PATH)
    cursor = connection.cursor()
    sql="DELETE FROM funds WHERE id_fund = ?"
    success = False
    try:
        cursor.execute(sql,(fund_id,))
        connection.commit()
        success = True
    except Exception as e:
        print("error",str(e))
        connection.rollback()
    
    cursor.close()
    connection.close()

    return success

def searchForFundsWithOption(searchParam):
    query = "SELECT * FROM funds WHERE"
    params=[]
    if searchParam['title']:
        params.append(f"%{searchParam['title']}%")
        query += " title LIKE ? AND"
    if searchParam['type']:
        params.append(searchParam['type'])
        query += " type = ? AND"
    if searchParam['target']:
        params.append(searchParam['target'])
        query += " target = ? AND"
    if searchParam['min']:
        params.append(searchParam['min'])
        query += " min_donation = ? AND"
    if searchParam['max']:
        params.append(searchParam['max'])
        query += " max_donation = ? AND"
    if searchParam['start_timestamp_s']:
        params.append(searchParam['start_timestamp_s'])
        query += " datetime(start_timestamp) >= datetime(?) AND"
    if searchParam['start_timestamp_e']:
        params.append(searchParam['start_timestamp_e'])
        query += " datetime(start_timestamp) <= datetime(?) AND"
    

    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    query=query.rsplit(' ', 1)[0] # per eliminare l'ultimo AND 


    cursor.execute(query,tuple(param for param in params))
    result = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return result