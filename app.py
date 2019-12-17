from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from forms import LoginForm, SignupForm
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from flask_migrate import Migrate

app = Flask(__name__)
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///" + os.path.join(project_dir) + "\database.db"
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.config['SECRET_KEY'] = 'my secret'
db = SQLAlchemy()
db.init_app(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False, unique=False)
    email = db.Column(db.String, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    roles = db.Column(db.String, nullable=False)


with app.app_context():
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/users')
def show_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/profile', methods=["POST", "GET"])
def profile():
    username = request.form["profile"]
    profiles = User.query.filter_by(username=username)
    return render_template("profile.html", profiles=profiles)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    username = request.form['target_user']
    user_found = User.query.filter_by(username=username).first()
    db.session.delete(user_found)
    db.session.commit()

    users = User.query.all()
    return redirect(url_for('show_users', users=users))


@app.route('/update_profile', methods=["POST"])
def update_profile():
    username = request.form['target_user']
    roles = request.form['target_role']
    email = request.form['target_email']
    number = request.form['target_number']
    user_found = User.query.filter_by(username=username).first()
    user_found.username = username
    user_found.email = email
    user_found.roles = roles
    user_found.number = number

    db.session.add(user_found)
    db.session.commit()
    users = User.query.all()
    return redirect(url_for('show_users', users=users))


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    password = form.password.data
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user.password == password:
            login_user(user)
            flash("You are logged in as {}".format(form.username.data), "success")
            return redirect(url_for('dashboard', user=user))
        else:
            flash("Invalid Credentials", "danger")
    return render_template('login.html', form=form)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        password = request.form["password"]
        email = form.email.data
        number = form.number.data
        roles = form.roles.data

        existing_username = User.query.filter_by(username=username).first()
        if existing_username is None:
            newUser = User(username=username, password=password, email=email, number=number, roles=roles)
            db.session.add(newUser)
            db.session.commit()
            flash("User {} is created successfully".format(newUser.username), 'success')
        else:
            flash("A user is Already Exist with this username", 'danger')
    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __file__ == "__main__":
    app.run(debug=True)
