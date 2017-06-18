from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app, resources={r"/peers/*": {"origins": "*"}})

peers = []
i = 0


@cross_origin()
@app.route('/peers', methods=['GET', 'POST'])
def handle():
    global i

    if request.method == 'POST':
        i += 1
        body = dict(id=i)
        peers.append(i)
        status = 201
    else:
        body = peers
        status = 200

    return jsonify(body), status


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
