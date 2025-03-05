from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define the User table using SQLAlchemy ORM
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.String(50), nullable=False)
    personality = db.Column(db.String(100), nullable=False)
    job = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    def __init__(self, name, age, genre, dob, personality, job, description):
        self.name = name
        self.age = age
        self.genre = genre
        self.dob = dob
        self.personality = personality
        self.job = job
        self.description = description
