from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    date_of_visit = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/book', methods=['POST'])
def book_ticket():
    name = request.form['name']
    dob_str = request.form['date_of_birth']
    contact = request.form['contact_number']
    visit_date_str = request.form['date_of_visit']

    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        visit_date = datetime.strptime(visit_date_str, '%Y-%m-%d').date()
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD.", 400

    booking = Booking(
        name=name,
        date_of_birth=dob,
        contact_number=contact,
        date_of_visit=visit_date
    )
    db.session.add(booking)
    db.session.commit()

    
    qr_data = name
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}"

    return render_template('success.html', name=name, qr_url=qr_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/admin')
@login_required
def admin():
    bookings = Booking.query.all()
    return render_template('admin.html', bookings=bookings)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
