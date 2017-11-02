from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from room import Room
from message import Message

class Messagelist:
    def __init__(self):
        self.messages = {}
        self.last_key = 0

    def get_all_message(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""  SELECT
                            messages.context,
                            messages.messageid,
                            users.username
                            FROM messages
                            RIGHT JOIN users ON users.id = messages.userid
                            WHERE messages.roomid = %s
                            ORDER BY messageid DESC; """, (roomid, ))

        message = [(Message(context, messageid, userhandle))
                    for context, messageid, userhandle in cursor]
        return message

    def getid(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        usernum=cursor.fetchone()
        return usernum

    def getownerid(self, twitid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT USERID FROM TWEETS WHERE TWEETID=%s""", (twitid,))
        owner = cursor.fetchone()
        return owner

    def add_message(self, message, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (current_user.username,))
        userid=cursor.fetchone()
        cursor.execute("""INSERT INTO MESSAGES (USERID, CONTEXT, ROOMID)    VALUES    (%s, %s, %s)""", (userid, message.context, roomid))
        connection.commit()
        connection.close()
