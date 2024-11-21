from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Set secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SECRET_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Where users are redirected if not logged in

# Define the User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

# Define the Cafe model for storing cafes
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    map_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=True)
    location = db.Column(db.String(250), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.Integer, nullable=True)
    coffee_price = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Cafe {self.name}>"

    def to_dict(self):
        return {
            'name': self.name,
            'map_url': self.map_url,
            'img_url': self.img_url,
            'location': self.location,
            'has_sockets': self.has_sockets,
            'has_toilet': self.has_toilet,
            'has_wifi': self.has_wifi,
            'can_take_calls': self.can_take_calls,
            'seats': self.seats,
            'coffee_price': self.coffee_price
        }

# Load user function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route: Display the list of cafes
@app.route('/')
def home():
    cafes = Cafe.query.all()
    if current_user.is_authenticated:
        # User is logged in, show form and cafe list
        return render_template('index.html', cafes=cafes, logged_in=True)
    else:
        # User is not logged in, show login and register links
        return render_template('index.html', cafes=cafes, logged_in=False)

# Register route: Handle user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user already exists
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Create and add the new user to the database
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route: Handle user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):  # Check hashed password
            login_user(user)
            flash('Login successful!')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

# Logout route: Handle user logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('You have logged out successfully.')
    return redirect(url_for('home'))

# API route to get all cafes (GET /api/cafes)
@app.route('/api/cafes', methods=['GET'])
def get_cafes():
    cafes = Cafe.query.all()
    return jsonify([cafe.to_dict() for cafe in cafes])

# API route to add a new cafe (POST /api/cafes)
@app.route('/api/cafes', methods=['POST'])
@login_required  # Only logged-in users can add cafes
def add_cafe():
    """Add a new cafe to the database."""
    data = request.json

    # Validate input
    required_fields = ["name", "map_url", "location", "has_sockets", "has_toilet", "has_wifi", "can_take_calls"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Add the new cafe
    new_cafe = Cafe(
        name=data['name'],
        map_url=data['map_url'],
        location=data['location'],
        has_sockets=data['has_sockets'],
        has_toilet=data['has_toilet'],
        has_wifi=data['has_wifi'],
        can_take_calls=data['can_take_calls'],
        seats=data.get('seats'),
        coffee_price=data.get('coffee_price')
    )
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(new_cafe.to_dict()), 201

# Route to delete a cafe
@app.route('/delete_cafe/<int:cafe_id>', methods=['POST'])
@login_required
def delete_cafe(cafe_id):
    # Check if the current user is the admin (user with id == 1)
    if current_user.id != 1:
        flash('You do not have permission to delete this cafe.')
        return redirect(url_for('home'))

    # Find the cafe to delete
    cafe = Cafe.query.get_or_404(cafe_id)

    # Delete the cafe from the database
    db.session.delete(cafe)
    db.session.commit()

    flash(f'Cafe {cafe.name} has been deleted successfully.')
    return redirect(url_for('home'))


# Run the application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
    app.run(debug=True)
