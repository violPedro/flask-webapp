from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import mysql.connector
from mysql.connector import errorcode
from functions import conection, close_conec
#import specie_present
'''
import os
from Crypto.Cipher import AES
from pbkdf2 import PBKDF2
'''

app = Flask(__name__)
app.secret_key = "simulator_pprata" #necessário para inciar a session
app.permanent_session_lifetime = timedelta(days=2)


'''
-------ESTE TRECHO DE CODIGO SERVIU PARA GERAR A NOSSA KEY PARA ENCRIPTAÇÃO DOS DADOS------
key = Fernet.generate_key()
file = open('key.key', 'wb')
file.write(key)
file.close()

#função d eencriptação#---------------------------------

def pad(s):
   return s + ((16-len(s) % 16) * '{')
   #função criada para dar o padding, necessario para a encriptação.

def encrypt(password):
   salt= os.urandom(8)
   key=PBKDF2(password,salt).read(32) #256-bit key
   #print(key)
   iv = os.urandom(16) #128 bit iv
   cipher = AES.new(key, AES.MODE_CBC, iv)
   new_pass=cipher.encrypt(str.encode(pad(password)))
   #print(new_pass)
   package = Set_encryp(new_pass,key,iv)
   return package

#FIM FUNÇAO ENCRYPT--------------------

def decrypt(key, pass_encri, iv):
   cipher = AES.new(key, AES.MODE_CBC, iv)
   dec = cipher.decrypt(pass_encri).decode('utf-8')
   l = dec.count('{')
   return dec[:len(dec)-l]
'''
@app.route('/')
def home():
   return render_template('home.html')

@app.route('/to_log') #isto so serve para fazer o render_template, e para diferenciar se ja tem um session inicada ou nao. 
#desta feita, poupamos recursos á máquina
def log():
   if "user" in session:
      flash(f"Com sessão iniciada.")
      return redirect(url_for('user'))
   
   return render_template('login.html')

#------------------------FUNCAO DE LOGIN--------------------------------------------------
@app.route('/login', methods=['POST', 'GET'])
def login():
   
   if request.method == 'POST':
      print("entrei no POST")
      username=request.form['USER']
      password=request.form['PASS']
      session["user"]= username #se cheguei aqui, o utilizador existe, abro a session
      session.permanent_session_lifetime=True
      sql_query = "SELECT * FROM user WHERE UserName = %s"
      val=(username)
      
      cn = conection() #estableço conecção a nossa base dde dados
      cursor = cn.cursor()

      try:
         cursor.execute(sql_query, (val, )) #tive de adicionar uma ',' pois, nao processava os parametros.
         myresult = cursor.fetchone() #apenas preciso de uma linha, dai o fetchone//
         myresult[1] #tenho acesso ao unico parametro que me interessa do resultset
            #login_credential = myresult[2] #faço o catch da password para confirmar no futuro//
            #flash(f"----------------LOGIN_DATABASE: "+ login_credential)
      except (TypeError):
         session.clear()
         print("Dei a excepçao")
         flash(f"Utilizador inexistente! Tente novamente.", "info")
         close_conec(cn,cursor)
         return render_template('login.html')
            
      else:
         #p_desencriptada=decrypt(myresult[5],myresult[2],myresult[6])
         #print("sou a passe depois de desencriptada: "+ p_desencriptada)
         if password!=myresult[2]:
            session.clear() #limpar dados user
            flash(f"Palavra-passe errada. Por favor tente novamente.", "info")
            close_conec(cn,cursor)
            return render_template('login.html')
         elif myresult[3]==1:
            print("---------SOU ADMIN--------") 
            flash(f"Sessão iniciada com sucesso.", "info")  
            close_conec(cn,cursor)
            return redirect(url_for('user')) #, flag=myresult[3], **request.args))
         else:
            session["id"]=myresult[0]    
            print(session["id"])
            print("vim aqui") 
            flash(f"Sessão iniciada com sucesso.", "info")  
            close_conec(cn,cursor)
            return redirect(url_for('user'))   #flag=myresult[3], **request.args))  

      
      #Caso o utilizador nao exista, um erro será despoletado do tipo TypeError:NoneType,
      #assim, esta excepçao abaixo criada, lidará com este erro, evitando o crash do serviço,
      #e informando que o utilizador nao existe.

#------------------------FIM FUNCAO LOGIN--------------------------------
@app.route('/user')
def user():
   user = session["user"]
   if "user" in session:
      #print("Sou a flag: "+flag)
      if user == 'Administrador':
         return render_template('admin.html', userino=user)  

      return render_template('menu.html', userino=user)

   #se chgou aqui, nao tava logado, e reencaminhado para o login 
   return redirect(url_for('login'))

#-------------------------------FUNCAO REGISTO--------------------------
@app.route('/registo', methods=['POST', 'GET'])
def registo():

   if request.method=='POST':

      username=request.form["USER"]
      password='default'

      if(username==""):
         flash(f"Nome de utilizador inválido. Tente novamente.", "info")
         return redirect(url_for('pre_clean'))

      cn = conection()
      cursor = cn.cursor()

      try:
         sql_query = "SELECT * FROM user WHERE username = %s"
         val=(username)
         cursor.execute(sql_query, (val, ))
         myresult = cursor.fetchone() #apenas preciso de uma linha, dai o fetchone//
         myresult[1] #tenho acesso ao unico parametro que me interessa do resultset
           
            
      except (TypeError):
         print("Dei a excepçao")
         #antes de fazer o insert, irei passar-lhe então os valores da key e salt.
         #set_package=encrypt(password)
         #Neste caso, a excepção e útil para garantirmos que nao há 2 usernames iguais.
         try:
            sql_query="INSERT INTO user (UserName, PPass) VALUES(%s,%s)"
         #print(username)
         #print(password)
            #val=(username,set_package.pass_encri, set_package.key, set_package.iv)
            val=(username,password)
            cursor.execute(sql_query,val)
            cn.commit()
         except mysql.connector.Error as err: #caso algum erro aconteça com o insert.
            print(err)
            flash(f"Um erro inesperado aconteceu. Tente novamente.")
            cn.rollback()
            close_conec(cn, cursor)
            return redirect(url_for('pre_clean'))
         else:   
            flash(f"Utilizador registado com sucesso.", "info")
            close_conec(cn, cursor)
            return redirect(url_for('pre_clean'))
            
      else:     
         print("vim aqui") 
         flash(f"O username já existe. Tente novamente. ", "info")  
         close_conec(cn, cursor)
         return redirect(url_for('pre_clean')) 

@app.route('/logout')
def logout():
   if "user" in session:
      session.clear() #limpar dados user
      flash(f"Sessão terminada com sucesso.", "info") 
      return render_template('login.html')
   else:
      flash(f"Sem sessão iniciada.", "info")
      return render_template("login.html")
      
####---------------------------PARA REMOVER----------------------
@app.route('/gestao')
def pre_clean():
   
   cn = conection()
   cursor = cn.cursor()

   sql_stm="SELECT * FROM user"
   cursor.execute(sql_stm)
   result_set=cursor.fetchall()
   
   #formei um dicionário com o nosso result set
   dic = { row[1]:row[0] for row in result_set }
   
   #aqui elimino o admin da nossa lista, para que nao apareça na tabela.
   dic.pop("Administrador")
   #print(dic)
   
   close_conec(cn, cursor)
   return render_template('gestao_users.html', Utiliz=dic.items())

##-------------OPERAÇÃO PARA DELETE USER--------------------------------
@app.route('/delete/<id>', methods = ['GET', 'POST'])
def erase(id):
   
   cn = conection()
   cursor = cn.cursor()

   try:
      sql_stm="DELETE FROM user WHERE UserID= %s"
      val=(id)
      cursor.execute(sql_stm, (val, ))
      cn.commit()
   except mysql.connector.Error as err:
      print(err)
      flash(f"Aconteceu um erro inesperado, tente novamente.")
      cn.rollback()
      close_conec(cn, cursor)
      return redirect(url_for('pre_clean'))
   else:
      print("CHEGUEI AO FIM")
      close_conec(cn, cursor)
      flash(f"Utilizador eliminado com sucesso.", "info")
      return redirect(url_for('pre_clean'))
  

#---------------------------LISTAGEM SIMULACOES-------------------------
@app.route('/lista_sims')
def listagem_sims():
   cn = conection()
   cursor = cn.cursor()

   sql_stm="SELECT * FROM sims where UserID = %s"
   val=session["id"] #aqui faco o retrieve do id do meu user, para dar uso a listagem das suas simulacoes
   #print(session["id"])
   cursor.execute(sql_stm, (val, ) )
   result_set=cursor.fetchall()
   
   #formei um dicionário com o nosso result set
   dic = { row[1]:row[3] for row in result_set }
   #print(dic)
   close_conec(cn, cursor)
   return render_template('sims.html', simulations=dic.items())

#------------------------APAGAR SIMULACAO--------------------------------
@app.route('/del/<name>', methods = ['GET', 'POST'])
def delete(name):
   cn = conection()
   cursor = cn.cursor()

   try:
      sql_stm="DELETE FROM sims WHERE Designacao= %s"
      val=(name)
      cursor.execute(sql_stm,(val, ))
      cn.commit()
   except mysql.connector.Error as err:
      print(err)
      flash(f"Aconteceu um erro inesperado, tente novamente.")
      cn.rollback()
      close_conec(cn, cursor)
      return redirect(url_for('listagem_sims'))
   else:
      print("CHEGUEI AO FIM")
      close_conec(cn, cursor)
      flash(f"Simulação eliminada com sucesso.", "info")
      return redirect(url_for('listagem_sims'))

#-----------------OPERAÇOES PRA MODAIS DO USEr-------------------------

@app.route('/user/edit', methods=['POST', 'GET'])

def change_username():
   cn = conection()
   cursor = cn.cursor()

   if request.method=='POST':

      username=request.form["USER"]
      sql_query = "SELECT * FROM user WHERE username = %s"

      try:
         val=(username)
         cursor.execute(sql_query, (val, ))
         myresult = cursor.fetchone() #apenas preciso de uma linha, dai o fetchone//
         myresult[1] #tenho acesso ao unico parametro que me interessa do resultset
            
      except (TypeError):
         print("Dei a excepçao")
         #antes de fazer o insert, irei passar-lhe então os valores da key e salt.
         #set_package=encrypt(password)
         #Neste caso, a excepção e útil para garantirmos que nao há 2 usernames iguais.
         try:
            sql_query="UPDATE user SET UserName = %s WHERE UserID= %s"
         #print(username)
         #print(password)
            
            val=(session["id"])
            cursor.execute(sql_query,(username, val, ))
            cn.commit()
         except mysql.connector.Error as err: #caso algum erro aconteça com o insert.
            print(err)
            flash(f"Um erro inesperado aconteceu. Tente novamente.")
            cn.rollback()
            close_conec(cn, cursor)
            return redirect(url_for('user'))
         else:   
            flash(f"Username editado com sucesso. Para que as alterações tenham efeito, por favor volte a entrar.", "info")
            close_conec(cn, cursor)
            return redirect(url_for('user'))
            
      else:     
         print("vim aqui") 
         flash(f"O username já existe. Tente novamente. ", "info")  
         close_conec(cn, cursor)
         return redirect(url_for('user'))

@app.route("/user/pass", methods=['POST', 'GET'])
def change_pass():
   cn = conection()
   cursor = cn.cursor()

   if request.method=='POST':

      password_new=request.form["PASS"]

      sql_query="UPDATE user SET PPass = %s WHERE UserID= %s"

      try:
         #print(username)
         #print(password)
         val=(session["id"])
         cursor.execute(sql_query,(password_new, val, ))
         cn.commit()
      except mysql.connector.Error as err: #caso algum erro aconteça com o insert.
         print(err)
         flash(f"Um erro inesperado aconteceu. Tente novamente.")
         cn.rollback()
         close_conec(cn, cursor)
         return redirect(url_for('user'))
      else:   
         flash(f"Palavra-Passe alterada com sucesso.", "info")
         close_conec(cn, cursor)
         return redirect(url_for('user'))


@app.route("/simulation")
def simula():
   return render_template("simula_1_view.html")

@app.route("/teste_sim", methods=["POST", "GET"])
def teste_script():
   if request.method=='POST':
      print("vou entrar")
      #specie_present.main_teste()
      return redirect(url_for('home'))

if __name__ == '__main__':
  app.run(debug=True)
