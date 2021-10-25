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

db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_all_drinks():
    try:
        all_drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks' : [drink.short() for drink in all_drinks]
            })
    except:
        abort(404)

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_detail_drinks(jwt):
    try:
        all_drinks = Drink.query.all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in all_drinks]
            })
    except:
        abort(404)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(jwt):
    body = request.get_json()
    if not ("title" in body and "recipe" in body):
        abort(422)

    title = body.get('title')
    recipe = body.get('recipe')


    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            "success": True,
            "drinks" : [drink.long()],
            })
    except:
        abort(422)

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(jwt, id):
    drink = Drink.query.get(id)

    if drink!=None:
        try:
            body = request.get_json()


            title = body.get("title")
            recipe = body.get("recipe")

            if title:
                drink.title = title
            if recipe:
                drink.recipe = recipe #attention
            
            drink.update()

            return jsonify({
                "success": True,
                "drinks" : [drink.long()]
                })
        except:
            abort(422)

    else:
        abort(404)

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt, id):
    drink = Drink.query.get(id)

    if drink!=None:
        try:
            drink.delete()

            return jsonify({
                'success': True,
                'delete': id
            })
        except:
            abort(422)
    else:
        abort(404)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found"
        }), 404

@app.errorhandler(401)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Not authorized"
        }), 401

@app.errorhandler(AuthError)
def auth_error_handler(AuthError):
    return (jsonify(
        {
            "error": AuthError.status_code,
            "message": AuthError.error["description"],
            "success": False,
        }
    ), AuthError.status_code,) 