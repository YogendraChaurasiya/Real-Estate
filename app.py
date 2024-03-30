from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail , Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///real_estate.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Add a secret key for session management

db = SQLAlchemy(app)
mail = Mail(app)

#Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # SMTP server address
app.config['MAIL_PORT'] = 465  # SMTP server port (587 for TLS)
app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'yogendrachaurasiya30@gmail.com'
app.config['MAIL_PASSWORD'] = 'rwmvymykfioubkig'
app.config['MAIL_DEFAULT_SENDER'] = 'yogendrachaurasiya30@gmail.com'# Default sender email address

# Define models
class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_no = db.Column(db.String(15), unique=True, nullable=False)

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

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    property = db.relationship('Property', backref=db.backref('appointments', lazy=True))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    client = db.relationship('Client', backref=db.backref('appointments', lazy=True))
    client_name = db.Column(db.String(100),nullable=False)





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
        name = request.form['Name']
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

@app.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        client_id = request.form['client_id']
        name = request.form['Name']
        email = request.form['email']
        phone_no = request.form['phone_no']

        new_client = Client(client_id=client_id, name=name, email=email, phone_no=phone_no)
        db.session.add(new_client)
        db.session.commit()
        # Redirect to index page after successful signup
        return redirect(url_for('index'))
    return render_template('client_signup.html')

@app.route('/client_login', methods=['GET','POST'])
def client_login():
    if request.method == 'POST':
        email = request.form['email']
        
        client = Client.query.filter_by(email=email).first()
        if client:
            # Client exists, store client_id in session and redirect to index page
            session['client_id'] = client.client_id
            return redirect(url_for('index'))
        else:
            # Client does not exist, redirect to signup page
            return redirect(url_for('client_signup'))
    return render_template('client_login.html')



@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        # Convert the date string to a Python date object
        appointment_date_str = request.form['appointment_date']
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()

        appointment_time_str = request.form['appointment_time']
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()

        # Retrieve form data
        client_id = request.form['client_id']
        property_id = request.form['property_id']
        owner_id = request.form['owner_id']
        client_name = request.form['client_name']
        
        # Check if owner_id exists in the User=owner table
        owner = User.query.get(owner_id)
        if owner:
            # Owner exists, fetch owner's email
            owner_email = owner.email

             # Print owner's email to verify
            print("Owner's email:", owner_email)

            # Create new appointment
            new_appointment = Appointment(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                client_id=client_id,
                property_id=property_id,
                owner_id=owner_id,
                client_name=client_name
            )

            db.session.add(new_appointment)
            db.session.commit()

             # Send email to the property owner
            send_email(owner_email, appointment_date, appointment_time, client_name)


            return redirect(url_for('appointment_booked'))
        else:
            # Owner ID does not exist, display error message
            return "No property owner with the specified ID exists."

    return render_template('appointment.html')

def send_email(email, appointment_date, appointment_time, client_name):
    try:
        msg = Message('New Appointment',sender='yogendrachaurasiya30@example.com', recipients=[email])
        msg.body = f'You have an appointment for property booking with {client_name} on {appointment_date} at {appointment_time}.'
        print("Email message:", msg)

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

@app.route('/appointment_booked')
def appointment_booked():
    return render_template('appointment_booked.html')



@app.route('/logout')
def logout():
    # Remove user_id from session if present
    session.pop('user_id', None)
    return redirect(url_for('index'))

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
