from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from enroll import *

class Enrolllist:
    def __init__(self):
        self.enrolls = {}
        self.last_key = 0

    def get_roomenrolled(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""  SELECT
                            enroll.roomid,
                            users.username
                            FROM enroll
                            RIGHT JOIN users ON user.id = enroll.userid
                            WHERE enroll.roomid = %s; """, (roomid, ))

        enroll = [(Enroll(roomid, username))
                    for roomid, username in cursor]
        return enroll

    def enroll_usr(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""INSERT INTO ENROLL (USERID, ROOMID) VALUES (%s, %s)""", (userid, roomid))
        connection.commit()
        connection.close()

    def is_enrolled(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()

        cursor.execute("""SELECT ROOMID FROM ENROLL WHERE USERID=%s AND ROOMID=%s""", (userid, roomid))
        if cursor.rowcount==0:
            return False

            return True
