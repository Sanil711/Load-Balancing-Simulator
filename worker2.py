# worker2.py
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/process', methods=['GET'])
def process():
    return jsonify({"message": "Handled by Worker 2"}), 200


if __name__ == '__main__':
    app.run(port=5002)
