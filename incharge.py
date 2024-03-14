from flask import Blueprint, render_template, url_for, redirect, session, request
from flask_mail import Message
from email_utils import mail
# from config import *
from database import *

incharge_bp = Blueprint('incharge', __name__)

user = 'skillhivedumy@gmail.com'

@incharge_bp.route('/incharge_dashboard', methods = ['GET', 'POST'])
def incharge_dashboard():
    data = []
    internships = get_all_internships()
    for internship in internships:
        student = get_student(internship.prn).name
        data.append(
            {
                "name":student.split()[0].lower().capitalize() +' '+ student.split()[1].lower().capitalize() +' '+ student.split()[2].lower().capitalize(),
                "internship":internship,
                "is_pending": internship.status == "pending",
                "is_approved": internship.status == "Approved",
                "is_rejected": internship.status == "Rejected",
                "is_completed":internship.status == "completed"
            }
        )
    return render_template('incharge_dashboard.html', data = data)

@incharge_bp.route('/view_internship/<int:internship_id>', methods = ['GET', 'POST'])
def view_internship(internship_id):
    id = internship_id
    internship = get_internship(id)
    student = get_student(internship.prn)

    session['internship_id'] = id
    session['internship_prn'] = internship.prn

    is_acknowledged = internship.status == 'Approved' or internship.status == 'Rejected' or internship.status == 'completed' 
    has_offer_letter = internship.offer_letter == 'submitted'
    has_certificate = internship.certificate == 'submitted'
    has_report = internship.report == 'submitted'
    has_feedback = internship.feedback == 'submitted'

    reasons_to_reject = ['inadequate information provided', 'ethical concerns', 'proposed work hours overlap with the established college schedule']


    return render_template('internship_view.html', internship = internship, student = student, is_acknowledged = is_acknowledged, has_offer_letter = has_offer_letter, has_certificate = has_certificate, has_report = has_report, has_feedback = has_feedback, reasons_to_reject = reasons_to_reject)

@incharge_bp.route('/approve', methods = ['POST'])
def approve():
    if request.method == 'POST' and request.form['action'] == 'Approve':
        internship_id = session.get('internship_id')
        set_internship_status(internship_id, 'Approved')
        email = request.form.get('email')

        msg = Message('Internship Approval', sender=user, recipients=[get_student_using_internship_id(id=internship_id).email])
        msg.body = f'Congratulations!!\n Your internship request for {get_internship(internship_id).organization} has been approved.'
        mail.send(msg)
    
    return redirect(url_for('incharge.incharge_dashboard'))


@incharge_bp.route('/reject', methods=['POST'])
def reject():
    if request.method == 'POST' and request.form['action'] == 'Reject':
        internship_id = session.get('internship_id')
        set_internship_status(internship_id, 'Rejected')
        rejection_reason = request.form.get('choice')

        msg = Message('Internship Rejection', sender=user, recipients=[get_student_using_internship_id(id=internship_id).email])
        msg.body = f'Your internship request for {get_internship(internship_id).organization} has been rejected. Reason: {rejection_reason}'
        # Send the email
        mail.send(msg)

    return redirect(url_for('incharge.incharge_dashboard'))


@incharge_bp.route('/view_report')
def view_report():
    internship = get_internship(session.get('internship_id'))
    student = get_student(internship.prn)
    report = get_report(session.get('internship_id'))
    signature_url = url_for('static', filename=f"student/{internship.prn}/signature/signature.png")
    return render_template('report_view.html' , report = report, internship = internship, student = student)

@incharge_bp.route('/view_feedback')
def view_feedback():
    internship = get_internship(session.get('internship_id'))
    student = get_student(internship.prn)
    report = get_report(session.get('internship_id'))
    feedback = get_feedback(session.get('internship_id'))

    signature_url = url_for('static', filename=f'students/{internship.prn}/signature/signature.png')

    return render_template('feedback_view.html', feedback = feedback, internship = internship, student = student, report = report,signature = signature_url)

@incharge_bp.route('/view_certificate')
def view_certificate():
    file = f"students/{session.get('internship_prn')}/completion_certificate/{session.get('internship_id')}.pdf"
    return render_template('pdf.html',file = file, title = 'Completion Certificate')

@incharge_bp.route('/view_offer_letter')
def view_offer_letter():
    file = f"students/{session.get('internship_prn')}/offer_letter/{session.get('internship_id')}.pdf"
    return render_template('pdf.html',file = file , title = 'Offer Letter')

@incharge_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))