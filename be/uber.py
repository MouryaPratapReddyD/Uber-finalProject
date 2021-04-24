from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, g, session, send_from_directory, abort
from flask_cors import CORS
from flask_api import status
from datetime import date, datetime, timedelta
from calendar import monthrange
from dateutil.parser import parse
import pytz
import os
import sys
import time
import uuid
import json
import random
import string
import pathlib
import io
from uuid import UUID
from bson.objectid import ObjectId
import json as JSON
from flask_bcrypt import Bcrypt
from flask import g
import jwt
g = dict()

# straight mongo access
from pymongo import MongoClient

# mongo
#mongo_client = MongoClient('mongodb://localhost:27017/')
# mongo_client = MongoClient("mongodb+srv://admin:admin@tweets.8ugzv.mongodb.net/tweets?retryWrites=true&w=majority")
mongo_client = MongoClient("mongodb+srv://dmouryapr:Abstergo97@uberbus.syoj4.mongodb.net/bookings?retryWrites=true&w=majority")

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Here are my datasets
bookings = dict()    

client =MongoClient("mongodb+srv://dmouryapr:Abstergo97@uberbus.syoj4.mongodb.net/bookings?retryWrites=true&w=majority")
db=client.bookings


################
# JWT
################
def set_env_var():
    global g
    if 'database_url' not in g:
        g['database_url'] = os.environ.get("DATABASE_URL", 'mongodb+srv://dmouryapr:Abstergo97@uberbus.syoj4.mongodb.net/bookings?retryWrites=true&w=majority')
    if 'secret_key' not in g:
        g['secret_key'] = os.environ.get("SECRET_KEY", "my_precious_1989")
    # g['secret_key'] = os.environ.get("SECRET_KEY", "your256bitsecret")
    if 'bcrypt_log_rounds' not in g:
        g['bcrypt_log_rounds'] = os.environ.get("BCRYPT_LOG_ROUNDS", 13)
    if 'access_token_expiration' not in g:
        g['access_token_expiration'] = os.environ.get("ACCESS_TOKEN_EXPIRATION", 300)
    if 'refresh_token_expiration' not in g:
        g['refresh_token_expiration'] = os.environ.get("REFRESH_TOKEN_EXPIRATION", 86400)
    if 'users' not in g:
        users = os.environ.get("USERS", 'Mourya')
        g['users'] = list(users.split(','))
        print('users:', g['users'])
    if 'passwords' not in g:
        passwords = os.environ.get("PASSWORDS", 'Tesla')
        g['passwords'] = list(passwords.split(','))
        print("passwords in g:", g['passwords'])
        g['password_hashes'] = []
        for p in g['passwords']:
            g['password_hashes'].append(bcrypt.generate_password_hash(p, 13).decode('utf-8'))
        print("password_hashes:", g['password_hashes'])
        g['userids'] = list(range(0, len(g['users'])))
        print("userids", g['userids'])

def get_env_var(varname):
    #return g.pop(varname, None)
    global g
    return g[varname]

def encode_token(user_id, token_type):
    if token_type == "access":
        seconds = get_env_var("access_token_expiration")
    else:
        seconds = get_env_var("refresh_token_expiration")

    payload = {
        "exp": datetime.utcnow() + timedelta(seconds=seconds),
        "iat": datetime.utcnow(),
        "sub": user_id,
    }
    return jwt.encode(
        payload, get_env_var("secret_key"), algorithm="HS256"
    )

def decode_token(token):
    payload = jwt.decode(token, get_env_var("secret_key"), algorithms=["HS256"])
    
    print("decode_token:", payload)
    return payload["sub"]


####################
# Uber Authentication Endpoints
####################
@app.route("/")
def home(): 
    return """Welcome to online mongo/uber testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/bookings<br />
        http://localhost:5000/bookings-week<br />
        http://localhost:5000/bookings-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-bookings<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""

@app.route("/doc")
def doc(): 
    return """Welcome to online mongo/twitter testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/bookings<br />
        http://localhost:5000/bookings-week<br />
        http://localhost:5000/bookings-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-bookings<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""

# Returns an encoded userid as jwt access and a refresh tokens. Requires username 
# and password. Refresh token not used. Only meant to be used with token issuer,
# but here the token issuer and the be are one and the same.
@app.route("/login", methods=["POST"])
def login():
    try:
        user = request.json['name']
        password = request.json['password']
        print('user:', user)
        print('password:', password)
        print('users:', get_env_var('users'))
        if not user or not password:
            print('Username or the password not entered')
            return jsonify(("Username and password authentication failed", status.HTTP_401_UNAUTHORIZED))
        elif not user in get_env_var('users'):
            print('No such username exists')
            return jsonify(("Entered username does not exist", status.HTTP_401_UNAUTHORIZED))
        else:
            # presumably we only store password hashes and compare passed pwd
            # with our stored hash. For simplicity, we store the full password
            # and the hash, which we retrieve here
            print('password_hashes:', get_env_var('password_hashes'))
            print("get_env_var('users').index(user):", get_env_var('users').index(user))
            password_hash = get_env_var('password_hashes')[get_env_var('users').index(user)]
            print('password_hash:', password_hash)
            a = datetime.now()
            if not bcrypt.check_password_hash(password_hash, password):
                print('Verification of Password with the signature = False')
                return jsonify(("Authentication failed", status.HTTP_401_UNAUTHORIZED))
            b = datetime.now()
            print('check_password took:', b - a)

            # create access and refresh token for the user to save.
            # User needs to pass access token for all secured APIs.
            userid = get_env_var('userids')[get_env_var('users').index(user)]
            access_token = encode_token(userid, "access")
            refresh_token = encode_token(userid, "refresh")
            print('type(access_token):', type(access_token))
            response_object = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
            return jsonify((response_object, status.HTTP_200_OK))
    except Exception as e:
        print('exception:', e)
        return jsonify(("AAuthentication failed", status.HTTP_401_UNAUTHORIZED))


# Returns an encoded userid. Requires both tokens. If access token expired 
# returns status.HTTP_401_UNAUTHORIZED, and user needs to fast login. If refresh 
# token expired returns status.HTTP_401_UNAUTHORIZED, and user needs to login
# with username and password. Tokens are usually passed in authorization headers 
# (auth_header = request.headers.get("Authorization")). For simplicity, I just 
# pass access token as an extra parameter in secured API calls.
@app.route("/fastlogin", methods=["POST"])
def fastlogin():
    try:
        access_token = request.json['access-token']
        refresh_token = request.json['refresh-token']

        if not access_token or not refresh_token:
            return jsonify(("Access or Refresh token missing", status.HTTP_401_UNAUTHORIZED))
        else:
            try:
                # first, with access token:
                userid = decode_token(access_token)

                if not userid or not userid in get_env_var('userids'):
                    return jsonify(("No such username exists, signup or use default login", status.HTTP_401_UNAUTHORIZED))

                try:
                    # second, with refresh token
                    userid2 = decode_token(refresh_token)

                    if not userid2 or userid2 != userid:
                        return jsonify(("No such username exists, signup or use default login", status.HTTP_401_UNAUTHORIZED))

                    # issue a new access token, keep the same refresh token
                    access_token = encode_token(userid, "access")
                    response_object = {
                  #      "access_token": access_token.decode(),
                        "refresh_token": refresh_token,
                    }
                    return jsonify((response_object, status.HTTP_200_OK))

                # refresh token failure: Need username/pwd login
                except jwt.ExpiredSignatureError:
                    return jsonify(("Signup or use default login", status.HTTP_401_UNAUTHORIZED))
                
                except jwt.InvalidTokenError:
                    return jsonify(("Invalid token. Use default login", status.HTTP_401_UNAUTHORIZED))

            # access token failure: Need at least fast login
            except jwt.ExpiredSignatureError:
                return jsonify(("Signature expired. Use fast login", status.HTTP_401_UNAUTHORIZED))
            
            except jwt.InvalidTokenError:
                return jsonify(("Invalid token. Use fast login", status.HTTP_401_UNAUTHORIZED))

    except:
        return jsonify(("Token issue. Use default login", status.HTTP_401_UNAUTHORIZED))


def verify_token(token):
    try:
        userid = decode_token(token)
        print("verify_token():", token, userid)
        print("verify_token():", get_env_var('userids'))
        print("verify_token():", userid in get_env_var('userids'))

        if userid is None or not userid in get_env_var('userids'):
            print("Token verification = False")
            return False, jsonify(("No such username exists, signup or use default login", status.HTTP_401_UNAUTHORIZED))
        else:
            print("Token verification = True")
            return True, userid

    except jwt.ExpiredSignatureError:
        return False, jsonify(("Signature expired. Use default log in", status.HTTP_401_UNAUTHORIZED))

    except jwt.InvalidTokenError:
        return False, jsonify(("Invalid token. Use default log in", status.HTTP_401_UNAUTHORIZED))


################
# Apply to mongo
################

def atlas_connect():
    # Node
    # const MongoClient = require('mongodb').MongoClient;
    # const uri = "mongodb+srv://admin:<password>@bookings.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
    # const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });
    # client.connect(err => {
    # const collection = client.db("test").collection("devices");
    # // perform actions on the collection object
    # client.close();
    # });

    # Python
    client = pymongo.MongoClient("mongodb+srv://dmouryapr:Abstergo97@uberbus.syoj4.mongodb.net/bookings?retryWrites=true&w=majority")
    db = client.bookings


# database access layer
def insert_one(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['bookings']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_one() to mongo: ", r)
        try:
            mongo_collection = db['bookings']
            result = mongo_collection.insert_one(r)
            print("inserted _ids: ", result.inserted_id)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_one.")


def update_one(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['bookings']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...update_one() to mongo: ", r)
        try:
            mongo_collection = db['bookings']
            result = mongo_collection.update_one(
                {"_id" : r['_id']},
                {"$set": r},
                upsert=True)
            printg ("...update_one() to mongo acknowledged:", result.modified_count)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to update_one.")


def insert_many(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['bookings']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_many() to mongo: ", r.values())
        try:
            mongo_collection = db['bookings']
            result = mongo_collection.insert_many(r.values())
            print("inserted _ids: ", result.inserted_ids)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_many.")


def update_many(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['bookings']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...insert_many() to mongo: ", r.values())
        # much more complicated: use bulkwrite()
        # https://docs.mongodb.com/manual/reference/method/db.collection.bulkWrite/#db.collection.bulkWrite
        ops = []
        records = r
        print("...bulkwrite() to mongo: ", records)
        for one_r in records.values():
            op = dict(
                    replaceOne=dict(
                        filter=dict(
                            _id=one_r['_id']
                            ),
                        replacement=one_r,
                        upsert=True
                    )
            )
            ops.append(op)
        try:
            mongo_collection = db['bookings']
            result = mongo_collection.bulkWrite(ops, ordered=True)
            print("matchedCount: ", result.matchedCount)
        except Exception as e:
            print(e)

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to update_many.")


def tryexcept(requesto, key, default):
    lhs = None
    try:
        lhs = requesto.json[key]
        # except Exception as e:
    except:
        lhs = default
    return lhs

## seconds since midnight
def ssm():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return str((now - midnight).seconds)


##################
# Uber endpoints
##################

@app.route('/health', methods=["GET"])
def getHealth():
    return "Health checck - uber.Py application"

# endpoint to signup a user
@app.route("/register", methods=["POST"])
def add_user():
    username = request.json['username']
    password = request.json["password"]
    adduser = dict(username=username, password=password,
                _id=str(ObjectId()))
    insert_user(adduser)
    print('User successfully registered:', adduser)
    return jsonify(adduser)
def insert_user(r):
    start_time = datetime.now()
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['bookings']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")
        print("...insert_user() to mongo: ", r)
        try:
            mongo_collection = db['users']
            result = mongo_collection.insert_one(r)
            print("inserted _ids: ", result.inserted_id)
        except Exception as e:
            print(e)
    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_one.")


# endpoint to book a new ride
@app.route("/book-ride", methods=["POST"])
def add_bookride():
    
    user = request.json['user']
    # userEmail = request.json['userEmail']
    firstName = request.json["firstNameA"]
    lastName = request.json["lastNameA"]
    source = request.json["sourceA"]
    destination = request.json["destinationA"]
    journeyDate = request.json["journeydDateA"]

    access_token = request.json['access-token']
    print("access_token:", access_token)
    permission = verify_token(access_token)
    print('access token accepted!')

    bookride = dict(user=user, firstName=firstName, lastName=lastName, source=source,
                 destination=destination,journeyDate=journeyDate,date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                _id=str(ObjectId()))
    bookings[bookride['_id']] = bookride

    insert_one(bookride)
    print('Successfully booked a ride:', bookride)
    return jsonify(bookride)

# endpoint to show all of today's bookings
@app.route("/bookings-day2", methods=["GET"])
def get_bookings_day2():
    todaysbookings = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d"), 
                bookings.items())
    )
    return jsonify(todaysbookings)

# endpoint to show all bookings 
@app.route("/bookings2", methods=["GET"])
def get_bookings2():
    return jsonify(bookings)

# endpoint to show all of this week's bookings (any user)
@app.route("/bookings-week", methods=["GET"])
def get_bookings_week2():
    weeksbookings = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7, 
                bookings.items())
    )
    return jsonify(weeksbookings)

@app.route("/bookings", methods=["GET"])
def get_bookings_results():
    return json.dumps({"results":
        sorted(
            bookings.values(),
            key = lambda t: t['date']
        )
    })


@app.route("/bookings-week-results", methods=["GET"])
def get_bookings_week_results():
    weekbookings = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private']
                ), 
                bookings.items())
    )
    #return jsonify(todaysbookings)
    return json.dumps({"results":
        sorted(
            [filter_bookride(k) for k in weekbookings.keys()],
            key = lambda t: t['date']
        )
    })

# endpoint to show all of today's bookings (user-specific)
def filter_bookride(t):
    bookride = bookings[t]
    return dict(date=bookride['date'], firstName=bookride['firstName'], 
                lastName=bookride['lastName'], source=bookride['source'],
                destination=bookride['destination'],journeyDate=bookride['journeyDate'], user=bookride['user'])
@app.route("/bookings-user-day", methods=["POST"])
def get_bookings_user_day():
    user = request.json['user']
    todaysbookings = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d") and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                bookings.items())
    )
    #return jsonify(todaysbookings)
    return jsonify(
        sorted(
            [filter_bookride(k) for k in todaysbookings.keys()],
            key = lambda t: t['date']
        )
    )

# endpoint to show all of this week's bookings (user-specific)
@app.route("/bookings-user-week", methods=["POST"])
def get_bookings_user_week():
    user = request.json['user']
    weeksbookings = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                bookings.items())
    )
    #return jsonify(weeksbookings)
    return jsonify(
        sorted(
            [filter_bookride(k) for k in weeksbookings.keys()],
            key = lambda t: t['date']
        )
    )


@app.route("/bookings-user-week-results", methods=["GET"])
def get_bookings_user_week_results():
    user = request.json['user']
    weekbookings = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                bookings.items())
    )
    #return jsonify(todaysbookings)
    return json.dumps({"results":
        sorted(
            [filter_bookride(k) for k in weekbookings.keys()],
            key = lambda t: t['date']
        )
    })


# endpoint to get bookride detail by id
@app.route("/bookride/<id>", methods=["GET"])
def bookride_detail(id):
    return jsonify(bookings[id])


##################
# Apply from mongo
##################
def applyRecordLevelUpdates():
    return None

def applyCollectionLevelUpdates():
    global bookings
    with mongo_client:
        db = mongo_client['bookings']
        mongo_collection = db['bookings']

        cursor = mongo_collection.find({})
        records = list(cursor)

        howmany = len(records)
        print('found ' + str(howmany) + ' bookings!')
        sorted_records = sorted(records, key=lambda t: datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S'))
        #return json.dumps({"results": sorted_records })

        for bookride in sorted_records:
            bookings[bookride['_id']] = bookride


################################################
# Mock
################################################

# add new bookride, for testing
@app.route("/dbg-bookride", methods=["GET"])
def dbg_bookride():
    with app.test_client() as c:
        json_data = []
        name = ''.join(random.choices(string.ascii_lowercase, k=7))
        description = ''.join(random.choices(string.ascii_lowercase, k=50))
        print("posting..")
        rv = c.post('/bookride', json={
            'user': name, 'description': description,
            'private': False, 'pic': None
        })
    return rv.get_json()


# endpoint to mock bookings
@app.route("/mock-bookings", methods=["GET"])
def mock_bookings():

    # first, clear all collections
    global bookings
    bookings.clear()

    # create new data
    json_data_all = []
    with app.test_client() as c:
        
        # bookings: 30
        print("@@@ mock-bookings(): bookings..")
        json_data_all.append("@@@ bookings")            
        for i in range(30):
            description = []
            private = random.choice([True, False])
            for j in range(20):
                w = ''.join(random.choices(string.ascii_lowercase, k=random.randint(0,7)))
                description.append(w)
            description = ' '.join(description)
            u = ''.join(random.choices(string.ascii_lowercase, k=7))
            img_gender = random.choice(['women', 'men'])
            img_index = random.choice(range(100))
            img_url = 'https://randomuser.me/api/portraits/' + img_gender + '/' + str(img_index) + '.jpg'
            rv = c.post('/bookride', json={
                'user': u, 'private': private,
                'description': description, 'pic': img_url
            })
            #json_data.append(rv.get_json())
        json_data_all.append(bookings)

    # done!
    print("@@@ mock-bookings(): done!")
    return jsonify(json_data_all)


##################
# ADMINISTRATION #
##################

# This runs once before the first single request
# Used to bootstrap our collections
@app.before_first_request
def before_first_request_func():
    set_env_var()
    applyCollectionLevelUpdates()

# This runs once before any request
@app.before_request
def before_request_func():
    applyRecordLevelUpdates()


############################
# INFO on containerization #
############################

# To containerize a flask app:
# https://pythonise.com/series/learning-flask/building-a-flask-app-with-docker-compose

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')