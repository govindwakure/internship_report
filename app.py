from flask import Flask, redirect, url_for, request, render_template, session, jsonify
from datetime import datetime
import os
from database import *
from email_utils import mail
from incharge import incharge_bp
from student import student_bp
from report import report_bp
# from config import *

app = Flask(__name__)


#socketio = SocketIO(app)
app.secret_key = 'SECRET_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://default:CSKFzMAYT8o5@ep-raspy-mouse-a4kjdb28.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'skillhivedumy@gmail.com'
app.config['MAIL_PASSWORD'] = 'fwgrugbsykerdtaw'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail.init_app(app)

app.register_blueprint(incharge_bp)
app.register_blueprint(student_bp)
app.register_blueprint(report_bp)

init_app(app)
@app.route('/', methods=['GET', 'POST'])
def index():
    selected_button = request.form.get('redirect_button')

    if selected_button == 'register':
        return redirect(url_for('register'))
    elif selected_button == 'login':
        return redirect(url_for('login'))
    elif selected_button == 'login_incharge':
        return redirect(url_for('incharge_login'))
    return render_template('login.html')
   
@app.route('/incharge_login', methods=['GET','POST'])
def incharge_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_admin(username, password):
            return redirect(url_for('incharge.incharge_dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('incharge_login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        prn_number = request.form['prn_number']
        prn_id = Student.query.get(prn_number)
        if not check_registration(prn_number):
            if prn_id:
                session['prn']= prn_number
                session['student']= get_student(prn_number).name
                folder_name = session.get('prn')
                base_directory = "static/students"

                student_folder_path = os.path.join(base_directory, folder_name)
                os.makedirs(student_folder_path)
                print('folder created')
                
                return redirect(url_for('set_password'))
            else:
                return "you are not registered yet"
        else:
            return "you already have an account go to login"
    return render_template('register.html',name = session.get('student'))

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(username)
        prn = get_student_using_username(username).prn
        session['prn'] = prn
        session['student']= get_student(prn).name
        if authenticate_student(prn, password):
            return redirect(url_for('student.dashboard'))
        else:
            return 'Invalid Credentials'
    return render_template('login.html')

@app.route('/set_password',methods = ['POST','GET'])
def set_password():
    

    if request.method =='POST':

        if 'file' not in request.files:
            return "No file part"
    
        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file:
            file.filename= 'signature.png'
            base_directory = f"static/students/{session.get('prn')}"

            signature_folder_path = os.path.join(base_directory, 'signature')
            os.makedirs(signature_folder_path)
            file.save(f"{signature_folder_path}/" + file.filename)

        password = request.form.get('password')
        username = request.form.get('username')
        department = request.form.get('department')
        gender = request.form.get('gender')
        email = request.form.get('email')

        update_password(password, session.get('prn'))
        set_student_username(session.get('prn'), username)
        set_student_department(session.get('prn'), department)
        set_student_email(session.get('prn'), email)
        set_student_gender(session.get('prn'), gender)

        return redirect(url_for('student.dashboard'))
    return render_template('set_password.html',name = session.get('student'))



if __name__ == '__main__':
    app.run(debug=True)
    
