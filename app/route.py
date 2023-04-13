from flask import render_template, redirect, url_for
from app.forms import LoginForm

def index():
    return render_template('index.html')

def login():
    form = LoginForm()
    if form.validate_on_submit():
        msg = 'username={}, password={}, remember_me={}'.format(
            form.username.data,
            form.password.data,
            form.remember_me.data
        )
        return redirect(url_for('index'))

    return render_template('login.html', title="Sign In", form=form)