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
        cursor.execute('''SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects
LEFT JOIN bids
ON objects.id = bids.object
GROUP BY objects.id''')
        rows = cursor.fetchall()
        response = jsonify(rows)
        response.status_code = 200
        return response
    except Exception as e:
        return jsonify(e)
    finally:
        cursor.close()
        conn.close()

# get object category list
@app.route("/api/objects/categories/<id>", methods=["GET"])
def get_objects_by_category(id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        query = '''SELECT objects.title, objects.info, objects.end_time, MAX(bids.amount) as current_bid
FROM objects 
LEFT JOIN bids
ON objects.id = bids.object
WHERE objects.category = %s
GROUP BY objects.id'''
        bind = (id)
        cursor.execute(query, bind)
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
        query2 = "SELECT * FROM bids WHERE bids.object = %s ORDER BY bids.amount DESC LIMIT 5"        
        bind = (id)
        cursor.execute(query, bind)
        rows = cursor.fetchall()
        cursor.execute(query2, bind)
        rows2 = cursor.fetchall()
        response = jsonify([rows, rows2])
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
objects.end_time = %s, objects.description = %s, objects.poster = %s, objects.info = %s, 
objects.starting_price = %s, objects.reserve_price = %s'''
        bind = (request.json["title"], request.json["end_time"], request.json["description"],
            user, request.json["info"], request.json["starting_price"], request.json["reserve_price"])
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

# create bid
@app.route("/api/objects/<id>/bid", methods=["POST"])
def create_bid(id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        user = session["user"]["id"]
        cursor.execute(f"SELECT objects.poster FROM objects WHERE objects.id = {id} ")
        seller = cursor.fetchone()
        cursor.execute(f"SELECT MAX(bids.amount) AS current_bid FROM bids WHERE bids.object = {id}")
        current_bid = cursor.fetchone()
        new_bid = request.json["amount"]
        query = "INSERT INTO bids SET bids.user = %s, bids.object = %s, bids.amount = %s, bids.date= CURRENT_TIMESTAMP"
        bind = (user, id, new_bid)
        if user is not None:
            if user != seller['poster']:
                if new_bid > current_bid['current_bid']:
                    cursor.execute(query, bind)
                    conn.commit()
                    response = jsonify({"Created bid ": cursor.lastrowid})
                    response.status_code = 200
                    return response
                else:
                    return jsonify(f"Error: Bid is too low, your bid needs to be higher than {current_bid['current_bid']}")
            else:
                return jsonify("Error: You cannot bid on your own item!")
        else: 
            return jsonify("Error: User is not logged in.")
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        conn.close()
        
app.run()