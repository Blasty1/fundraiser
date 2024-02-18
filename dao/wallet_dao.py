import sqlite3
def get_my_transactions(id_user):
    connection = sqlite3.connect('db/database.db')
    #questa riga va messa prima di creare il cursor
    connection.row_factory = sqlite3.Row #per ottenere dei dizionari come risultati 
    cursor = connection.cursor()
    sql = "SELECT * FROM wallets WHERE id_user = ? ORDER BY datetime(created_at) DESC"
    cursor.execute(sql,(id_user,))

    user  = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return user