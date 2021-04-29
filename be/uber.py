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
# straight mongo access
from pymongo import MongoClient

# security
# pip install flask-bcrypt
# https://pypi.org/project/Bcrypt-Flask/
# https://auth0.com/blog/refresh-tokens-what-are-they-and-when-to-use-them/
#from flask.ext.bcrypt import Bcrypt
from flask_bcrypt import Bcrypt
from flask import g
import jwt
g = dict()

# mongo
#mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_client = MongoClient("mongodb+srv://dmouryapr:Abstergo97@uberbus.syoj4.mongodb.net/bookings?retryWrites=true&w=majority")
# mongodb+srv://admin:admin@tweets.8ugzv.mongodb.net/tweets?retryWrites=true&w=majority
# client = pymongo.MongoClient("mongodb+srv://dmouryapr:<password>@uberbus.syoj4.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
app = Flask(__name__)
CORS(app)
#CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Here are my datasets
bookings = dict()   
users1 = dict()   

################
# Security
################
def set_env_var():
    global g
    if 'database_url' not in g:
        g['database_url'] = os.environ.get("DATABASE_URL", 'mongodb+srv://test:test@bookings.hclbd.mongodb.net/bookings?retryWrites=true&w=majority')
    if 'secret_key' not in g:
        g['secret_key'] = os.environ.get("SECRET_KEY", "my_precious_1869")
    if 'bcrypt_log_rounds' not in g:
        g['bcrypt_log_rounds'] = os.environ.get("BCRYPT_LOG_ROUNDS", 13)
    if 'access_token_expiration' not in g:
        g['access_token_expiration'] = os.environ.get("ACCESS_TOKEN_EXPIRATION", 900)
    if 'refresh_token_expiration' not in g:
        g['refresh_token_expiration'] = os.environ.get("REFRESH_TOKEN_EXPIRATION", 2592000)
    if 'users' not in g:
        users = os.environ.get("USERS", 'Elon Musk,Bill Gates,Jeff Bezos,Mourya')
        print('users=', users)
        print('g.users=', list(users.split(',')))
        g['users'] = list(users.split(','))
        print('g.users=', g['users'])
    if 'passwords' not in g:
        passwords = os.environ.get("PASSWORDS", 'Tesla,Clippy,Blue Horizon,Pratap')
        g['passwords'] = list(passwords.split(','))
        print("g['passwords']=", g['passwords'])
        # Once hashed, the value is irreversible. However in the case of 
        # validating logins a simple hashing of candidate password and 
        # subsequent comparison can be done in constant time. This helps 
        # prevent timing attacks.
        #g['password_hashes'] = list(map(lambda p: bcrypt.generate_password_hash(str(p), g['bcrypt_log_rounds']).decode('utf-8'), g['passwords']))
        g['password_hashes'] = []
        for p in g['passwords']:
            g['password_hashes'].append(bcrypt.generate_password_hash(p, 13).decode('utf-8'))
        print("g['password_hashes]=", g['password_hashes'])
        g['userids'] = list(range(0, len(g['users'])))
        print("g['userids]=", g['userids'])

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
# Security Endpoints
####################
@app.route("/")
def home(): 
    return """Welcome to online mongo/twitter testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/tweets<br />
        http://localhost:5000/tweets-week<br />
        http://localhost:5000/tweets-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-tweets<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""

@app.route("/doc")
def doc(): 
    return """Welcome to online mongo/twitter testing ground!<br />
        <br />
        Run the following endpoints:<br />
        From collection:<br/>
        http://localhost:5000/tweets<br />
        http://localhost:5000/tweets-week<br />
        http://localhost:5000/tweets-week-results<br />
        Create new data:<br />
        http://localhost:5000/mock-tweets<br />
        Optionally, to purge database: http://localhost:5000/purge-db"""

# Returns an encoded userid as jwt access and a refresh tokens. Requires username 
# and password. Refresh token not used. Only meant to be used with token issuer,
# but here the token issuer and the be are one and the same.
@app.route("/login", methods=["POST"])
def login():
    try:
        print("keys")

        user = request.json['name']
        password = request.json['password']
        print('user:', user)
        obj = get_user(user)
        print('password:', password)
        print('users:', get_env_var('users'))
        if not user or not password:
            print('not user or not password!')
            return jsonify(("Authentication is required and has failed!", status.HTTP_401_UNAUTHORIZED))

        # elif not user in get_env_var('users'):
        #     print('unknown user!')
        #     return jsonify(("Unknown user!", status.HTTP_401_UNAUTHORIZED))
        elif obj["username"] != user:
            print('unknown user!')
            return jsonify(("Unknown user!", status.HTTP_401_UNAUTHORIZED))
        else:
            # presumably we only store password hashes and compare passed pwd
            # with our stored hash. For simplicity, we store the full password
            # and the hash, which we retrieve here
            # print('password_hashes:', get_env_var('password_hashes'))
            # print("get_env_var('users').index(user):", get_env_var('users').index(user))
            # password_hash = get_env_var('password_hashes')[get_env_var('users').index(user)]
            # print('password_hash:', password_hash)
            password_hash = obj["password_hash"]
            a = datetime.now()
            if not bcrypt.check_password_hash(password_hash, password):
                print('bcrypt.check_password_hash(password_hash, password) returned False!')
                return jsonify(("Authentication is required and has failed!", status.HTTP_401_UNAUTHORIZED))
            b = datetime.now()
            print('check_password took:', b - a)
            # debugging
            #print('password:', password)
            #print('type(password):', type(password))
            #for i in range(3):
            #    password_hash2 = bcrypt.generate_password_hash(password, 13).decode('utf-8')
            #    print('password_hash2:', password_hash2)
            #    if not bcrypt.check_password_hash(password_hash2, password):
            #        print('bcrypt.check_password_hash(password_hash, password) returned False!')
            #        return jsonify(("Authentication is required and has failed!", status.HTTP_401_UNAUTHORIZED))

            # create access and refresh token for the user to save.
            # User needs to pass access token for all secured APIs.
            # userid = get_env_var('userids')[get_env_var('users').index(user)]
            userid = obj["username"]
            access_token = encode_token(userid, "access")
            refresh_token = encode_token(userid, "refresh")
            print('type(access_token):', type(access_token))
            response_object = {
                "access_token": access_token,
                "refresh_token": refresh_token,
               # "userid": userid,
               # "username": user
            }
            #return response_object, 200
            #return response_object
            return jsonify((response_object, status.HTTP_200_OK))
    except Exception as e:
        print('exception:', e)
        return jsonify(("Authentication is required and has failed!", status.HTTP_401_UNAUTHORIZED))


# Returns an encoded userid. Requires both tokens. If access token expired 
# returns status.HTTP_401_UNAUTHORIZED, and user needs to fast login. If refresh 
# token expired returns status.HTTP_401_UNAUTHORIZED, and user needs to login
# with username and password. Tokens are usually passed in authorization headers 
# (auth_header = request.headers.get("Authorization")). For simplicity, I just 
# pass access token as an extra parameter in secured API calls.
@app.route("/fastlogin", methods=["POST"])
def fastlogin():
    try:
        access_token = request.json['access']
        refresh_token = request.json['refresh']

        if not access_token or not refresh_token:
            return jsonify(("Missing token(s)!", status.HTTP_401_UNAUTHORIZED))
        else:
            try:
                # first, with access token:
                userid = decode_token(access_token)
                obj = get_user(userid)
                print("fast login userid: ", userid)

                # if not userid or not userid in get_env_var('userids'):
                # if not userid in get_env_var('userids'):
                #     print("User IDs test: ", get_env_var('userids'))
                #     return jsonify(("User unknown, please login with username and password.", status.HTTP_401_UNAUTHORIZED))
                if obj["username"] != userid:
                    return jsonify(("User unknown, please login with username and password.", status.HTTP_401_UNAUTHORIZED))

                try:
                    # second, with refresh token
                    userid2 = decode_token(refresh_token)
                    print("user id 2 test: ", userid2)

                    # if not userid2 or userid2 != userid:
                    if not userid2 or userid2 != userid:
                        return jsonify(("User unknown, please login with username and password.", status.HTTP_401_UNAUTHORIZED))

                    # issue a new access token, keep the same refresh token
                    access_token = encode_token(userid, "access")
                    response_object = {
                      # "access_token": access_token.decode(),
                        "refresh_token": refresh_token,
                    }
                    return jsonify((response_object, status.HTTP_200_OK))

                # refresh token failure: Need username/pwd login
                except jwt.ExpiredSignatureError:
                    return jsonify(("Lease expired. Please log in with username and password.", status.HTTP_401_UNAUTHORIZED))
                
                except jwt.InvalidTokenError:
                    return jsonify(("Invalid token. Please log in with username and password.", status.HTTP_401_UNAUTHORIZED))

            # access token failure: Need at least fast login
            except jwt.ExpiredSignatureError:
                return jsonify(("Signature expired. Please fast log in.", status.HTTP_401_UNAUTHORIZED))
            
            except jwt.InvalidTokenError:
                return jsonify(("Invalid token. Please fast log in.", status.HTTP_401_UNAUTHORIZED))

    except:
        return jsonify(("Missing token or other error. Please log in with username and password.", status.HTTP_401_UNAUTHORIZED))


def verify_token(token):
    try:
        userid = decode_token(token)
        print("verify_token():", token, userid)
        print("verify_token():", get_env_var('userids'))
        print("verify_token():", userid in get_env_var('userids'))

        if userid is None or not userid in get_env_var('userids'):
            print("verify_token() returning False")
            return False, jsonify(("User unknown!", status.HTTP_401_UNAUTHORIZED))
        else:
            print("verify_token() returning True")
            return True, userid

    except jwt.ExpiredSignatureError:
        return False, jsonify(("Signature expired. Please log in.", status.HTTP_401_UNAUTHORIZED))

    except jwt.InvalidTokenError:
        return False, jsonify(("Invalid token. Please log in.", status.HTTP_401_UNAUTHORIZED))


################################
# Add and get new users
################################
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


@app.route("/register", methods=["POST"])
def add_user(): 
    username = request.json['username']
    password = request.json["password"]
    password_hash = bcrypt.generate_password_hash(password, 13).decode('utf-8')
    adduser = dict(username=username, password=password, password_hash = password_hash,
                _id=str(ObjectId()))               
    users1[username] = password
    insert_user(adduser)
    print('User submitted:', adduser)
    return jsonify(adduser)


def get_user(username):
    start_time = datetime.now()
    obj = {}
    with mongo_client:
        #start_time_db = datetime.now()
        db = mongo_client['bookings']
        #microseconds_caching_db = (datetime.now() - start_time_db).microseconds
        #print("*** It took " + str(microseconds_caching_db) + " microseconds to cache mongo handle.")

        print("...get_user() from mongo: ", username)
        try:
            mongo_collection = db['users']
            result = mongo_collection.find({"username":username})
            for doc in result:
                    obj = doc
        except Exception as e:
            print(e)
    return obj

    microseconds_doing_mongo_work = (datetime.now() - start_time).microseconds
    print("*** It took " + str(microseconds_doing_mongo_work) + " microseconds to insert_one.")   


################
# Apply to mongo
################

def atlas_connect():
    # Node
    # const MongoClient = require('mongodb').MongoClient;
    # const uri = "mongodb+srv://admin:<password>@tweets.8ugzv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority";
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
    return result.inserted_id


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
# bookings Endpoints 
##################

# secured with jwt
# endpoint to create new booktrip
@app.route("/book-trip", methods=["POST"])
def add_booktrip():
    user = request.json['user']
    source = request.json["sourceP"]
    destination = request.json["destinationP"]
    journeyDate = request.json["journeydDateP"]
    #accesstoken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiTW91cnlhIiwiZmlyc3ROYW1lUCI6Ik1vdXJ5YSIsImxhc3ROYW1lUCI6IlJlZGR5Iiwic291cmNlUCI6IkJvc3RvbiIsImRlc3RpbmF0aW9uUCI6IkZsb3JpZGEiLCJqb3VybmV5RGF0ZSI6IjIwMjEtMDQtMjAifQ.1ZNx3Qopm5h07ecNhoNQ1_VFLNt_c516wdtgglh7wCc"
    access_token = request.json['access-token']
    print("access_token:", access_token)
    permission = verify_token(access_token)
    # if not permission[0]: 
    #     print("tweet submission denied due to invalid token!")
    #     print(permission[1])
    #     return permission[1]
    # else:
    print('access token accepted!')

    booktrip = dict(user=user, source=source,
                 destination=destination,journeyDate=journeyDate,date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                _id=str(ObjectId()))
    bookings[booktrip['_id']] = booktrip

    insert_one(booktrip)
    print('Booking submitted:', booktrip)
    return jsonify(booktrip)

# endpoint to show all of today's bookings
@app.route("/bookings-day2", methods=["GET"])
def get_bookings_day2():
    todaysbookings = dict(
        filter(lambda elem: 
                elem[1]['date'].split(' ')[0] == datetime.now().strftime("%Y-%m-%d"), 
                bookings.items())
    )
    return jsonify(todaysbookings)

# endpoint to show all tweets 
@app.route("/bookings2", methods=["GET"])
def get_bookings2():
    return jsonify(bookings)

# endpoint to show all of this week's tweets (any user)
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
            [filter_booktrip(k) for k in weekbookings.keys()],
            key = lambda t: t['date']
        )
    })

# endpoint to show all of today's tweets (user-specific)
def filter_booktrip(t):
    booktrip = bookings[t]
    return dict(date=booktrip['date'], source=booktrip['source'],
                destination=booktrip['destination'],journeyDate=booktrip['journeyDate'], user=booktrip['user'])
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
            [filter_booktrip(k) for k in todaysbookings.keys()],
            key = lambda t: t['date']
        )
    )

# endpoint to show all of this week's tweets (user-specific)
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
            [filter_booktrip(k) for k in weeksbookings.keys()],
            key = lambda t: t['date']
        )
    )


@app.route("/bookings-user-week-results", methods=["GET"])
def get_bookings_user_week_results():
    print(request)
    user = request.args.get('user')
    weekbookings = dict(
        filter(lambda elem: 
                (datetime.now() - datetime.strptime(elem[1]['date'].split(' ')[0], '%Y-%m-%d')).days < 7 and
                (
                    #False == elem[1]['private'] or
                    user == elem[1]['user']
                ), 
                bookings.items())
    )
    #return jsonify(todaysbookings)
    return json.dumps({"results":
        sorted(
            [filter_booktrip(k) for k in weekbookings.keys()],
            key = lambda t: t['date']
        )
    })


# endpoint to get tweet detail by id
@app.route("/booktrip/<id>", methods=["GET"])
def booktrip_detail(id):
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

        for booktrip in sorted_records:
            bookings[booktrip['_id']] = booktrip


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
    set_env_var()
    applyRecordLevelUpdates()


############################
# INFO on containerization #
############################

# To containerize a flask app:
# https://pythonise.com/series/learning-flask/building-a-flask-app-with-docker-compose

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")