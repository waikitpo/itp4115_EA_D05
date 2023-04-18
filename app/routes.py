from datetime import datetime
from flask import render_template, redirect, flash, url_for, request, g
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse


from app import app, db
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, CompanyLoginForm, CompanyRegistrationForm, JobSearchForm, JobForm
from app.models import User, Post, Company, Job
# ,Location,JobCategories,Job


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    user = User.query.filter_by(username=current_user.username).first()
    company = Company.query.filter_by(username=current_user.username).first()

    if user:
        if form.validate_on_submit():
            post = Post(body=form.post.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post is live!')
            return redirect(url_for('index'))

        page = request.args.get("page", 1, type=int)
        posts = current_user.followed_posts().paginate(
            page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
        next_url = url_for(
            'index', page=posts.next_num) if posts.next_num else None
        prev_url = url_for(
            'index', page=posts.prev_num) if posts.prev_num else None
        return render_template("index.html.j2", title="Home", form=form,
                            posts=posts.items, next_url=next_url, prev_url=prev_url)

    elif company:
        return redirect(url_for('job_publish'))

@app.route('/explore')
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template("index.html.j2", title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('index')
        redirect(next_page)
    return render_template('login.html.j2', title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congraduations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html.j2', title="Register", form=form)


@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        company = Company.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset password.')
            return redirect(url_for('login'))
            
        elif company:
            send_password_reset_email(company)
            flash('Check your email for the instructions to reset password.')
            return redirect(url_for('login'))
        else:
            flash('User 404 Not Found')

    return render_template('reset_password_request.html.j2', title="Reset Password", form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    company = Company.verify_reset_password_token(token)

    # if user and company:
    #     flash('Invalid token')
    #     return redirect(url_for('index'))

    # if not user and not company:
    #     flash('Invalid token')
    #     return redirect(url_for('index'))

    if user and company is None:
        flash('Invalid token')
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('login'))
        
        elif company:
            company.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('company_login'))
        
    return render_template('reset_password.html.j2', title="Reset Password", form=form)



    # if user and company is None:
    #     return redirect(url_for('index'))
    
    # form = ResetPasswordForm()
    # if user and form.validate_on_submit():
    #     user.set_password(form.password.data)
    #     db.session.commit()
    #     flash('Your password has been reset.')

    # elif company and form.validate_on_submit():
    #     company.set_password(form.password.data)
    #     db.session.commit()
    #     flash('Your password has been reset.')

    # if form.validate_on_submit():
    #     user.set_password(form.password.data)
    #     db.session.commit()
    #     flash('Your password has been reset.')
    #     if user:
    #         return redirect(url_for('login'))
    #     elif company:
    #         return redirect(url_for('company_login'))
    # return render_template('reset_password.html.j2', title="Reset Password", form=form)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = user.followed_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template('user.html.j2', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your change have been saved.")
        return redirect(url_for('edit_profile'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title="Edit Profile", form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found.")
        return redirect(url_for('index'))
    if user == current_user:
        flash("You cannot follow yourself!")
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f"You are following {username}!")
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(f"User {username} not found.")
        return redirect(url_for('index'))
    if user == current_user:
        flash("You cannot unfollow yourself!")
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You are not following {username}!")
    return redirect(url_for('user', username=username))


@app.route("/company_login", methods=['GET', 'POST'])
def company_login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = CompanyLoginForm()
    if form.validate_on_submit():
        company = Company.query.filter_by(username=form.username.data).first()
        if company is None or not company.check_password(form.password.data):
            flash('Invalid username or password!')
            return redirect(url_for('login'))

        login_user(company, remember=form.remember_me.data)

        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for('index')
        redirect(next_page)
    return render_template('company_login.html.j2', title="Company Sign In", form=form)

@app.route("/company_register", methods=['GET', 'POST'])
def company_register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        user = Company(username=form.username.data, email=form.email.data, name=form.name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congraduations, you are now a registered Employers!')
        return redirect(url_for('company_login'))
    return render_template('company_register.html.j2', title="Register for Employer", form=form)

@app.route("/job_search", methods=['GET', 'POST'])
def job_search():
    form = JobSearchForm()
    # jobs = Job.query
    # if form.validate_on_submit():
    #     #get data from submitted form
    #     jobs.search = form.search.data
    #     #query the data base
    #     jobs = jobs.filter(Job.title.like('%' + jobs.search + '%'))
    #     jobs = jobs.order_by(Job.title).all()
    # not finish yet
    return render_template('job_search.html.j2', title="Job Search", form=form)

@app.route("/job_publish", methods=['GET', 'POST'])
@login_required
def job_publish():
    form = JobForm()
    
    if form.validate_on_submit():
        job = Job(title=form.title.data, description=form.description.data, requirement=form.requirement.data, salary=form.salary.data, job_location=form.location.data, job_category=form.category.data, available=form.available.data)

        db.session.add(job)
        db.session.commit()

        flash("Job Posted")
    return render_template('job_publish.html.j2', title="Job Publish", form=form)