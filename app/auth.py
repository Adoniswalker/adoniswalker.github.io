import datetime
import jwt

from app import app, db


def check_user_in_db(account_id):
    try:
        account_id = int(account_id)
        user_query = "select account_id from users where account_id = {}".format(account_id)
        if db.qry(user_query, fetch="one"):
            return True
    except ValueError:
        return account_id


def jwt_required(f):
    """ Ensure jwt token is provided and valid
        :param f: function to decorated
        :return: decorated function
    """
    try:
        auth_header = f['Authorization'].split(' ')[-1]
    except Exception as e:
        print(e)
        return "Unauthorized. Please login {}".format(e)
    decode_result = decode_auth_token(auth_header)
    if not check_user_in_db(decode_result):
        return "User not found. Kindly register"
    return decode_result


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3, seconds=5),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        return e


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, app.config['SECRET_KEY'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
