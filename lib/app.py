from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound
from main import db, User

app = Flask(__name__)
api= Api(app)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.py"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True


migrate = Migrate(app, db)

db.init_app(app)

class Index(Resource):
    def get(self):
        response_body = "<h1>Hello, World</h1>"
        status =200
        headers ={}
        return make_response(response_body, status, headers)
api.add_resource(Index, "/")



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