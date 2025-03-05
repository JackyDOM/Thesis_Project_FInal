from flask import Flask, render_template
from flask_restx import Api
from models.user_model import db
from instance.user_resource import user_ns

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', title='My API', description='A simple API', doc='/swagger/')

# Add custom namespace for User Information
api.add_namespace(user_ns)

# Initialize the database inside an application context
with app.app_context():
    db.create_all()
    

# Dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('layout.html')

if __name__ == '__main__':
    app.run(debug=True)
