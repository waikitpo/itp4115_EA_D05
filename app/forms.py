from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, SearchField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User, Company


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use different email address.")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField("Request Password Reset")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")

    def __init__(self, original_username,  *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError("Please use different username.")


class PostForm(FlaskForm):
    post = TextAreaField("Say Somethong", validators=[
                         DataRequired(), Length(min=0, max=140)])
    submit = SubmitField("Submit")


class CompanyLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class CompanyRegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    name = StringField("Company Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    def validate_company_username(self, username):
        company = Company.query.filter_by(username=username.data).first()
        if company is not None:
            raise ValidationError("Please use different username.")

    def validate_company_email(self, email):
        company = Company.query.filter_by(email=email.data).first()
        if company is not None:
            raise ValidationError("Please use different email address.")
        
    def validate_company_name(self, name):
        company = Company.query.filter_by(name=name.data).first()
        if company is not None:
            raise ValidationError("Please use different Company Name.")
        
class JobSearchForm(FlaskForm):
    search = SearchField("Job title, keyword or company")
    job_location = SelectField('Location', choices=[('All', 'All Locations'), ('1', 'Hong Kong Island'), ('2', 'Kowloon Peninsula'), ('3', 'New Territory'), ('4', 'Oversea')])
    job_category = SelectField('Category', choices=[('All', 'All Job Categories'), ('1', 'Information Technology'), ('2', 'Engineering'), ('3','Education'),('4', 'Management'),('5', 'Finance') ,('6', 'Healthcare'),('7', 'Transportation')])
    # job_location = SelectField('Location', choices=[('', 'All Locations'), ('Hong Kong Island', 'Hong Kong Island'), ('Kowloon Peninsula', 'Kowloon Peninsula'), ('New Territory', 'New Territory'), ('Oversea', 'Oversea')])
    # job_category = SelectField('Category', choices=[('', 'All Job Categories'), ('Information Technology', 'Information Technology'), ('Engineering', 'Engineering'), ('Education','Education'),('Management', 'Management'),('Finance', 'Finance') ,('Healthcare', 'Healthcare'),('Transportation', 'Transportation')])
    submit = SubmitField("Search")

class JobForm(FlaskForm):
    title = StringField('Job Title')
    description = TextAreaField('Job Description')
    requirement = TextAreaField('Job Requirement')
    salary = StringField('Job Salary')
    available = BooleanField('still available?')

    location = SelectField('Location', choices=[('1', 'Hong Kong Island'), ('2', 'Kowloon Peninsula'), ('3', 'New Territory'), ('4', 'Oversea')])
    category = SelectField('Category', choices=[('1', 'Information Technology'), ('2', 'Engineering'), ('3','Education'),('4', 'Management'),('5', 'Finance') ,('6', 'Healthcare'),('7', 'Transportation')])
    submit = SubmitField("Submit")


class CompanyEditForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Company", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def __init__(self, original_username,  *args, **kwargs):
        super(CompanyEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            company = Company.query.filter_by(username=username.data).first()
            if company is not None:
                raise ValidationError("Please use different username.")
            
    