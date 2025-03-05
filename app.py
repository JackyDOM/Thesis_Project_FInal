from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
from instance.user_resource import user_ns
from models.user_model import db

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', title='My API', description='A simple API', doc='/swagger/')

# Add the user namespace to the API
api.add_namespace(user_ns)

# Dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('layout.html')

# Initialize the database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)