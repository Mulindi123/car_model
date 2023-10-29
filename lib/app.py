from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from flask_bcrypt import Bcrypt
from main import db, User

app = Flask(__name__)
app.secret_key = b'\x10J\x11lL\x13\xbe\x86\xfe\xa9\xc6\x06\xcbY)\x81'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


migrate = Migrate(app, db , render_as_batch=True)
db.init_app(app)

bcrypt = Bcrypt(app)

api= Api(app)
CORS(app, origins= "*")

@app.before_request
def check_if_logged_in():
    if not session["user_id"]\
    and request.endpoint != "login" and request.endpoint != "signup":
        return {"error": "unauthorized"}, 401

class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id==session['user_id']).first()
            return user.to_dict(), 200
        
        return {'error': 'Resource unavailable'}
    
api.add_resource(CheckSession, "/session", endpoint="session")

class Index(Resource):
    def get(self):
        response_body = "<h1>Hello, World</h1>"
        status =200
        headers ={}
        return make_response(response_body, status, headers)
api.add_resource(Index, "/")


class Signup(Resource):
    def post(self):
        name = request.get_json().get("name")
        password = request.get_json().get("password")

        if name and password:
            new_user = User(name=name)
            new_user.password_hash = password

            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id
            return new_user.to_dict(), 201
        
        return {"error": "user details must be added"}, 422
        
api.add_resource(Signup, "/signup", endpoint="signup")

class Login(Resource):
    def post(self):
        name = request.get_json().get("name")
        password = request.get_json().get("password")
        user = User.query.filter(User.name==name).first()

        if user and user.authenticate(password):
            session["user_id"] = user.id

            return user.to_dict(), 200
        else:
            return {'error': 'user or password id not correct!'}, 401
        
api.add_resource(Login, "/login", endpoint="login")

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {'info': 'user logged out successfully'}
        else:
            return {'error': 'unauthorized'}, 401
        
api.add_resource(Logout, "/logout", endpoint="logout")


class Users(Resource):
    def get(self):
        # users = []
        # for user in User.query.all():
        #     user_dict = user.to_dict()
        #     users.append(user_dict)
        users = [user.to_dict() for user in User.query.all()]
        response = make_response(
            jsonify(users),
            200
        )

        return response
    
    def post(self):
        # Check if the 'name' key is in the JSON data
        if 'name' in request.json:
            new_user = User(name=request.json['name'])
            db.session.add(new_user)
            db.session.commit()
            user_dict = new_user.to_dict()

            response = make_response(
                jsonify(user_dict),
                201
            )
        else:
            response = make_response(
                jsonify({"message": "Name is missing in the request JSON"}),
                400
            )

        return response
    
api.add_resource(Users, "/users")

class UserById(Resource):
    def get(self,id):
        user=User.query.filter_by(id=id).first()
        user_dict = {
                "name": user.name,
            }
    
        response=make_response(jsonify(user_dict),200)

        return response

    def patch(self,id):
        user = User.query.filter_by(id=id).first()

        for attr in request.form:
            setattr(user, attr, request.form[attr])

            db.session.add(user)
            db.session.commit()

            user_dict = {
                "name": user.name,
            }

            response = make_response(
                jsonify(user_dict),
                200
            )

            return response
        
    def delete(self,id):
        user=User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()

       
        response_body ={
           "delete_successful": True,
           "message": "User deleted successfully"
        }

        response = make_response(jsonify(response_body), 200)

        return response

api.add_resource(UserById, '/users/<int:id>')


@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(jsonify({"message": "Resource not found in the server"}), 404)
    
    return response


# @app.route('/users', methods=['GET', 'POST'])
# def users():

#     if request.method == 'GET':
#         users = []
#         for user in User.query.all():
#             user_dict = user.to_dict()
#             users.append(user_dict)

#         response = make_response(
#             jsonify(users),
#             200
#         )

#         return response
    

#     elif request.method == 'POST':
#         new_user = User(
#             name=request.form.get("name"),
#         )

#         db.session.add(new_user)
#         db.session.commit()

#         user_dict = new_user.to_dict()

#         response = make_response(
#             jsonify(user_dict),
#             201
#         )



# @app.route('/users/<int:id>', methods=["GET","PATCH", "DELETE"])
# def user_by_id(id):
#     if request.method == "GET":
#         user=User.query.filter_by(id=id).first()
#         user_dict = {
#                 "name": user.name,
#             }
    
#         response=make_response(jsonify(user_dict),200)

#         response.headers["Content-Type"]= "application/json"

#         return response
   
#     elif request.method == 'PATCH': 
#         user = User.query.filter_by(id=id).first()

#         for attr in request.form:
#             setattr(user, attr, request.form[attr])

#             db.session.add(user)
#             db.session.commit()

#             user_dict = {
#                 "name": user.name,
#             }

#             response = make_response(
#                 jsonify(user_dict),
#                 200
#             )

#             return response
   
#     elif request.method == "DELETE":
#        user=User.query.filter_by(id=id).first()
#        db.session.delete(user)
#        db.session.commit()

       
#        response_body ={
#            "delete_successful": True,
#            "message": "User deleted successfully"
    #    }

    #    response = make_response(jsonify(response_body), 200)

    #    return response

# @app.route("/users")
# def users():
#     users = []
#     for user in User.query.all():
#         user_dict = {
#             "name": user.name
#         }
#         users.append(user_dict)
#     response= make_response(jsonify(users), 200)


#     return response

if __name__ == "__main__":
    app.run(port=5555, debug=True)