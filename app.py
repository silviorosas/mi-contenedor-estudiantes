from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'register'

# Define los modelos dentro de una función que toma la app como argumento
def init_models(app):
    from flask_login import UserMixin
    from sqlalchemy import Column, Integer, String

    class User(db.Model, UserMixin):
        __tablename__ = 'users' # Es buena práctica definir el nombre de la tabla
        id = Column(Integer, primary_key=True)
        username = Column(String(80), unique=True, nullable=False)
        email = Column(String(120), unique=True, nullable=False)
        password = Column(String(256), nullable=False)

        def __repr__(self):
            return f'<User {self.username}>'

        @property
        def is_authenticated(self):
            return True

        @property
        def is_active(self):
            return True

        @property
        def is_anonymous(self):
            return False

        def get_id(self):
            return str(self.id)
    return User

# Inicializa los modelos
User = init_models(app)

# Importa los formularios DENTRO de las funciones donde se utilizan
# Esto asegura que 'app' y 'User' ya estén completamente inicializados

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    from forms import RegistrationForm  # Importa aquí
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    from forms import LoginForm  # Importa aquí
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not check_password_hash(user.password, form.password.data):
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('auth/login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.username)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)