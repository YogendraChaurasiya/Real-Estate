from flask import Flask, render_template, request, redirect, url_for , session , flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, and_
import os
import secrets
import string
from sqlalchemy import func
from werkzeug.utils import secure_filename
from datetime import datetime
from datetime import time
from flask_mail import Mail, Message
import secrets
from flask import jsonify
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///real_estate.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yogendrachaurasiya30@gmail.com'  
app.config['MAIL_PASSWORD'] = 'oizzrkharzmoltmv'  

mail = Mail(app)
app.jinja_env.globals['getattr'] = getattr

# Define models
class Client(db.Model):
    id = db.Column(db.String(6), primary_key=True, default=lambda: ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    photo = db.Column(db.String(200))

class Owner(db.Model):
    id = db.Column(db.String(6), primary_key=True, default=lambda: ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    owner_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    photo = db.Column(db.String(200))

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(100), db.ForeignKey('owner.owner_name'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    property_name = db.Column(db.String(100), nullable=False)
    property_description = db.Column(db.Text, nullable=False)  
    property_size = db.Column(db.String(20), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image1 = db.Column(db.String(200))
    image2 = db.Column(db.String(200))
    image3 = db.Column(db.String(200))
    image4 = db.Column(db.String(200))
    
class Appointment(db.Model):
    id = db.Column(db.String(6), primary_key=True, default=lambda: ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    client_id = db.Column(db.String(6),nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(100), nullable=False)
    client_phone = db.Column(db.String(10), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    property_address = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)

class PropertyBooked(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    cid = db.Column(db.String(6), db.ForeignKey('client.id'), nullable=False)
    booked_date = db.Column(db.Date, nullable=False)


class Payment(db.Model):
    transaction_id = db.Column(db.String(10), primary_key=True, default=lambda: ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
    prop_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class SoldProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_name = db.Column(db.String(100), nullable=False)
    property_description = db.Column(db.Text, nullable=False)  
    property_size = db.Column(db.String(20), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    previous_owner = db.Column(db.String(100), nullable=False)
    current_owner = db.Column(db.String(100), nullable=False)
    image1 = db.Column(db.String(200))
    image2 = db.Column(db.String(200))
    image3 = db.Column(db.String(200))
    image4 = db.Column(db.String(200))
    
# Define routes
@app.route('/')
def index():
    # Get filter parameters from the query string
    property_type = request.args.get('property_type')
    property_size_min = request.args.get('property_size_min')
    property_size_max = request.args.get('property_size_max')
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')
    address = request.args.get('address')

    # Filter properties based on the parameters
    properties = Property.query

    if property_type:
        properties = properties.filter(Property.property_type == property_type)
    if property_size_min and property_size_max:
        properties = properties.filter(Property.property_size.between(property_size_min, property_size_max))
    if price_min and price_max:
        properties = properties.filter(Property.price.between(price_min, price_max))
    if address:
        properties = properties.filter(Property.address.ilike(f'%{address}%'))

    properties = properties.all()

    return render_template('index.html', properties=properties)

@app.route('/property/<int:id>')
def property_details(id):
    property = Property.query.get_or_404(id)
    return render_template('property_details.html', property=property, id=id, owner_name=property.owner_name)

@app.route('/properties')
def properties():
    # Fetch properties data as needed
    properties = Property.query.all()
    return render_template('properties.html', properties=properties)

@app.route('/list_property', methods=['POST'])
def list_property():
    if 'owner_id' not in session:
        return redirect(url_for('owner_login'))  
    
    if request.method == 'POST':
        owner_id = session['owner_id']
        owner = Owner.query.get(owner_id)
        if owner:
            property_name = request.form['property_name']
            property_description = request.form['property_description']
            address = request.form['address']
            property_size = request.form['property_size']
            property_type = request.form['property_type']
            price = request.form['price']

            # Initialize an empty list to store file paths
            property_images = []

            # Process file uploads
            for i in range(1, 5):
                file_key = 'property_image{}'.format(i)
                if file_key in request.files:
                    file = request.files[file_key]
                    if file.filename != '':
                        # Save the file to the uploads folder
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)
                        property_images.append(file_path)

            # Create a new property with the logged-in owner's owner_name
            new_property = Property(owner_name=owner.owner_name, property_name=property_name, 
                                    property_description=property_description, address=address, 
                                    property_size=property_size, property_type=property_type, price=price)
            db.session.add(new_property)
            db.session.commit()

            # Save property images to the database
            for i in range(len(property_images)):
                setattr(new_property, f"image{i+1}", property_images[i])
            db.session.commit()

            return redirect(url_for('index'))
        else:
            return "Owner not found!"
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_properties():
    query = request.form.get('query')
    # Search for properties that match the query
    properties = Property.query.filter(
        (Property.property_name.ilike(f'%{query}%')) |
        (Property.owner_name.ilike(f'%{query}%')) |
        (Property.address.ilike(f'%{query}%')) |
        (Property.property_type.ilike(f'%{query}%')) |
        (Property.property_size.ilike(f'%{query}%')) |
        (Property.price.ilike(f'%{query}%'))
    ).all()
    # Render a template with the search results
    return render_template('property_list.html', properties=properties)

# Add two different routes for client and owner signup
@app.route('/client_signup', methods=['GET', 'POST'])
def client_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        # Validate password
        if not (
            len(password) >= 8 and
            any(char.islower() for char in password) and
            any(char.isupper() for char in password) and
            any(char.isdigit() for char in password) and
            any(char in string.punctuation for char in password)
        ):
            flash("Password must be at least 8 characters long and contain at least 1 lowercase alphabet, 1 uppercase alphabet, 1 special character, and 1 numeric value.")
            return redirect(url_for('client_signup'))
        
        # Check if the email is already registered
        existing_user = Client.query.filter_by(email=email).first()
        if existing_user:
            # User already exists, redirect to login page
            return redirect(url_for('client_login'))
        else:
            # Process photo upload
            if 'photo' in request.files:
                photo = request.files['photo']
                photo_path = 'static/images/' + photo.filename
                photo.save(photo_path)
            else:
                photo_path = None
            
            # Create a new client user
            new_client = Client(name=name, email=email, phone=phone, password=password, photo=photo_path)
            db.session.add(new_client)
            db.session.commit()
            # Store user_id in session after successful signup
            session['user_id'] = new_client.id
            # Redirect to index page after successful signup
            return redirect(url_for('index'))
    return render_template('client_signup.html')

@app.route('/owner_signup', methods=['GET', 'POST'])
def owner_signup():
    if request.method == 'POST':
        owner_name = request.form['owner_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        # Validate password
        if not (
            len(password) >= 8 and
            any(char.islower() for char in password) and
            any(char.isupper() for char in password) and
            any(char.isdigit() for char in password) and
            any(char in string.punctuation for char in password)
        ):
            flash("Password must be at least 8 characters long and contain at least 1 lowercase alphabet, 1 uppercase alphabet, 1 special character, and 1 numeric value.")
            return redirect(url_for('owner_signup'))
        
        # Check if the email is already registered
        existing_owner = Owner.query.filter_by(email=email).first()
        if existing_owner:
            # Owner already exists, redirect to owner login page
            return redirect(url_for('owner_login'))
        else:
            new_owner = Owner(owner_name=owner_name, email=email, password=password, phone=phone)
            db.session.add(new_owner)
            db.session.commit()
            # Store owner_id in session after successful signup
            session['owner_id'] = new_owner.id
            # Redirect to index page after successful signup
            return redirect(url_for('sell_property'))
    return render_template('owner_signup.html')

# Add routes for client and owner login
@app.route('/client_login', methods=['GET', 'POST'])
def client_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if the client exists in the database
        client = Client.query.filter_by(email=email).first()
        if client:
            # Verify password
            if client.password == password:
                # Client exists and password matches, store user_id in session and redirect to index page
                session['user_id'] = client.id
                return redirect(url_for('index'))
            else:
                flash("Incorrect email or password.")
                return redirect(url_for('client_login'))
        else:
            # Client does not exist, redirect to client signup page
            return redirect(url_for('client_signup'))
    return render_template('client_login.html')

@app.route('/owner_login', methods=['GET', 'POST'])
def owner_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Check if the owner exists in the database
        owner = Owner.query.filter_by(email=email).first()
        if owner:
            # Verify password
            if owner.password == password:
                # Owner exists and password matches, store owner_id in session and redirect to index page
                session['owner_id'] = owner.id
                return redirect(url_for('sell_property'))
            else:
                flash("Incorrect email or password.")
                return redirect(url_for('owner_login'))
        else:
            # Owner does not exist, redirect to owner signup page
            return redirect(url_for('owner_signup'))
    return render_template('owner_login.html')

@app.route('/logout')
def logout():
    # Remove user_id from session if present
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/sell_property', methods=['GET', 'POST'])
def sell_property():
    if 'owner_id' not in session:
        return redirect(url_for('owner_login'))  # Redirect to login page if user is not logged in
    
    if request.method == 'POST':
        # Handle property listing form submission
        # Add property listing logic here
        return redirect(url_for('index'))
    return render_template('sell_property.html')

# Define a function to send email to client
def send_appointment_email(client_email, property_details):
    msg = Message('Appointment Scheduled', sender='yogendrachaurasiya30@gmail.com', recipients=[client_email])
    msg.body = f"Hello,\n\nYour property booking appointment for property located at {property_details['property_address']} has been scheduled.\n\nAppointment Date: {property_details['appointment_date']}\nAppointment Time: {property_details['appointment_time']}\n\nRegards,\nReal Estate Team"
    mail.send(msg)
    
# Define a function to send appointment notification email to property owner
def send_owner_appointment_email(owner_email, appointment_data):
    msg = Message('New Appointment Scheduled', sender='yogendrachaurasiya30@gmail.com', recipients=[owner_email])
    msg.body = f"Hello,\n\nA new appointment has been scheduled by {appointment_data['client_name']} for your property located at {appointment_data['property_address']}.\n\nAppointment Date: {appointment_data['appointment_date']}\nAppointment Time: {appointment_data['appointment_time']}\n\nClient Phone: {appointment_data['client_phone']}\n\nRegards,\nReal Estate Team"
    mail.send(msg)

# schedule_appointment route to send emails to both client and owner
@app.route('/schedule_appointment', methods=['POST'])
def schedule_appointment():
    if 'user_id' not in session:
        return redirect(url_for('client_login'))
    
    if request.method == 'POST':
        client_id = session['user_id']
        client = Client.query.get(client_id)
        if client:
            appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
            appointment_time_str = request.form.get('appointment_time')
            hour, minute = map(int, appointment_time_str.split(':'))
            appointment_time = time(hour, minute)
            property_id = request.args.get('id')  
            property_owner_name = request.args.get('owner_name')  # Fetch owner name from request
            
            # Fetch owner's email address based on the owner's name
            property_owner = Owner.query.filter_by(owner_name=property_owner_name).first()
            if property_owner:
                property_owner_email = property_owner.email
                
                property_address = Property.query.get(property_id).address
                
                # Check if there is an existing appointment for the client and property
                existing_appointment = Appointment.query.filter_by(client_id=client_id, property_id=property_id).first()
                if existing_appointment:
                    # Update the existing appointment
                    existing_appointment.appointment_date = appointment_date
                    existing_appointment.appointment_time = appointment_time
                else:
                    # Create a new appointment instance
                    new_appointment = Appointment(client_id=client_id, client_name=client.name, client_email=client.email,
                                                  client_phone=client.phone, appointment_date=appointment_date,
                                                  appointment_time=appointment_time, property_id=property_id,
                                                  property_address=property_address, owner_name=property_owner_name)
                    
                    # Add the appointment to the database
                    db.session.add(new_appointment)
                
                db.session.commit()
                
                # Send appointment confirmation email to the client
                client_email_data = {
                    'property_address': property_address,
                    'appointment_date': appointment_date,
                    'appointment_time': appointment_time
                }
                send_appointment_email(client.email, client_email_data)
                
                # Send appointment notification email to the property owner
                owner_email_data = {
                    'client_name': client.name,
                    'client_phone': client.phone,
                    'appointment_date': appointment_date,
                    'appointment_time': appointment_time,
                    'property_address': property_address
                }
                send_owner_appointment_email(property_owner_email, owner_email_data)
                
                # Redirect to property details page after scheduling/updating appointment
                return redirect(url_for('property_details', id=property_id))
            else:
                return "Property owner not found!"
        else:
            return "Client not found!"
    return render_template('property_details.html')


@app.route('/book_property', methods=['GET', 'POST'])
def book_property():
    if 'user_id' not in session:
        return redirect(url_for('client_login'))

    if request.method == 'POST':
        pid = request.args.get('pid')
        cid = session.get('user_id')  # Assuming the user is logged in and session contains user_id
        
        # Fetch the appointment date and time for the specific client and property ID combination
        appointment = Appointment.query.filter_by(client_id=cid, property_id=pid).first()
        
        if appointment:
            appointment_date = appointment.appointment_date
            appointment_time = appointment.appointment_time
            
            # Get the current datetime in IST timezone
            ist = pytz.timezone('Asia/Kolkata')
            current_datetime_ist = datetime.now(ist)
            
            # Check if appointment_datetime is not None and is on or after the scheduled appointment date and time
            if current_datetime_ist.date() >= appointment_date and current_datetime_ist.time() >= appointment_time:
                # The appointment time has passed, allow booking
                # Create a new PropertyBooked instance
                new_booking = PropertyBooked(pid=pid, cid=cid, booked_date=current_datetime_ist.date())
                db.session.add(new_booking)
                db.session.commit()
                
                print("Property booked successfully.")

                # Redirect to home page after booking
                return redirect(url_for('index'))
            else:
                # The appointment time is in the future, display an error message
                flash("You can only book the property after the scheduled appointment time.")
                return redirect(url_for('property_details', id=pid))  # Redirect to property details page
        else:
            flash("No appointment found for this property.")
            return redirect(url_for('property_details', id=pid))  # Redirect to property details page

    else:
        pid = request.args.get('pid')
        appointment_date = request.args.get('appointment_date')  # Get appointment date from query parameter
        return render_template('book_property.html', pid=pid, appointment_date=appointment_date)

@app.route('/down_payment', methods=['GET', 'POST'])
def down_payment():
    if 'user_id' not in session:
        return redirect(url_for('client_login'))

    if request.method == 'POST':
        client_id = session.get('user_id')
        prop_id = request.args.get('prop_id')

        # Check if the property is booked
        property_booked = PropertyBooked.query.filter_by(pid=prop_id, cid=client_id).first()
        if not property_booked:
            flash("Please book the property before making a down payment.")
            return redirect(url_for('property_details', id=prop_id))

        amount = 10000

        # Create a new Payment instance
        new_transaction = Payment(prop_id=prop_id, client_id=client_id, amount=amount)
        db.session.add(new_transaction)

        # Fetch property details
        property_to_sell = Property.query.get(prop_id)

        # Create a new SoldProperty instance with property details
        sold_property = SoldProperty(property_name=property_to_sell.property_name,
                                     property_description=property_to_sell.property_description,
                                     property_size=property_to_sell.property_size,
                                     property_type=property_to_sell.property_type,
                                     price=property_to_sell.price,
                                     address=property_to_sell.address,
                                     previous_owner=property_to_sell.owner_name,
                                     current_owner=Client.query.get(client_id).name,
                                     image1=property_to_sell.image1,
                                     image2=property_to_sell.image2,
                                     image3=property_to_sell.image3,
                                     image4=property_to_sell.image4)

        # Add sold property to the database
        db.session.add(sold_property)

        # Delete property from the Property table
        db.session.delete(property_to_sell)

        # Delete scheduled appointments for the property
        Appointment.query.filter_by(property_id=prop_id).delete()

        # Delete property bookings
        PropertyBooked.query.filter_by(pid=prop_id).delete()

        db.session.commit()

        return redirect(url_for('index'))

    # If the request method is GET, render the template
    # Check if the property is booked and flash the message accordingly
    client_id = session.get('user_id')
    prop_id = request.args.get('prop_id')
    property_booked = PropertyBooked.query.filter_by(pid=prop_id, cid=client_id).first()
    if not property_booked:
        flash("Please book the property before making a down payment.")
    return render_template('down_payment.html')

# Add route to render the client page
@app.route('/client_page')
def client_page():
    if 'user_id' not in session:
        return redirect(url_for('client_login'))

    # Fetch client's information
    client_id = session['user_id']
    client = Client.query.get(client_id)

    # Fetch client's photo path
    client_photo = client.photo if client.photo else None

    # Fetch client's scheduled appointments    
    # Join Appointment, Property, and PropertyBooked tables
    appointments = db.session.query(Appointment, Property, PropertyBooked).\
        join(Property, Appointment.property_id == Property.id).\
        outerjoin(PropertyBooked, and_(Appointment.property_id == PropertyBooked.pid, PropertyBooked.cid == client_id)).\
        filter(Appointment.client_id == client_id).all()
        
    # Fetch client's booked properties (pending down payment)
    booked_properties = PropertyBooked.query.filter_by(cid=client_id).all()

    # Fetch client's owned properties
    owned_properties = SoldProperty.query.filter_by(current_owner=client.name).all()

    # Render the client page template with the fetched data
    return render_template('client_page.html', client=client, client_photo=client_photo, appointments=appointments,
                           booked_properties=booked_properties, owned_properties=owned_properties)


@app.route('/owner_page')
def owner_page():
    if 'owner_id' not in session:
        return redirect(url_for('owner_login'))

    # Fetch owner's information
    owner_id = session['owner_id']
    owner = Owner.query.get(owner_id)

    # Fetch owner's properties
    owner_properties = Property.query.filter_by(owner_name=owner.owner_name).all()

    # Fetch scheduled appointments and bookings for owner's properties
    owner_appointments = {}
    booked_properties = {}

    for property in owner_properties:
        # Fetch scheduled appointments for the property
        appointments = Appointment.query.filter_by(property_id=property.id).all()
        owner_appointments[property] = appointments

        # Check if the property is booked
        bookings = PropertyBooked.query.filter_by(pid=property.id).all()
        booked_properties[property] = bookings

    # Fetch sold properties by owner
    sold_properties = SoldProperty.query.filter_by(previous_owner=owner.owner_name).all()

    # Pass the Client model to the template context
    return render_template('owner_page.html', owner=owner, owner_properties=owner_properties,
                           owner_appointments=owner_appointments, booked_properties=booked_properties,
                           sold_properties=sold_properties, Client=Client)



# @app.route('/admin')
# def admin_panel():
#     queries = [
#         ("Retrieve all properties along with their owners' details", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Owner.owner_name, Owner.email AS owner_email
#             FROM Property
#             JOIN Owner ON Property.owner_name = Owner.owner_name
#             """)
#         )),
#         ("Find the total number of properties listed by each owner:", db.session.execute(
#             text("""
#             SELECT Owner.owner_name, COUNT(Property.id) AS total_properties
#             FROM Owner
#             LEFT JOIN Property ON Owner.owner_name = Property.owner_name
#             GROUP BY Owner.owner_name
#             """)
#         )),
#         ("List properties along with the client's name who booked them, if booked", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Client.name AS client_name
#             FROM Property
#             LEFT JOIN Appointment ON Property.id = Appointment.property_id
#             LEFT JOIN Client ON Appointment.client_id = Client.id
#             """)
#         )),
#         ("Find the total number of appointments scheduled for each property", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, COUNT(Appointment.id) AS total_appointments
#             FROM Property
#             LEFT JOIN Appointment ON Property.id = Appointment.property_id
#             GROUP BY Property.id
#             """)
#         )),
#         ("Retrieve the properties booked by a specific client", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price
#             FROM Property
#             JOIN Appointment ON Property.id = Appointment.property_id
#             WHERE Appointment.client_id = 'H7ND6X'
#             """)
#         )),
#         ("List the clients who have made down payments, along with the property details", db.session.execute(
#             text("""
#             SELECT Client.name, Client.email, Property.address, Payment.amount, Payment.transaction_date
#             FROM Client
#             JOIN Payment ON Client.id = Payment.client_id
#             JOIN Property ON Payment.prop_id = Property.id
#             """)
#         )),
#         ("Find the average price of properties of each type", db.session.execute(
#             text("""
#             SELECT Property.property_type, AVG(Property.price) AS avg_price
#             FROM Property
#             GROUP BY Property.property_type
#             """)
#         )),
#         ("Retrieve the details of the latest transaction made for each property", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Payment.amount, Payment.transaction_date
#             FROM Property
#             JOIN Payment ON Property.id = Payment.prop_id
#             GROUP BY Property.id
#             ORDER BY Payment.transaction_date DESC
#             """)
#         )),
#         ("List the properties that have not been booked yet", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price
#             FROM Property
#             LEFT JOIN Appointment ON Property.id = Appointment.property_id
#             WHERE Appointment.id IS NULL
#             """)
#         )),
#         ("Find the properties booked by a specific client along with the appointment details", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Appointment.appointment_date, Appointment.appointment_time
#             FROM Property
#             JOIN Appointment ON Property.id = Appointment.property_id
#             WHERE Appointment.client_id = 'JPTCTQ'
#             """)
#         )),
#         ("Retrieve the properties listed by owners who have more than 3 properties listed", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Owner.owner_name
#             FROM Property
#             JOIN Owner ON Property.owner_name = Owner.owner_name
#             GROUP BY Owner.owner_name
#             HAVING COUNT(Property.id) > 3
#             """)
#         )),
#         ("Retrieve the properties listed by owners who have more than 3 properties listed and have made at least 1 down payment", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Owner.owner_name 
#             FROM Property
#             JOIN Owner ON Property.owner_name = Owner.owner_name
#             JOIN Payment ON Property.id = Payment.prop_id
#             GROUP BY Owner.owner_name
#             HAVING COUNT(Property.id) > 3
#             AND SUM(Payment.amount) > 0
#             """)
#         )),
#         ("Find the total amount earned from property transactions for each owner", db.session.execute(
#             text("""
#             SELECT Owner.owner_name, SUM(Payment.amount) AS total_earnings
#             FROM Owner
#             JOIN Property ON Owner.owner_name = Property.owner_name
#             JOIN Payment ON Property.id = Payment.prop_id
#             GROUP BY Owner.owner_name
#             """)
#         )),
#         ("List the clients who have scheduled appointments for properties owned by a specific owner", db.session.execute(
#             text("""
#             SELECT DISTINCT Client.name, Client.email
#             FROM Client
#             JOIN Appointment ON Client.id = Appointment.client_id
#             JOIN Property ON Appointment.property_id = Property.id
#             WHERE Property.owner_name = 'owner_name_value'
#             """)
#         )),
#         ("Retrieve the properties with their owners' details where the appointment date is in the future", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Owner.owner_name
#             FROM Property
#             JOIN Owner ON Property.owner_name = Owner.owner_name
#             JOIN Appointment ON Property.id = Appointment.property_id
#             WHERE Appointment.appointment_date > CURRENT_DATE
#             """)
#         )),
#         ("Find the top 5 clients who have made the highest total amount of transactions", db.session.execute(
#             text("""
#             SELECT Client.name, SUM(Payment.amount) AS total_transactions
#             FROM Client
#             JOIN Payment ON Client.id = Payment.client_id
#             GROUP BY Client.name
#             ORDER BY total_transactions DESC
#             LIMIT 5
#             """)
#         )),
#         ("List the properties booked by clients who have not made any transactions yet", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price
#             FROM Property
#             JOIN Appointment ON Property.id = Appointment.property_id
#             LEFT JOIN Payment ON Appointment.client_id = Payment.client_id
#             WHERE Payment.client_id IS NULL
#             """)
#         )),
#         ("Find the clients who have made transactions but haven't booked any appointments yet", db.session.execute(
#             text("""
#             SELECT Client.name, Client.email
#             FROM Client
#             JOIN Payment ON Client.id = Payment.client_id
#             LEFT JOIN Appointment ON Client.id = Appointment.client_id
#             WHERE Appointment.client_id IS NULL
#             """)
#         )),
#         ("Retrieve the properties listed by owners whose email domain is 'example.com'", db.session.execute(
#             text("""
#             SELECT Property.id, Property.address, Property.price, Owner.owner_name, Owner.email
#             FROM Property
#             JOIN Owner ON Property.owner_name = Owner.owner_name
#             WHERE Owner.email LIKE '%@gmail.com'
#             """)
#         )),
#         ("List the appointments scheduled for properties of a specific type along with their property details", db.session.execute(
#             text("""
#             SELECT Appointment.appointment_date, Appointment.appointment_time, Property.address, Property.price
#             FROM Appointment
#             JOIN Property ON Appointment.property_id = Property.id
#             WHERE Property.property_type = 'Villa'
#             """)
#         )),
#     ]
#     return render_template('admin.html', queries=queries)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)