from flask_restx import Resource, fields, Namespace
from flask import request
from models.user_model import db, User

# Define user model for input validation
user_model = {
    'name': fields.String(required=True, description='Name of the user'),
    'age': fields.Integer(required=True, description='Age of the user'),
    'genre': fields.String(required=True, description='Genre of the user'),
    'dob': fields.String(required=True, description='Date of birth'),
    'personality': fields.String(required=True, description='Personality description'),
    'job': fields.String(required=True, description='Job description'),
    'description': fields.String(required=True, description='Short description of the user')
}

user_ns = Namespace('User_Information', description='Operations related to user information')

@user_ns.route('/user/<int:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Retrieve user information"""
        user = User.query.get(user_id)
        if not user:
            return {'message': f'User with ID {user_id} not found'}, 404
        return {
            'id': user.id,
            'name': user.name,
            'age': user.age,
            'genre': user.genre,
            'dob': user.dob,
            'personality': user.personality,
            'job': user.job,
            'description': user.description
        }, 200

    @user_ns.expect(user_model)
    def post(self, user_id):
        """Create new user information"""
        if User.query.get(user_id):
            return {'message': f'User with ID {user_id} already exists'}, 400
        data = request.get_json()
        user = User(
            name=data['name'],
            age=data['age'],
            genre=data['genre'],
            dob=data['dob'],
            personality=data['personality'],
            job=data['job'],
            description=data['description']
        )
        db.session.add(user)
        db.session.commit()
        return {'message': f'User {user_id} created successfully'}, 201

    @user_ns.expect(user_model)
    def put(self, user_id):
        """Update existing user information"""
        user = User.query.get(user_id)
        if not user:
            return {'message': f'User with ID {user_id} not found'}, 404
        data = request.get_json()
        user.name = data['name']
        user.age = data['age']
        user.genre = data['genre']
        user.dob = data['dob']
        user.personality = data['personality']
        user.job = data['job']
        user.description = data['description']
        db.session.commit()
        return {'message': f'User {user_id} updated successfully'}, 200

    def delete(self, user_id):
        """Delete user information"""
        user = User.query.get(user_id)
        if not user:
            return {'message': f'User with ID {user_id} not found'}, 404
        db.session.delete(user)
        db.session.commit()
        return {'message': f'User {user_id} deleted successfully'}, 200


@user_ns.route('/users')
class UserList(Resource):
    def get(self):
        """Retrieve all user information"""
        users = User.query.all()
        if not users:
            return {'message': 'No users found', 'code': 404}, 404

        # Format all users into a structured list
        users_list = []
        for user in users:
            users_list.append({
                'id': user.id,
                'name': user.name,
                'age': user.age,
                'genre': user.genre,
                'dob': user.dob,
                'personality': user.personality,
                'job': user.job,
                'description': user.description
            })
        
        response = {
            'message': 'All user information retrieved successfully',
            'code': 200,
            'data': users_list  # Ensure that 'data' is a list of users
        }
        return response, 200
