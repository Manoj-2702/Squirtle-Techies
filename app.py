from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from flask_mail import Mail, Message
from email_utils import initialize_mail, send_otp_email, verify_otp2
import os
from flask import jsonify
from twitter import main
import threading

app = Flask(__name__)
app.secret_key = "4"
app.config["MONGO_URI"] = "mongodb+srv://sana:sana1000@cluster0.eybaoqn.mongodb.net/dotslash?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# Initialize Flask-Mail
initialize_mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'meowtasim@gmail.com'
app.config['MAIL_PASSWORD'] = 'mdng lasz wrwn ebfn'

mail_sender = app.config['MAIL_USERNAME']
mail_password = app.config['MAIL_PASSWORD']

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        adm = mongo.db.admin.find_one({"email": email, "password": password})
        if adm:
            session['admin'] = True  # Set a session variable to indicate admin login
            return redirect(url_for('admin2'))
        else:
            error = 'Invalid email or password'
            return render_template('admin_login.html', error=error)

    return render_template('admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in the database
        user = mongo.db.users.find_one({"email": email, "password": password})

        if user:
            session['email'] = email  # Store the email in the session
            return redirect(url_for('user'))
        else:
            return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        otp = send_otp_email(email, mail_sender, mail_password)
        if otp:
            session['otp'] = otp
            session['user_data'] = {
                'name': name,
                'email': email,
                'phone': phone,
                'password': password
            }
            return redirect(url_for('verify_otp'))
        else:
            return render_template('register.html', error='Failed to send OTP email')

    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered_otp = request.form['otp']
        generated_otp = session.get('otp')

        if verify_otp2(entered_otp, generated_otp):
            user_data = session.get('user_data')
            # Insert the new user into the database
            mongo.db.users.insert_one({
                "name": user_data['name'],
                "email": user_data['email'],
                "phone": user_data['phone'],
                "password": user_data['password']
            })
            session.pop('otp', None)
            session.pop('user_data', None)
            return redirect(url_for('login'))
        else:
            return render_template('verify_otp.html', error='Invalid OTP')

    return render_template('verify_otp.html')

@app.route('/register_with_otp', methods=['POST'])
def register_with_otp():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']
    entered_otp = request.form['otp']
    generated_otp = session.get('otp')

    if verify_otp(entered_otp, generated_otp):
        # Insert the new user into the database
        mongo.db.users.insert_one({"name": name, "email": email, "phone": phone, "password": password})
        return redirect(url_for('login'))
    else:
        return render_template('register.html', error='Invalid OTP')

@app.route('/submit_data', methods=['POST'])
def submit_data():
    if 'email' in session:
        email = session['email']
        user_data = {
            "email": email,
            "location": request.form['location'],
            "category": request.form['category'],
            "description": request.form['description'],
            "latitude":request.form['latitude'],
            "longitude":request.form['longitude']
            # Add any other data fields here
        }
        mongo.db.users.update_one(
            {"email": email},
            {"$set": user_data},
            upsert=True
        )
        return redirect(url_for('user'))
    else:
        return redirect(url_for('login'))

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')
    if email:
        otp = send_otp_email(email, mail_sender, mail_password)
        if otp:
            session['otp'] = otp
            return {'success': True}
        else:
            return {'success': False, 'error': 'Failed to send OTP email'}
    else:
        return {'success': False, 'error': 'Email is required'}

@app.route('/admin2')
def admin2():
    if 'admin' in session: 
         # Check if the user is logged in as an admin
                # Define a function to run the main function in a separate thread
        def run_main():
            main()  # Assuming your main function is named 'main'

        # Start a new thread to run the main function
        thread = threading.Thread(target=run_main)
        thread.start()

        return render_template('admin.html')
    else:
        return redirect(url_for('admin_login'))
    
@app.route('/user')
def user():
    if 'email' in session:  # Change 'username' to 'email'
        email=session['email']
        user_data=mongo.db.users.find_one( {"email": email } )
        return render_template('user.html',user_data=user_data)
    else:
        return redirect(url_for('login'))

@app.route('/get_locations', methods=['GET'])
def get_locations():
    locations = []
    for user in mongo.db.users.find({}, {"latitude": 1, "longitude": 1, "category": 1, "location": 1, "description": 1}):
        if "latitude" in user and "longitude" in user:
            locations.append({
                "latitude": user["latitude"],
                "longitude": user["longitude"],
                "category": user["category"],
                "location": user["location"],
                "description": user["description"]
            })
    return jsonify(locations)


if __name__ == '__main__':
    app.run(debug=True)