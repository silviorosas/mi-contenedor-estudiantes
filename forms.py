from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app import app, db, User  # Importa User desde app.py

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        with app.app_context():
            user = db.session.execute(db.select(User).filter_by(username=username.data)).scalar_one_or_none()
            if user is not None:
                raise ValidationError('Este nombre de usuario ya está en uso.')

    def validate_email(self, email):
        with app.app_context():
            user = db.session.execute(db.select(User).filter_by(email=email.data)).scalar_one_or_none()
            if user is not None:
                raise ValidationError('Esta dirección de correo electrónico ya está registrada.')

class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar sesión')