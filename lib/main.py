from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import Bcrypt
from sqlalchemy.ext.hybrid import hybrid_property


db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    serialize_rules = ("-cars.user",)
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    _password_hash =db.Column(db.String)

    cars = db.relationship("Car", backref="user")

    def __repr__(self):
        return f'The User is {self.name}'

    def to_dict(self):
        return{
            'id':self.id,
            'name':self.name,
        }
    
    @hybrid_property
    def password_hash(self):
        raise AttributeError('password hash cannot be viewed')

    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('utf-8')
        )
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode('utf-8')
        )

class Car(db.Model, SerializerMixin):
    __tablename__ = "cars"

    serialize_rules = ("-user.cars",)
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f'The Car model is {self.model}'