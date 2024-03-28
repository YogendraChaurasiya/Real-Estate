from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///real_estate.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Add a secret key for session management
db = SQLAlchemy(app)

# Define models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    photo = db.Column(db.String(2000))
    phone = db.Column(db.String(15), unique=True, nullable=False)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100), nullable=False)
    property_images = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    property_size = db.Column(db.String(20), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Define routes
@app.route('/')
def index():
    properties = Property.query.all()
    return render_template('index.html', properties=properties)

@app.route('/property/<int:id>')
def property_details(id):
    property = Property.query.get_or_404(id)
    return render_template('property_details.html', property=property)

# Update the 'list_property' route
@app.route('/list_property', methods=['POST'])
def list_property():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
    
    if request.method == 'POST':
        owner_name = request.form['owner_name']
        address = request.form['address']
        property_size = request.form['property_size']
        property_type = request.form['property_type']
        price = request.form['price']

        # Initialize an empty list to store file paths
        property_images = []

        # Process file uploads
        for i in range(1, 9):
            file_key = 'property_images{}'.format(i)
            if file_key in request.files:
                file = request.files[file_key]
                if file.filename != '':
                    # Save the file to the uploads folder
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    property_images.append(file_path)

        # Concatenate file paths into a single string with a delimiter
        property_images_str = '|'.join(property_images)

        # Create a new property with the concatenated image paths
        new_property = Property(owner_name=owner_name, property_images=property_images_str, address=address, 
                                property_size=property_size, property_type=property_type, price=price)
        db.session.add(new_property)
        db.session.commit()

        return redirect(url_for('index'))

    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # User exists, store user_id in session and redirect to index page
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            # User does not exist, redirect to signup page
            return redirect(url_for('signup'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        # Check if the email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # User already exists, redirect to login page
            return redirect(url_for('login'))
        else:
            # Process photo upload
            if 'photo' in request.files:
                photo = request.files['photo']
                photo_path = 'static/images/' + photo.filename
                photo.save(photo_path)
            else:
                photo_path = None
            
            # Create a new user
            new_user = User(name=name, email=email, phone=phone, photo=photo_path)
            db.session.add(new_user)
            db.session.commit()
            # Store user_id in session after successful signup
            session['user_id'] = new_user.id
            # Redirect to index page after successful signup
            return redirect(url_for('index'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Remove user_id from session if present
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/sell_property', methods=['GET', 'POST'])
def sell_property():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
    
    if request.method == 'POST':
        # Handle property listing form submission
        # Add property listing logic here
        return redirect(url_for('index'))
    return render_template('sell_property.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
