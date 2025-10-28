import os
import re
import csv
from flask import Flask, render_template, request, redirect, abort, flash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, EmailField, TelField, SelectField, DateField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, Regexp
from werkzeug.utils import secure_filename
from datetime import datetime

# Configuration
app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024   # 10MB file limit

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

csrf = CSRFProtect(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class MyForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3,32), Regexp('^[A-Za-z0-9_]+$')])
    password = PasswordField('Password', validators=[DataRequired(), Length(5,32)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(5,64)])
    number = TelField('Mobile Number', validators=[DataRequired(), Regexp('^[0-9]{10,15}$')])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    check = BooleanField('I agree', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    file = FileField('File', validators=[DataRequired()])
    subject = StringField('Subject', validators=[Length(0,50)])
    message = StringField('Message', validators=[Length(0,300)])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = MyForm()
    if form.validate_on_submit():
        # Honeypot implementation: add hidden field in template and abort if filled
        if request.form.get('website') or request.form.get('fax'):
            abort(400)
        file = request.files.get('file')
        if not file or not allowed_file(file.filename):
            flash('Invalid file type!')
            return redirect(request.url)
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Store form data in CSV (never plain password!)
        with open('submissions.csv', 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([datetime.now().isoformat(), form.username.data,
                             "[password omitted]", form.email.data, form.number.data,
                             form.gender.data, form.date.data, filename, form.subject.data, form.message.data])
        flash('Submission successful!')
        return redirect('/')
    return render_template('form.html', form=form)

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
