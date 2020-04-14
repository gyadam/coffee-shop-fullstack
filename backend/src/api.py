import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    print(drinks)
    drinks_formatted = [d.short() for d in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks_formatted
    })
    

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.all()
    drinks_formatted = [d.long() for d in drinks]
    return jsonify({
        "success": True,
        "drinks": drinks_formatted
    })
    

@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def add_drinks(jwt):
    body = request.get_json()
    title = body['title']
    print("title: ", title)
    recipe = body['recipe']
    print("recipe: ", recipe)
    drink = Drink(title=title, recipe=json.dumps(recipe))
    try:
        drink.insert()
    except SQLAlchemyError as e:
        print(e)
        print("could not add new drink")
        abort(422)
    return jsonify({
        "success": True,
        "drinks": drink.long()
    })


@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def modify_drinks(jwt, drink_id):
    error = False
    body = request.get_json()
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        if 'title' in body:
            drink.title = body['title']
        if 'recipe' in body:
            drink.recipe = body['recipe']
        drink.update()
    except SQLAlchemyError as e:
        error = True
        print(e)
        print("could not modify drink")
        abort(422)
    success = False if error else True
    return jsonify({
        "success": success,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(jwt, drink_id):
    error = False
    try:
        drink = Drink.query.filter_by(id=drink_id).one_or_none()
        drink.delete()
    except SQLAlchemyError as e:
        error = True
        print(e)
        print("could not delete drink")
        abort(422)
    success = False if error else True
    return jsonify({
        "success": success,
        "delete": drink_id
    })


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
