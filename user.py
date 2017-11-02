from flask import current_app
from flask_login import UserMixin
import psycopg2 as dbapi2


class User(UserMixin):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.active = True
        self.is_admin = False
        self.activetab = 0

    def get_id(self):
        return self.username

    @property
    def is_active(self):
        return self.active


def get_user(username):
    if (username=='admin'):
        user = User(username, current_app.config['ADMINPASS'])
        user.is_admin = True
        return user
    try:
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT PASSWORD FROM USERS WHERE USERNAME = %s""", (username,))
        values=cursor.fetchone()
        password=values[0]
        connection.commit()
        cursor.close()
        connection.close()
        user = User(username, password) if password else None
        return user
    except:
        pass

def get_userid(username):
    with dbapi2.connect(current_app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT ID FROM USERS WHERE USERNAME = %s""", (username,))
            values=cursor.fetchone()
            print(values)
            userid=values[0]
            print(userid)
            return userid

def get_nickname(username):
    with dbapi2.connect(current_app.config['dsn']) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT NICKNAME FROM USERPROFILE WHERE USERNAME=%s""", (username,))
            return cursor.fetchone()[0]