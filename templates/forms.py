from wtforms import Form 
from wtforms import StringField, TextField, PasswordField
from wtforms.fields.html5 import EmailField
 
from wtforms import validators 
class RegistroForm(Form):
    name = StringField('Name')
    username = StringField('Username')
    email = EmailField('Correo electronico')
    password = PasswordField('Contraseña')
    password_validator = PasswordField('Comfirma tu contraseña')


class LoginForm(Form):
    email = EmailField('Correo electronico')
    password = PasswordField('Contraseña')
    