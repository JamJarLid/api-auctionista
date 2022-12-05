from flask import Flask, request, jsonify, session
import pymysql
from flaskext.mysql import MySQL

app = Flask(__name__)
app.config.update(
    DEBUG = True,
    SECRET_KEY = "secret_sauce",
    SESSION_COOKIE_HTTPONLY = True,
    REMEMBER_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = "Strict"
)

# connect
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'auctionista'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)


#register
@app.route("/api/register", methods=["POST"])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try: 
        query = "INSERT INTO users SET name = %s email = %s password %s"
        bind = (request.json['name'], request.json['email'], request.json['password']) 
        cursor.execute(query, bind)
        conn.commit()
        response = jsonify({"Created user ": cursor.lastrowid})
        response.status_code = 200
        return response
    except Exception as e:
        return jsonify({e})
    finally:
        cursor.close()
        conn.close()


# login
@app.route("/api/login", methods=["POST"])
def login():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        bind = (request.json['email'], request.json['password'])
        cursor.execute(query, bind)
        user = cursor.fetchone()
        if user['email']:
            session['user'] = user
            #print(session["user"]["id"])
            return jsonify({"login": True})
    except Exception as e:
        return jsonify({"login": False})
    finally:
        cursor.close()
        conn.close()

# get object list
@app.route("/api/objects", methods=["GET"])
def get_objects():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT title, info, end_time from objects")
        rows = cursor.fetchall()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        return jsonify(e)
    finally:
        cursor.close()
        conn.close()

# get object details
@app.route("/api/objects/<id>", methods=["GET"])
def get_object_details(id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = "SELECT * FROM objects WHERE objects.id = %s"
        bind = (id)
        cursor.execute(query, bind)
        rows = cursor.fetchone()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()    
    
# create new object
@app.route("/api/objects/create", methods=["POST"])
def create_object():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        user = session["user"]["id"]
        query = '''INSERT INTO objects SET objects.title = %s, objects.start_time = CURRENT_TIMESTAMP, 
objects.end_time = %s, objects.description = %s, objects.poster = %s, objects.info = %s'''
        bind = (request.json["title"], request.json["end_time"], request.json["description"],
            user, request.json["info"],)
        if user is not None:
            cursor.execute(query, bind)
            conn.commit()
            response = jsonify({"Created object ": cursor.lastrowid})
            response.status_code = 200
            return response
        else:
            return jsonify("Error: User is not logged in.")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()

app.run()