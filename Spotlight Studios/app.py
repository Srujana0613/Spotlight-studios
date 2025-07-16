from flask import Flask, render_template, request, redirect, jsonify
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Pre-existing admin credentials
ADMIN_CREDENTIALS = {"username": "admin", "password": "1234"}

# Load existing students data if available
try:
    with open("students.json", "r") as file:
        students_data = json.load(file)
except FileNotFoundError:
    students_data = []

# Types data structure for genre and specific types
types = {
    "dancing": {
        "western": ["Salsa", "Hip Hop", "Belly Dance"],
        "classical": ["Kuchipudi", "Kathak", "Bharatanatyam"],
        "folk": ["Bhangra", "Garba", "Ghoomar"]
    },
    "singing": {
        "western": ["Pop", "Rock", "Opera"],
        "classical": ["Carnatic", "Bass", "Lyric"],
        "folk": ["Folk Rock", "Indie Folk", "Nordic Folk"]
    }
}

# Route for main page with Admin or Student selection
@app.route('/')
def index():
    return render_template('index.html')

# Admin login page
@app.route('/admin', methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            return redirect('/registered_students')
        else:
            return "Invalid credentials", 403
    return render_template("admin.html")

# Route to display registered students in a new page
@app.route('/registered_students')
def registered_students():
    return render_template('registered_students.html', students=students_data)


# Student domain selection page
@app.route('/student')
def student_select():
    return render_template('student_select.html')

# Dance categories page
@app.route('/dance')
def dance():
    return render_template('dance.html')

# Singing categories page
@app.route('/singing')
def singing():
    return render_template('singing.html')

# Registration form page
@app.route('/register')
def register():
    return render_template('register.html')

# Handle student registration
@app.route('/submit_registration', methods=["POST"])
def submit_registration():
    data = request.form.to_dict()

    # Backend validation
    # Validate email to ensure it is a @gmail.com address
    email_regex = r'^[\w\.-]+@gmail\.com$'
    if not re.match(email_regex, data.get('email', '')):
        return "Invalid email format. Only @gmail.com addresses are allowed.", 400

    # Validate mobile number to ensure it contains exactly 10 digits
    mobile = data.get('mobile', '')
    if not mobile.isdigit() or len(mobile) != 10:
        return "Invalid mobile number. Must contain exactly 10 digits.", 400

    # Append dropdown selections to registration data
    dropdown_data = {
        "activity": data.get("activity"),
        "genre": data.get("genre"),
        "specificType": data.get("specificType")
    }
    data.update(dropdown_data)  # Add dropdown selections to the data

    # If all validations pass, proceed to save registration data
    students_data.append(data)
    with open("students.json", "w") as file:
        json.dump(students_data, file, indent=4)

    # Send thank-you email with all registration details
    send_email(data)

    return "Thank you for registration! Check your email for details."

# Function to send email using SMTP
def send_email(data):
    from_email = "adminmailhere@gmail.com"
    from_password = "16 digit password here"
    to_email = data['email']
    name = data['name']

    subject = "Spotlight Studios Registration info"
    body = f"""
    Dear {name},

    Thank you for registering for the class. Here are your registration details:

    Name: {data.get('name')}
    Age: {data.get('age')}
    Mobile: {data.get('mobile')}
    Email: {data.get('email')}
    Experience: {data.get('experience')}
    Address: {data.get('address')}
    Health Issues: {data.get('health')}
    Activity: {data.get('activity')}
    Genre: {data.get('genre')}
    Specific Type: {data.get('specificType')}

    We are excited to have you with us!

    Best regards,
    Spotlight Studios.
    """

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Setup SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())

# Route to get genres based on the selected activity
@app.route('/get_genres', methods=['GET'])
def get_genres():
    activity = request.args.get('activity')
    genres = list(types.get(activity, {}).keys()) if activity in types else []
    return jsonify(genres=genres)

# Route to get specific types based on the selected activity and genre
@app.route('/get_types', methods=['GET'])
def get_types():
    activity = request.args.get('activity')
    genre = request.args.get('genre')
    specific_types = types.get(activity, {}).get(genre, []) if activity and genre else []
    return jsonify(types=specific_types)

if __name__ == '__main__':
    app.run(debug=True)
