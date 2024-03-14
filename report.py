from flask import Blueprint, render_template, url_for, redirect, session,request, jsonify
from collections import Counter, defaultdict
from datetime import datetime
from database import *
report_bp = Blueprint('report',__name__)

@report_bp.route('/reports', methods=['POST','GET'])
def report_filters():
    internships = get_all_internships()
    students = get_all_students()
    organizations = set(i.organization for i in internships)
    accademic_years = set(i.year for i in internships)

    start_year_filter = request.form.get('start-year')
    end_year_filter = request.form.get('end-year')
    std_class_filter = request.form.get('std-class')
    department_filter = request.form.get('department')
    organization_filter = request.form.get('company')
    accademic_year_filter = request.form.get('accademic-year')
    internship_type_filter = request.form.get('internship-type')



    return render_template('report_filter.html', organizations = organizations,  accademic_years = accademic_years)


@report_bp.route('/report-nav')
def report_nav():
    return render_template('report-nav.html')


def month_count_list_generator(dates, target_year=None):
    month_counts = {}

    for date_obj in dates:
        if date_obj.year == target_year:
            # Extract the month name
            month_name = date_obj.strftime("%B")
            
            # Update the count in the dictionary
            month_counts[month_name] = month_counts.get(month_name, 0) + 1

    # Convert the dictionary into a list of tuples
    return list(month_counts.items())

def gender_count_list_generator(ids):
    students_count = {"male":0, "female":0}
    for id in ids:
        if get_student_using_internship_id(id).gender =='male':
            students_count['male']+=1
        else:
            students_count['female']+=1
    return students_count

def house_count_list_generator(ids):
    house_count = {"inhouse":0,"outhouse":0}
    for id in ids:
        if get_internship(id).internship_type =='Out-house':
            house_count['outhouse']+=1
        else:
            house_count['inhouse']+=1
    return house_count

def mode_count_list_generator(ids):
    modes_counts = {'online':0, 'offline':0}
    for id in ids:
        if get_internship(id).mode =='online':
            modes_counts['online']+=1
        else:
            modes_counts['offline']+=1
    return modes_counts

def student_internship_count(prn):
    count = 0
    print(get_internships_using_prn())

    return count

@report_bp.route('/year-end-summary')
def year_end_summary_report():

    internships = get_all_internships()
    date_objects = [internship.start_date for internship in internships]
    target_year = 2023

    # Create a dictionary to store the count for each month
    month_count_list = month_count_list_generator(date_objects, target_year)

    gender = gender_count_list_generator([internship.internship_id for internship in internships])
    house = house_count_list_generator([internship.internship_id for internship in internships])
    mode = mode_count_list_generator([internship.internship_id for internship in internships])
    company = [ internship.organization for internship in internships]
    bar = Counter(company)
    
    bar_label =list(bar.keys())
    print(bar_label)
    bar_values = list(bar.values())

    labels = [row[0] for row in month_count_list]
    values = [row[1] for row in month_count_list]

    return render_template('year_end_summary.html',labels = labels, values = values, gender = gender, house = house,mode =mode, bar_label = bar_label, bar_values = bar_values)


@report_bp.route('/company_report',methods = ['GET','POST'])
def company_report():
    i = get_all_internships()
    companies = [internship.organization for internship in i]
    
    if request.method == 'POST':
        selected_company = request.form.get('company')
        print(selected_company)
        return redirect(url_for('report.company_display',company = selected_company))
        
    return render_template('company_report.html', companies=companies)

@report_bp.route('/company_display')
def company_display():
    company = request.args.get('company', type=str)
    internships= get_company(company=company)
    return render_template('company_display.html',company=company, internships =internships )


@report_bp.route('/accademic_year_report')
def accademic_year_report():
    internships = get_all_internships()
    fe_count = 0;
    se_count = 0;
    te_count = 0;
    be_count = 0;

    for internship in internships:
        if internship.std_class == "FE":
            fe_count +=1

        elif internship.std_class == "SE":
            se_count += 1

        elif internship.std_class == "TE":
            te_count += 1

        elif internship.std_class == "BE":
            be_count += 1

    departments_classes = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for internship in internships:
 
        if get_student(internship.prn).department == "Information Technology":
            if internship.std_class == "FE":
                departments_classes[0][0]+=1
            elif internship.std_class == "SE":
                departments_classes[0][1]+=1
            elif internship.std_class == "TE":
                departments_classes[0][2]+=1
            elif internship.std_class == "BE":
                departments_classes[0][3]+=1

        if get_student(internship.prn).department == "Computer Engineering":
            if internship.std_class == "FE":
                departments_classes[1][0]+=1
            elif internship.std_class == "SE":
                departments_classes[1][1]+=1
            elif internship.std_class == "TE":
                departments_classes[1][2]+=1
            elif internship.std_class == "BE":
                departments_classes[1][3]+=1

        if get_student(internship.prn).department == "Mechanical Engineering":
            if internship.std_class == "FE":
                departments_classes[2][0]+=1
            elif internship.std_class == "SE":
                departments_classes[2][1]+=1
            elif internship.std_class == "TE":
                departments_classes[2][2]+=1
            elif internship.std_class == "BE":
                departments_classes[2][3]+=1

        if get_student(internship.prn).department == "Artificial Inteligience and Data Science":
            if internship.std_class == "FE":
                departments_classes[3][0]+=1
            elif internship.std_class == "SE":
                departments_classes[3][1]+=1
            elif internship.std_class == "TE":
                departments_classes[3][2]+=1
            elif internship.std_class == "BE":
                departments_classes[3][3]+=1

        if get_student(internship.prn).department == "Electronics and Telecommunication":
            if internship.std_class == "FE":
                departments_classes[4][0]+=1
            elif internship.std_class == "SE":
                departments_classes[4][1]+=1
            elif internship.std_class == "TE":
                departments_classes[4][2]+=1
            elif internship.std_class == "BE":
                departments_classes[4][3]+=1
        
    print(departments_classes)
            

    labels = ['FE', "SE", "TE", "BE"]
    values = [fe_count, se_count, te_count, be_count]

    return render_template('accademic_year_report.html', labels = labels, values = values, departments_classes = departments_classes)

@report_bp.route('/inhouse_report')
def inhouse_report():
    internships = get_inhouse_outhouse('in-house')
    return render_template('house_report.html',internships = internships)

@report_bp.route('/outhouse_report')
def outhouse_report():
    internships = get_inhouse_outhouse('out-house')
    return render_template('house_report.html',internships = internships)





@report_bp.route('/students-report/',methods=['GET','POST'])
def students_report():

    if request.method == "POST":
        search_string = request.form.get('search')
        print(search_string)
        return redirect(url_for('report.search_results', q="Harsh"))
    
    students_data = get_all_students()
    students = []
    for student in students_data:
        if student.username != None:
            students.append(student)
    return render_template('students_report.html',students = students)

@report_bp.route('/student-view/<int:prn>/')
def student_view(prn):

    student_data = get_student(prn)
    internships = get_internships_using_prn(prn)

    student = {
        "name":student_data.name,
        "interned_for": set(i.organization for i in internships),
        "internship_count": len(internships),
        "internships": [i for i in internships],
        "data":student_data
    }
    return render_template('student_summary.html', student = student)

@report_bp.route('/search_results/<string:q>/')
def search_results(q):
    students = []
    students_data = get_all_students()
    for student in students_data:
        if student.department is not None:
            students.append(student)

    result = []
    for student in students:
        if q.lower() in student.name.lower():
            result.append(student)
            print(result)
    return render_template('search_results.html', result = result)