import mysql.connector
from mysql.connector import errorcode

def conection():
    config = {
         'host':'sqlserversimulador.mysql.database.azure.com',
         'user':'myadmin@sqlserversimulador.mysql.database.azure.com',
         'password':'Teste123',
         'database':'projetobd'
    }
# Construct connection string
    try:
        cnx = mysql.connector.connect(**config)
        print("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        return cnx
              

def close_conec(cnx,cursor):
    cnx.close()  
    cursor.close()
    return print("Conec fechada")