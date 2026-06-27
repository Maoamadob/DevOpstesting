from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify(status='ok', service='api')

@app.route('/api/info')
def info():
    return jsonify(
        service='api',
        environment=os.getenv('ENV', 'dev'),
        db_host=os.getenv('DB_HOST', 'not-configured'),
        message='DevOps Technical Test - Platform Engineer'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)