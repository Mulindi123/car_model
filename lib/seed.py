from faker import Faker
from main import db,User,Car
from random import choice
from app import app

fake=Faker()

with app.app_context(): 
    User.query.delete()
    Car.query.delete()

    users=[]

    for i in range(50):
        user=User(name=fake.name())
        users.append(user)
    db.session.add_all(users)

    car_models=["Camry", "Corolla", "Rav4", "Highlander", "Prius", "Tacoma", "Sienna", "Tundra", "Land Cruiser", "Yaris"]
    
    cars=[]

    for i in range(100):
        car=Car(model=choice(car_models), user=choice(users))
        cars.append(car)
    db.session.add_all(cars)

    db.session.commit()