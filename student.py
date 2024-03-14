from flask import Blueprint, render_template, url_for, redirect, session, request
from database import *
from datetime import datetime
from flask_mail import Message
from email_utils import mail
from config import *
import os

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
def dashboard():
    data = []
    internships = get_internships_using_prn(session.get('prn'))
    for internship in internships:
        data.append({
            "status":internship.status =="Approved",
            "internship":internship,
            "is_completed":internship.end_date <=datetime.now().date(),
            "has_report":internship.report == 'submitted',
            "has_feedback":internship.feedback == 'submitted',
            "has_offer_letter":internship.offer_letter == 'submitted',
            "has_certificate":internship.certificate == 'submitted'
        })
    student_name = session.get('student')
    first_name = student_name.split()[1].lower().capitalize()


    return render_template('dashboard.html', student_name = first_name,data = data)


@student_bp.route('/add_new_internship', methods=['POST','GET'])
def add_new_internship():

    internships = get_all_internships()
    organizations=[]
    for internship in internships:
        if internship.organization not in organizations:
            organizations.append(internship.organization)
    print(organizations)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if request.method == 'POST':
        academic_year = request.form.get('academic_year')
        student_class = request.form.get('class')
        roll_no = request.form.get('roll_no')
        organization_name = request.form.get('organization_list') if request.form.get('organization_name') == '' else request.form.get('organization_name')
        internship_type = request.form.get('internship_type')
        duration = request.form.get('duration')
        mode = request.form.get('mode')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        work_time = f"{request.form.get('work_time_1')} - {request.form.get('work_time_2')}"

        selected_days = request.form.getlist('selected_days')
        days_string = ', '.join([str(day) for day in selected_days])


        add_internship(prn= session.get('prn'), organization= organization_name, year = academic_year, duration= duration, start_date= start_date, end_date=end_date, work_time= work_time, days=days_string, std_class=student_class, internship_type=internship_type, mode =mode)

        msg = Message(sender= 'skillhivedumy@gmail.com',recipients=['skillhivedumy@gmail.com'] )
        msg.body = f"New Internship has been requested by {get_student(session.get('prn')).name} "

        mail.send(msg)
        
        return redirect(url_for('student.dashboard'))
    return render_template('request_internship.html',days = days, organizations = organizations)

@student_bp.route('/upload_offer_letter/<int:internship_id>', methods=['GET', 'POST'])
def upload_file(internship_id):
    id = internship_id
    if request.method == 'POST':

        if 'file' not in request.files:
            return "No file part"
    
        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file:
            base_directory = f"static/students/{session.get('prn')}"

            offer_letter_folder_path = os.path.join(base_directory, 'offer_letter')
            if not os.path.exists(offer_letter_folder_path):
                os.makedirs(offer_letter_folder_path)
            new_filename = f'{id}.pdf'
            file.filename = new_filename
            file.save(f"{offer_letter_folder_path}/" + file.filename)
            update_internship_offer_letter_status(id)
            return redirect(url_for('student.dashboard'))
    
    return render_template('upload.html')

@student_bp.route('/certificate/<int:internship_id>', methods = ['GET', 'POST'])
def upload_certificate(internship_id):
    id = internship_id
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
    
        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file:
            base_directory = f"static/students/{session.get('prn')}"

            completion_certificate_folder_path = os.path.join(base_directory, 'completion_certificate')
            if not os.path.exists(completion_certificate_folder_path):
                os.makedirs(completion_certificate_folder_path)
            new_filename = f'{id}.pdf'
            file.filename = new_filename
            file.save(f"{completion_certificate_folder_path}/" + file.filename)
            update_internship_certificate_status(id)
        return redirect(url_for('student.dashboard'))

    return render_template('upload_certificate.html',id = id)

@student_bp.route('/report-form/<int:internship_id>', methods=['GET', 'POST'])
def report_form(internship_id):
    id = internship_id
    if request.method == 'POST':
        
        session['internship_id'] = id

        mobile = request.form['mobile']
        email = request.form['email']
        role = request.form['role']
        employer_email = request.form['employerEmail']
        supervisor_name = request.form['supervisorName']
        supervisor_email = request.form['supervisorEmail']
        supervisor_contact = request.form['supervisorContact']
        project_title = request.form['projectTitle']
        work_done = request.form['workDone']
        resources = request.form['resources']
        learnings = request.form['learnings']
        set_internship_report(id=id, std_mobile=mobile,std_email=email,roll_as_intern=role,emp_email=employer_email,supervisor_name=supervisor_name, supervisor_email=supervisor_email, supervisor_phone=supervisor_contact,project_title=project_title,project_desc=work_done, resources=resources, learnings=learnings)

        update_internship_report_status(id)
        
        return redirect(url_for('student.dashboard'))

    return render_template('reportInput.html',id = id)

@student_bp.route('/feedback-form/<int:internship_id>', methods=['GET','POST'])
def feedback_form(internship_id):
    id = internship_id
    if request.method == 'POST':
        
        session['internship_id'] = id

        q1 = request.form['q1']
        q2 = request.form['q2']
        q3 = request.form['q3']
        q4 = request.form['q4']
        q5 = request.form['q5']
        q6 = request.form['q6']
        q7 = request.form['q7']
        q8 = request.form['q8']

        set_internship_feedback(id=id, question_1=q1, question_2=q2, question_3=q3, question_4=q4, question_5=q5,question_6=q6,question_7=q7, question_8=q8)

        update_internship_feedback_status(id)
        set_internship_status(id, 'completed')
        
        return redirect(url_for('student.dashboard'))
    return render_template('feedbackInput.html', id =id)

@student_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))