from flask_login import current_user
import psycopg2 as dbapi2
from flask import current_app, request
from room import *

class Roomlist:
    def __init__(self):
        self.rooms = {}
        self.last_key = 0

    def getid(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT ID FROM USERS WHERE USERS.USERNAME=%s""", (current_user.username,))
        usernum=cursor.fetchone()
        print(usernum)
        return usernum

    def get_room(self, roomid):
            connection = dbapi2.connect(current_app.config['dsn'])
            cursor = connection.cursor()
            cursor.execute("""SELECT
                            rooms.roomid,
                            users.username,
                            rooms.maxp
                            FROM rooms
                            LEFT JOIN users ON users.id = rooms.userid
                            WHERE rooms.roomid=%s""", (roomid,))
            roomid, username, maxp=cursor.fetchone()
            rooms=Room(roomid, username, maxp)
            return rooms

    def getadmin(self):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        name='admin'
        cursor.execute("""SELECT ID FROM USERS WHERE USERNAME=%s""", (name,))
        usernum=cursor.fetchone()
        return usernum

    def get_room(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT
                        rooms.roomid,
                        users.username,
                        rooms.maxp
                        FROM rooms
                        LEFT JOIN users ON users.id = rooms.userid
                        WHERE rooms.roomid=%s""", (roomid,))
        roomid, username, maxp=cursor.fetchone()
        rooms=Room(roomid, username, maxp)
        return rooms

    def get_room_user(self, userid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT
                        rooms.roomid,
                        users.username,
                        rooms.maxp
                        FROM ROOMS
                        RIGHT JOIN USERS ON users.id = rooms.userid
                        WHERE rooms.userid=%s
                        ORDER BY rooms.roomid DESC""", (userid,))

        if cursor.rowcount==0:
            room = Room(-1, -1, -1)
            return room

        room = [(Room(roomid, username, maxp))
                    for roomid, username, maxp in cursor]
        return room

    def add_room(self, room):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO ROOMS (maxp, userid)
        VALUES    (%s, %s)""",  (room.maxp, room.userid))

        cursor.execute("""SELECT
                        room.roomid
                        FROM rooms
                        WHERE rooms.userid=%s
                        ORDER BY rooms.roomid DESC""", (room.userid,))

        room=cursor.fetchone()

        cursor.execute("""INSERT INTO ENROLL (userid, roomid)
        VALUES    (%s, %s)""",  (room.userid, room.roomid))
        connection.commit()
        connection.close()

    def inc_max(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""SELECT maxp FROM ROOMS WHERE roomid=%s""", (roomid,))
        maxps=cursor.fetchone()
        maxps=maxps+5
        cursor.execute("""UPDATE ROOMS SET maxp=%s WHERE roomid=%s""", (maxps, roomid))

    def delete_room(self, roomid):
        connection = dbapi2.connect(current_app.config['dsn'])
        cursor = connection.cursor()
        cursor.execute("""DELETE FROM ROOMS WHERE roomid=%s""", (roomid,))
        connection.commit()
        connection.close()
