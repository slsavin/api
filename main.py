import json
import jwt
import datetime
from functools import wraps
from sanic import Sanic, response


SECRET_KEY = "hkBxrbZ9Td4QEwgRewV6gZSVH4q78vBia4GBYuqd09SsiMsIjH"
FAKE_DB = {
    'fake_user1': 'fake_password1',
    'fake_user2': 'fake_password2'
}

app = Sanic('normalize_app')


def token_required(f):
    @wraps(f)
    def inner(request):
        token = request.json.get('token')
        if not token:
            return response.text('Missing token', status=500)

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception as e:
            return response.text('Invalid token', status=500)

        return f(request)

    return inner


@app.route('/login', methods=['POST'])
def login(request):
    username = request.json.get('username')
    password = request.json.get('password')

    if username in FAKE_DB and FAKE_DB[username] == password:
        token = jwt.encode(
            {
                'user': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return response.json({'token': token})

    return response.text('Invalid login', status=500)


@app.route('/normalize', methods=['POST'])
@token_required
def normalize_post(request):
    try:
        data = request.json.get('data')
        resp = {
            item['name']: [v for k, v in item.items() if 'val' in k.lower()][0] for item in data
        }
        return response.json(resp, status=200)
    except Exception as e:
        return response.text(f'Error: {repr(e)}', status=500)


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8000, debug=True)
