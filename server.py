# -*- coding: utf-8 -*-
import datetime
import os
import json
import re
import psycopg2 as dbapi2
import math
import time

from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_login import LoginManager
from flask_login import current_user, login_required, login_user, logout_user
from passlib.apps import custom_app_context as pwd_context
from flask import current_app, request
from user import *
from messagelist import *
from message import *
from enroll import *
from enrolllist import *
from room import Room
from roomlist import Roomlist
from forms import *

lm = LoginManager()
app = Flask(__name__)

def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
            dbname='{}'""".format(user, password, host, port, dbname)
    return dsn

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)

def create_app():
    app.config.from_object('settings')

    app.Enrolllist = Enrolllist()
    app.Roomlist = Roomlist()
    app.Messagelist = Messagelist()

    lm.init_app(app)
    lm.login_view='login_page'

    return app


@app.route('/')
def root_page():
    return redirect(url_for('home_page'))

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form=LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        user = get_user(username)
        if user is not None:
            password = form.password.data
            if pwd_context.verify(password, user.password):
                login_user(user)
                try:
                    with dbapi2.connect(app.config['dsn']) as connection:
                        with connection.cursor() as cursor:
                            cursor.execute("""SELECT * FROM USERS WHERE ID=1""")
                except:
                    return redirect(url_for('initialize_database'))
                flash('You have logged in.')
                next_page = request.args.get('next', url_for('home_page'))
                return redirect(next_page)
        flash('Invalid credentials.')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = pwd_context.encrypt(form.password.data)
        try:
            with dbapi2.connect(app.config['dsn']) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("""INSERT INTO USERS (USERNAME, PASSWORD) VALUES (%s, %s)""", (username, password))
                    user=get_user(username)
                    return redirect(url_for('home_page'))
        except:
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)

@app.route('/home', methods=['GET'])
@login_required
def home_page():
    current_user.activetab = 0
    now = datetime.datetime.now()
    if    request.method == 'GET':
        now = datetime.datetime.now()
        userid=current_app.Roomlist.getid()
        chkrm=current_app.Roomlist.chkroom(userid)

        if(chkrm==0):
            room=Room(1,userid,10)
            current_app.Roomlist.add_room(room)

        rooms = current_app.Roomlist.get_room_user(userid)
        return render_template('home.html', username=request.args.get('username'), rooms=rooms,  current_time=now.ctime())

@app.route('/404', methods=['GET'])
@login_required
def error_page():
    now = datetime.datetime.now()
    if    request.method == 'GET':
        return render_template('error.html')

@app.route('/adminpanel')
@login_required
def adminpanel():
    current_user.activetab = 15
    if not current_user.is_admin:
        abort(401)
    return render_template('adminpanel.html')

@app.route('/addroom')
@login_required
def addroom():
    return render_template('add_room.html')

@app.route('/enroll')
@login_required
def enroll():
    return render_template('enroll.html')



@app.route('/rooms/<int:room_id>', methods=['GET', 'POST'])
@login_required
def rooms_page(room_id):
    id_room=room_id
    is_enrolled=current_app.Enrolllist.is_enrolled(room_id)

    if request.method == 'GET':
        message = current_app.Messagelist.get_all_message(room_id)
        if is_enrolled==False:
            return(redirect(url_for('error_page')))

        else:
            return render_template('room.html', messages=message, room_id=room_id)
    else:
        content = request.form['content']
        messageid=0
        userh="NONE"
        message = Message(content, messageid, userh)
        current_app.Messagelist.add_message(message, room_id)
        message = current_app.Messagelist.get_all_message(room_id)
        return render_template('room.html', messages=message, room_id=room_id)


@app.route('/deleteuser', methods=['GET','POST'])
@login_required
def deleteuser():
    current_user.activetab = 15
    if not current_user.is_admin:
        abort(401)
    if request.method == 'POST':
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                username=request.form['selecteduser']
                if username=='- Select user -':
                    flash('Please select a user to delete')
                else:
                    cursor.execute("""DELETE FROM USERS WHERE USERNAME=%s""",(username,))
                    flash("User '%s' is deleted." % get_nickname(username))
        return redirect(url_for('deleteuser'))
    else:
        with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT USERNAME, NICKNAME FROM USERPROFILE""")
                users=cursor.fetchall()
        return render_template('deleteuser.html', users=users)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have logged out.')
    return redirect(url_for('home_page'))

def main():
    app = create_app()
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant' host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)

@app.route('/initdb')
def initialize_database():
   # if not current_user.is_admin:
    #    abort(401)
    with dbapi2.connect(app.config['dsn']) as connection:
            with connection.cursor() as cursor:
                cursor.execute(open("script.sql", "r").read())
    #time.sleep(5)
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    main()
