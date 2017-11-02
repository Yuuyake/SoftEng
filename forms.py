from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators, Form, BooleanField, SelectField, RadioField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms_components import IntegerField


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])

    password = PasswordField('Password',[validators.DataRequired()])

class RegisterForm(Form):
    username = StringField('Username',
                           [validators.Length(min=4, max=15), validators.DataRequired()])
    password = PasswordField('Password',
                             [validators.Length(min=4, max=15), validators.DataRequired(),
                              validators.EqualTo('confirmPass', message="Passwords do not match!")])
    confirmPass = PasswordField('Confirm Password')

class UpdateProfileForm(Form):
    nickname = StringField('Nickname', [validators.Length(min=4, max=20), validators.DataRequired()])
    bio = TextAreaField('Bio', [validators.Length(max=100)])

class ChangePassForm(Form):
    password = PasswordField('Password',
                             [validators.Length(min=4, max=15), validators.DataRequired(),
                              validators.EqualTo('confirmPass', message="Passwords do not match!")])
    confirmPass = PasswordField('Confirm Password')
