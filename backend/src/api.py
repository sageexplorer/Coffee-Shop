import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from urllib.request import urlopen

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


db_drop_and_create_all()

''' -- ROUTES -- '''

@app.route('/drinks')
def get_drinks():
    # auth_token = request.headers.get('Authorization', None)
    # print('My authorization is ', auth_token)
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'status_code':200,
            'drinks': formatted_drinks,
        })
    except Exception as e:
        print(e)
        abort(404)



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(permission=''):
    try:
        drinks = Drink.query.all()
        formatted_drinks = [drink.long() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except Exception:
        abort(422)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(permission=''):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
   
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drink': request.get_json()
        })
    except Exception as e:
        print("MY ERROR IS",e)
        abort(422)
  

@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(permission, id):

    drink = Drink.query.filter_by(id=id).first()
    if drink is None:
        abort(404)
    params = lambda val: request.get_json().get(val)
    try:
        if params('title'):
            drink.title = request.get_json()['title']
        if params('recipe'):
            drink.recipe = json.dumps(request.get_json()['recipe'])
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(permission, id):
    drink = Drink.query.filter_by(id=id).first()
    if drink is None:
        abort(404)
    try:
        drink.delete()
        success = True
    except Error:
        abort(422)
        success = False
    finally:
        return jsonify({
            'success': success,
            'delete': id
      })    



## Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422



@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Not found."
                    }), 404


@app.errorhandler(401)
def autherror(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Authorization error"
                    }), 401
@app.errorhandler(403)
def permissionerror(error):
    return jsonify({
                    "success": False, 
                    "error": 403,
                    "message": "Permission Denied."
                    }), 403                    
