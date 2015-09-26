from flask_wtf import Form
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired


class SignUpForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
