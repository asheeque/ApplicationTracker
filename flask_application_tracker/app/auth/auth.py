from flask import Blueprint, request, jsonify
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests

# Import the add_user function
from app.db.mongo_manager import add_or_update_user_token
from datetime import datetime, timedelta
from flask import g
import logging
import os
SECRET_KEY = os.getenv("SECRET_KEY")




auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/callback', methods=['POST'])
def auth_callback():
    
    # print("request",token)
    
    # return jsonify(success=False, message="Token missing"), 400
    try:
        # Extract the token from the request data
        token = request.json.get('credential')
        GOOGLE_CLIENT_ID = request.json.get('clientId')

        # Verify the token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        if 'iss' not in idinfo or idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        user_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo['name'] 
        user_data = {"user_id": user_id, "email": email, "name": name,"googleToken":token}
        add_or_update_user_token(user_data)
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)  # Token expires in 1 day
        }

        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"success": True, "message": "Logged in successfully","token":jwt_token})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid token"})


def check_auth_middleware():
    BearerToken = request.headers.get('Authorization')
    if not BearerToken or "Bearer " not in BearerToken:
        logging.warning("Invalid Authorization header format.")
        return jsonify(success=False, message="Token missing or malformed"), 400
    
    token = BearerToken.split(" ")[1]
    if not token:
        logging.warning("Token missing after Bearer keyword.")
        return jsonify(success=False, message="Token missing"), 400

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        g.user = decoded_token
    except jwt.ExpiredSignatureError:
        logging.warning("Expired JWT token used.")
        return jsonify(success=False, message="Token has expired"), 401
    except jwt.DecodeError:
        logging.warning("Token decode error.")
        return jsonify(success=False, message="Token is invalid"), 403
    except jwt.InvalidTokenError:
        logging.warning("Invalid JWT token used.")
        return jsonify(success=False, message="Invalid token"), 403
    return None


    # GOOGLE_CERTS_URL = "https://www.googleapis.com/oauth2/v3/certs"
    # api = "https://www.googleapis.com/oauth2/v1/userinfo?access_token="+token
    # response = requests.get(api)
    # jwks = response.json()
    # print(jwks)
    # return jsonify(success=False, message="token"), 401
    # public_keys = {}
    
    # for jwk in jwks['keys']:
    #     kid = jwk['kid']
    #     public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    # header = jwt.get_unverified_header(token)
    # kid = header['kid']
    # key = public_keys[kid]

    # try:
    #     # Decode and verify the token
    #     decoded_token = jwt.decode(token, key, algorithms=['RS256'], audience=GOOGLE_CLIENT_ID)

    #     # Extract user info (like email) from the decoded token for further processing
    #     email = decoded_token['email']
        
    #     # Now, you can either create a new user in your database using the email
    #     # or retrieve the details of an existing user and maybe generate a new JWT for your own app, etc.

    #     return jsonify(success=True, message="User logged in successfully!", email=email)
        
    # except Exception as e:
    #     return jsonify(success=False, message="Invalid token"), 401