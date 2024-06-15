from flask import Flask, render_template, request, jsonify, session, redirect ,Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import base64
from datetime import datetime, date, time, timedelta
import random
import requests
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__,static_folder='static', static_url_path='/static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fadalytrac.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'your_secret_key_here'
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "*"}})


class Employees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    workplace = db.Column(db.String(100))
    position = db.Column(db.String(100))
    user_id = db.Column(db.Integer)
    # Personal Information
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    marital_status = db.Column(db.String(50))
    nationality = db.Column(db.String(100))
    # Contact Information
    address = db.Column(db.String(255))
    mobile_phone = db.Column(db.String(20))
    home_phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    # Work Experience
    current_job_title = db.Column(db.String(100))
    start_date_current_job = db.Column(db.Date)
    duration_current_job = db.Column(db.String(50))
    previous_job_titles = db.Column(db.String(255))
    previous_companies = db.Column(db.String(255))
    duration_previous_job = db.Column(db.String(255))
    # Skills and Languages
    autocad_proficiency = db.Column(db.String(5))
    civil_3d_proficiency = db.Column(db.String(5))
    total_station_proficiency = db.Column(db.String(5))
    gps_proficiency = db.Column(db.String(5))
    _3d_scanner_proficiency = db.Column(db.String(5))
    data_transfer_software_proficiency = db.Column(db.String(5))
    languages = db.Column(db.String(255))
    technical_skills = db.Column(db.String(255))
    personal_skills = db.Column(db.String(255))
    # Additional Information
    highest_education_degree = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    educational_institution = db.Column(db.String(255))
    graduation_year = db.Column(db.Integer)
    additional_info = db.Column(db.Text)
    # Financial Information
    personal_bank_account_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(100))
    personal_wallet_number = db.Column(db.String(50))
    tax_number = db.Column(db.String(50))
    social_security_number = db.Column(db.String(50))
    # Emergency Contact
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))



class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    mes = db.Column(db.String(1000))
    name = db.Column(db.String(100), nullable=False)
    st_id = db.Column(db.Integer)
    stat = db.Column(db.Integer)

class AdminComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    Day_id = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(1000))

class TimeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    latitude_in = db.Column(db.Float, nullable=False)
    longitude_in = db.Column(db.Float)
    latitude_out = db.Column(db.Float)
    longitude_out = db.Column(db.Float)
    date = db.Column(db.Date, default=func.current_date())
    month = db.Column(db.Integer, default=func.extract('month', func.current_date()))
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    image_in = db.Column(db.LargeBinary)
    image_out = db.Column(db.LargeBinary)
    browser_number = db.Column(db.LargeBinary)
    comment_in = db.Column(db.String(1000))
    comment_out = db.Column(db.String(1000))
    Tlocation_in = db.Column(db.String(1000))
    Tlocation_out = db.Column(db.String(1000))
    attendance_in = db.Column(db.String(10))
    attendance_out = db.Column(db.String(10))

@app.before_request
def before_request():
    if 'browser_number' not in session:
        session['browser_number'] = random.randint(100000, 1000000)
# make a bluebrint for the emplowers
employees = Blueprint('employees', __name__)
admin = Blueprint('admin', __name__)
# ----------------- employees -----------------
@employees.route('/')
def home():
    return render_template('user/index.html')
@employees.route('/capture', methods=['POST'])
def capture():
        user_id = request.form.get('id')
        comment = request.form.get('comment1')
        name = Employees.query.filter_by(user_id=user_id).first()
        attendance = request.form.get('attendance')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        photo_data = request.files['photoData']
        browser_number = session['browser_number']
        comment = request.form.get('comment')
        image_data = photo_data.read()

        if attendance == "Entrance":
            today = date.today()
            result = TimeRecord.query.filter_by(user_id=user_id, date=today, attendance_in="Entrance").first()
            if result:
                return render_template('user/index.html', mes='You have pre-registered')
            else:
                browser_number_encoded = base64.b64encode(str(browser_number).encode('utf-8'))
                response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Riyadh')
                data = response.json()
                current_time = data['datetime']
                formatted_time = datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%S.%f%z').time()
                location = TimeRecord(
                    name=name.name,
                    user_id=int(user_id),
                    latitude_in=latitude,
                    longitude_in=longitude,
                    image_in=image_data,
                    Tlocation_in="Null",
                    browser_number=browser_number_encoded,
                    time_in=formatted_time,
                    comment_in=comment,
                    attendance_in="Entrance"
                )
                db.session.add(location)
                db.session.commit()
                # store the name and id in the session for 90 days and check if they are already in session
                if 'name' not in session or 'user_id' not in session:
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(days=90)
                    session['name'] = name.name
                    session['user_id'] = user_id
                if location.time_in > time(hour=9, minute=30, second=0):
                    new_notif = Notification(user_id=user_id, name=name.name, st_id=location.id, mes='Late attendance', stat=0)
                    db.session.add(new_notif)
                    db.session.commit()

                return redirect(f'/saveed/{location.id}/in')

        elif attendance == "Exit":
            today = date.today()
            result = TimeRecord.query.filter_by(user_id=user_id, date=today, attendance_in="Entrance").first()
            if result:
                result.attendance_out = "Exit"
                result.latitude_out = latitude
                result.longitude_out = longitude
                result.image_out = image_data
                result.comment_out = comment
                response = requests.get('http://worldtimeapi.org/api/timezone/Asia/Riyadh')
                data = response.json()
                current_time = data['datetime']
                formatted_time = datetime.strptime(current_time, '%Y-%m-%dT%H:%M:%S.%f%z').time()
                result.time_out = formatted_time
                db.session.commit()

                if result.time_out < time(hour=14, minute=30, second=0):
                    new_notif = Notification(user_id=user_id, name=name.name, st_id=result.id, mes='Early departure from work', stat=0)
                    db.session.add(new_notif)
                    db.session.commit()

                return redirect(f'/saveed/{result.id}/out')
            else:
                return render_template('user/index.html', mes='You have not registered your entrance yet!')
        else:
            return render_template('user/index.html', mes="Invalid attendance type!")


@employees.route('/saveed/<int:id>/<type>')
def saveed(id, type):
        # Retrieve the location record by ID
        location = TimeRecord.query.filter_by(id=id).first()
        # Retrieve the corresponding employee
        employee = Employees.query.filter_by(user_id=location.user_id).first()

        # Determine which attendance attribute to use based on the type parameter
        if type == 'in':
            attendance = location.attendance_in
            time_record = location.time_in
            comment_record = location.comment_in
            image_record = location.image_in
        elif type == 'out':
            attendance = location.attendance_out
            time_record = location.time_out
            comment_record = location.comment_out
            image_record = location.image_out
        else:
            return render_template('user/saveed.html', mes="Invalid type parameter!")

        context = {
            'name': employee.name,
            'attendance': attendance,
            'time': time_record,
            'comment': comment_record,
            'image': base64.b64encode(image_record).decode('utf-8') if image_record else None
        }
        return render_template('user/saveed.html', **context)
@employees.route('/delete-session')
def delete_session():
    session.pop('name', None)
    session.pop('user_id', None)
    return redirect('/')
# ----------------- admin -----------------
@admin.route('/dashboard')
def admin_home():
    emplowersCount = Employees.query.count()
    timeRecordsCount = TimeRecord.query.count()
    notificationsCount = Notification.query.count()
    adminCommentsCount = AdminComment.query.count()
    last50Attend = TimeRecord.query.order_by(TimeRecord.id.desc()).limit(50).all()
    
    context = {
        'emplowersCount': emplowersCount,
        'timeRecordsCount': timeRecordsCount,
        'notificationsCount': notificationsCount,
        'adminCommentsCount': adminCommentsCount,
        'last50Attend': last50Attend
    }
    return render_template('admin/index.html', **context)

# /admin/employees route
@admin.route('/employees')
def admin_employees():
    employees = Employees.query.all()
    return render_template('admin/employees.html', employees=employees)
@admin.route('/add_employees', methods=['GET', 'POST'])
def add_employees():
        if request.method == 'POST':
            name = request.form.get('name')
            workplace = request.form.get('workplace')
            position = request.form.get('position')
            user_id = request.form.get('user_id')
            date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            gender = request.form.get('gender')
            marital_status = request.form.get('marital_status')
            nationality = request.form.get('nationality')
            address = request.form.get('address')
            mobile_phone = request.form.get('mobile_phone')
            home_phone = request.form.get('home_phone')
            email = request.form.get('email')
            current_job_title = request.form.get('current_job_title')
            start_date_current_job = datetime.strptime(request.form.get('start_date_current_job'), '%Y-%m-%d').date()
            duration_current_job = request.form.get('duration_current_job')
            previous_job_titles = request.form.get('previous_job_titles')
            previous_companies = request.form.get('previous_companies')
            duration_previous_job = request.form.get('duration_previous_job')
            autocad_proficiency = request.form.get('autocad_proficiency')
            civil_3d_proficiency = request.form.get('civil_3d_proficiency')
            total_station_proficiency = request.form.get('total_station_proficiency')
            gps_proficiency = request.form.get('gps_proficiency')
            _3d_scanner_proficiency = request.form.get('_3d_scanner_proficiency')
            data_transfer_software_proficiency = request.form.get('data_transfer_software_proficiency')
            languages = request.form.get('languages')
            technical_skills = request.form.get('technical_skills')
            personal_skills = request.form.get('personal_skills')
            highest_education_degree = request.form.get('highest_education_degree')
            field_of_study = request.form.get('field_of_study')
            educational_institution = request.form.get('educational_institution')
            graduation_year = datetime.strptime(request.form.get('graduation_year'), '%Y-%m-%d').date()
            additional_info = request.form.get('additional_info')
            personal_bank_account_number = request.form.get('personal_bank_account_number')
            bank_name = request.form.get('bank_name')
            personal_wallet_number = request.form.get('personal_wallet_number')
            tax_number = request.form.get('tax_number')
            social_security_number = request.form.get('social_security_number')
            emergency_contact_name = request.form.get('emergency_contact_name')
            emergency_contact_phone = request.form.get('emergency_contact_phone')

            employee = Employees(
                name=name,
                workplace=workplace,
                position=position,
                user_id=user_id,
                date_of_birth=date_of_birth,
                gender=gender,
                marital_status=marital_status,
                nationality=nationality,
                address=address,
                mobile_phone=mobile_phone,
                home_phone=home_phone,
                email=email,
                current_job_title=current_job_title,
                start_date_current_job=start_date_current_job,
                duration_current_job=duration_current_job,
                previous_job_titles=previous_job_titles,
                previous_companies=previous_companies,
                duration_previous_job=duration_previous_job,
                autocad_proficiency=autocad_proficiency,
                civil_3d_proficiency=civil_3d_proficiency,
                total_station_proficiency=total_station_proficiency,
                gps_proficiency=gps_proficiency,
                _3d_scanner_proficiency=_3d_scanner_proficiency,
                data_transfer_software_proficiency=data_transfer_software_proficiency,
                languages=languages,
                technical_skills=technical_skills,
                personal_skills=personal_skills,
                highest_education_degree=highest_education_degree,
                field_of_study=field_of_study,
                educational_institution=educational_institution,
                graduation_year=graduation_year,
                additional_info=additional_info,
                personal_bank_account_number=personal_bank_account_number,
                bank_name=bank_name,
                personal_wallet_number=personal_wallet_number,
                tax_number=tax_number,
                social_security_number=social_security_number,
                emergency_contact_name=emergency_contact_name,
                emergency_contact_phone=emergency_contact_phone
            )

            db.session.add(employee)
            db.session.commit()

            return redirect('/')

        return render_template('admin/add_employees.html')
# /admin/view_record/<int:id> route
@admin.route('/view_record/<int:id>')
def view_record(id):
    time_records = TimeRecord.query.filter_by(id=id).first()
    employee = Employees.query.filter_by(user_id=time_records.user_id).first()

    context = {
        'employee': employee,
        'record': time_records,
    }
    return render_template('admin/view_record.html', **context)
# /admin/displayrecordimg/<int:id>/<type> route
@admin.route('/displayrecordimg/<int:id>/<type>')
def displayrecordimg(id, type):
    location = TimeRecord.query.filter_by(id=id).first()
    if type == 'in':
        image = location.image_in
    elif type == 'out':
        image = location.image_out
    else:
        return render_template('admin/displayrecordimg.html', mes='Invalid type parameter!')

    return render_template('admin/displayrecordimg.html', image=base64.b64encode(image).decode('utf-8'))
# export the blueprint
app.register_blueprint(employees, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
