from flask import Flask
from flask import render_template
from templates import forms
from flask import request 
from flask import make_response
from flask import redirect, url_for
from flask import session
from flaskext.mysql import MySQL

app = Flask(__name__)
app.secret_key='my_secret_key'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'to_do_list'

mysql = MySQL()
mysql.init_app(app)

@app.route('/')
def home():
    return render_template('pag.html')
    
@app.route('/saber_mas')
def about():
    return render_template('index.html')

@app.route('/registro', methods = ['GET', 'POST'])
def registro():
    registro_form = forms.RegistroForm(request.form)
    if request.method == 'POST':
        name = registro_form.name.data
        username = registro_form.username.data
        email = registro_form.email.data
        password = registro_form.password.data


        if(registro_form.password.data != registro_form.password_validator.data):
            print("Las contraseñas no coinciden!")
            
        else:
            print("Mandar a guardar los datos!!!!")
            cursor = mysql.get_db().cursor()
            # aqui debes mandar a la base de datos
            # y cuando se guarde, redireccionas a login 
            cursor.execute("INSERT INTO usuarios(name, username, email,password) VALUES (%s,%s,%s,%s)", (name,username,email,password))
            cursor.connection.commit()
           # data = cursor.fetchone()
            cursor.close()

            return redirect(url_for('login'))
    return render_template('registro.html', form = registro_form)
    

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login_form = forms.LoginForm(request.form)
    if request.method == 'POST':
        email = login_form.email.data
        password = login_form.password.data
       # session['username'] = login_from.username.data
       # 
        #sesiones basadas en cookies 
        cursor = mysql.get_db().cursor()
        #SELECT name, username, email, password FROM usuarios WHERE email = %s
        cursor.execute("SELECT id,name, username, email, password FROM usuarios WHERE email = (%s)", (email))
        cursor.connection.commit()
        resultado = cursor.fetchone()
        cursor.close()
        print(resultado)
        if (not resultado):
            return redirect(url_for('registro'))
        db_id =str(resultado[0])  
        db_name = resultado[1]
        db_username = resultado[2]
        db_email = resultado[3]
        db_password = resultado[4]
        cursor.close()
        print(f"la contraseña ingresada es:", password)
        print(f"la contraseña en la base de datos es:", db_password)
        print(db_id)

        if password == db_password:
            response = make_response(redirect('/task'))
            response.set_cookie('user', db_username)
            response.set_cookie('id_user', db_id)
            return response
        else: 
            return redirect(url_for('login'))
    return render_template('login.html',form = login_form )

@app.route('/task', methods = ['GET', 'POST'])
def task():
    print("formulario = ",request.form)
    user_cookie = request.cookies.get('user', 'Undefined')
    print(user_cookie)
    id_user_cookie = request.cookies.get('id_user', 'Undefined')
    print(id_user_cookie)
    if user_cookie == 'Undefined': 
        return redirect(url_for('login'))
    cursor = mysql.get_db().cursor()
    if request.method == 'POST':
        lista = request.form.getlist("task")
        cursor.execute("INSERT INTO tareas (task,user_id) VALUES (%s,%s)", (lista, id_user_cookie))
        cursor.connection.commit()
    cursor.execute("SELECT id, task, status FROM tareas WHERE user_id = (%s)", (id_user_cookie))
    cursor.connection.commit()
    resultado = cursor.fetchall()
    cursor.close()
    return render_template('to_do_list.html', tareas = resultado)

@app.route("/completar/<task_id>", methods= ['GET', 'POST'])
def completado(task_id):
    cursor = mysql.get_db().cursor()
    cursor.execute("UPDATE tareas SET status = 0 WHERE id = %s", (task_id))
    cursor.connection.commit()
    cursor.close()
    return redirect(url_for("task"))

@app.route("/desmarcado/<task_id>", methods= ['GET', 'POST'])
def desmarcar(task_id):
    cursor = mysql.get_db().cursor()
    cursor.execute("UPDATE tareas SET status = 1 WHERE id = %s", (task_id))
    cursor.connection.commit()
    cursor.close()
    return redirect(url_for("task"))
@app.route('/cerrar_sesion')
def cerrar():
    response = make_response(redirect('/'))
    response.set_cookie('user', '',expires=0)
    response.set_cookie('id_user','', expires=0)
    return response



if __name__ == '__main__':
    app.run(debug = True, port=8000)