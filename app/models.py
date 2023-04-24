from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, timezone
from hashlib import md5
from app import app, db, login
import jwt

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from flask import session

from enum import Enum

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    job_application = db.relationship('JobApplication', backref='user', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, followers.c.followed_id == Post.user_id
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in=600, is_company=True):
        if not is_company:
            raise ValueError("Incorrect class type")
        return jwt.encode({"reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")
    
    # ------------------------------------------------------------------------------------------------------------
    def get_id(self):
        return 'user.' + str(self.id)



    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
        except:           
            return None
        return User.query.get(id)


# @login.user_loader
# def load_user(id):
#     return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<Post {self.body}>'

# /------------------------------------------------------------------------------------------------/#

@login.user_loader
def load_user(user_id):
    temp = user_id.split('.')
    type = session.get('type')
    try:
        uid = temp[1]
        if temp[0] == 'user' or type == 'user':
            return User.query.get(uid)
        elif temp[0] == 'company' or type == 'company':
            return Company.query.get(uid)
        else:
            return None
    except IndexError:
        return None

# @login.user_loader
# def load_user(id):
#     type = session.get('type')
#     if type == 'user':
#         user = User.query.get(int(id))
#     elif type == 'company':
#         user = Company.query.get(int(id))
#     else:
#         user = None
#     return user


class Company(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    name = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    publishes = db.relationship('Job', backref='publisher', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"company_reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")

    def get_id(self):
        return 'company.' + str(self.id)

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "company_reset_password"]
        except:           
            return None
        return Company.query.get(id)
    
    job_application = db.relationship('JobApplication', backref='company', lazy='dynamic')

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50))
    jobs = db.relationship('Job', backref='location')

    @staticmethod
    def insert_default_locations():
        locations = ['Hong Kong Island', 'Kowloon Peninsula', 'New Territory', 'Oversea']
        for location_name in locations:
            location = Location.query.filter_by(location=location_name).first()
            if not location:
                location = Location(location=location_name)
                db.session.add(location)
        db.session.commit()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    jobs = db.relationship('Job', backref='category')

    @staticmethod
    def insert_default_categories():
        categories = ['Information Technology','Engineering', 'Education','Management','Finance','Healthcare','Transportation']
        for category_name in categories:
            category = Category.query.filter_by(category=category_name).first()
            if not category:
                category = Category(category=category_name)
                db.session.add(category)
        db.session.commit()



# job_location = db.Table(
#     'job_location',
#     db.Column('job_id', db.Integer, db.ForeignKey('job.id')),
#     db.Column('location_id',db.Integer, db.ForeignKey('location.id'))
# )

# job_category = db.Table(
#     'job_category',
#     db.Column('job_id', db.Integer, db.ForeignKey('job.id')),
#     db.Column('category_id',db.Integer, db.ForeignKey('category.id'))
# )

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    title = db.Column(db.String(50), index=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirement = db.Column(db.Text, nullable=False)
    salary = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    available = db.Column(db.Boolean)

    # locations = db.relationship('Location', backref='job_in_location')
    # categories = db.relationship('Category', backref='job_in_category')

    job_application = db.relationship('JobApplication', backref='job', lazy='dynamic')


class JobApplicationStatus(Enum):
    submitted = 'Submitted'
    reviewed = 'Reviewed'
    interview = 'Interview'
    offered = 'Offered'
    rejected = 'Rejected'


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))

    name = db.Column(db.String(128), index=True)
    contact_number = db.Column(db.Integer, nullable=False)
    contact_email = db.Column(db.String(120), index=True, nullable=False)
    resume = db.Column(db.Text, nullable=False)

    message = db.Column(db.Text)
    reply = db.Column(db.Text)

    # status = db.Column(db.Enum(JobApplicationStatus), nullable=False)
    status = db.Column(db.String(50), nullable=False, index=True)

    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Relationships
    # job = db.relationship('Job', back_populates='job_application')
    # user = db.relationship('User', back_populates='job_application')
    # company = db.relationship('Company', back_populates='job_application')






