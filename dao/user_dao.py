import sqlite3
def store_user(user):
    connection = sqlite3.connect('db/database.db')
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 

    cursor = connection.cursor()
    sql = "INSERT INTO users(name,surname,email,password) VALUES(?,?,?,?)"
    success = False
    try:
        cursor.execute(sql,(user['name'],user['surname'],user['email'],user['password']))
        connection.commit()
        success = True
    except Exception as e:
        print("error",str(e))
        connection.rollback()
    
    cursor.close()
    connection.close()

    return success

def get_user_by_email(user_email):
    connection = sqlite3.connect('db/database.db')
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 
    cursor = connection.cursor()
    sql = "SELECT * FROM users WHERE email = ?"
    cursor.execute(sql,(user_email,))

    user  = cursor.fetchone()
    

    cursor.close()
    connection.close()

    return user

def get_user_by_id(user_id):
    connection = sqlite3.connect('db/database.db')

    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 
    cursor = connection.cursor()
    sql = "SELECT * FROM users WHERE id_user = ?"
    cursor.execute(sql,(user_id,))

    user  = cursor.fetchone()

    cursor.close()
    connection.close()

    return user