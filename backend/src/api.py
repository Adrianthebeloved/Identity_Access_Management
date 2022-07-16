import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
STATUS: Done
'''
@app.route('/drinks', methods=["GET"])
def retrieve_drinks():

    try:
        selection = Drink.query.order_by(Drink.id).all()
        drinks = [drink.short() for drink in selection]
    
    except:
        abort(422)

    return jsonify(
        {
            "success": True,
            "drinks": drinks
        }
    )


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
STATUS: Done
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    
    try:
        # Query the database to get all drink.long
        selection = Drink.query.all()
    
        drink = [drink.long() for drink in selection]
    except:
        abort(400)

    return jsonify(
        {
            "success": True,
            "drinks": drink
        }
    )

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
STATUS: Done
'''
@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(payload):
    # Get the json body object
    body = request.get_json()
    new_title = body.get("title", None)
    new_recipes = body.get("recipe", None)

    try:
        drink = Drink(title=new_title, recipe=json.dumps(new_recipes))
        # Commit to the database
        drink.insert()

    except BaseException:
        abort(400)

    return jsonify(
        {
            "success": True,
            "drinks": [drink.long()]
        }
    )


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
STATUS: Done
'''
@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(payload, *args, **kwargs):

    drink_id = kwargs['drink_id']
    # Get the json body object
    new_drink = request.get_json()

    try:
        # Query the database to get the object with the required id
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        if 'title' and 'recipe' in new_drink:
            drink.title = new_drink.get('title')
            
            drink.recipe = json.dumps(new_drink['recipe'])
        
        elif 'title' in new_drink:

            drink.title = new_drink.get('title')

        elif 'recipe' in new_drink:
            
            drink.recipe = json.dumps(new_drink['recipe'])
        
        else:
            abort(422)
        # Commit changes to the Database
        drink.update()

        return jsonify(
        {
            "success": True,
            "drinks": [drink.long()]
        })

    except:
        abort(422)

    

@app.route('/drinks/<id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    try:
        # Query the database to get the object with the required id
        drink = Drink.query.get(id)
        #Commit to the DB
        drink.delete()

    except BaseException:
        abort(422)

    return jsonify(
        {
            "success": True,
            "delete": id
        }, 200
    )
    


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422



@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad request"
        }), 400


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method not allowed"
        }), 405

'''
AuthError handler
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    return response, ex.status_code
