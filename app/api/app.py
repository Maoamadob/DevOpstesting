import os
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["endpoint"]
)


@app.before_request
def before_request():
    request.start_time = time.time()


@app.after_request
def after_request(response):
    if hasattr(request, "start_time"):
        latency = time.time() - request.start_time
        endpoint = request.endpoint or "unknown"
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status=response.status_code
        ).inc()
    return response


@app.route("/health")
def health():
    return jsonify(status="ok", service="api")


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.route("/api/info")
def info():
    return jsonify(
        service="api",
        environment=os.getenv("ENV", "dev"),
        db_host=os.getenv("DB_HOST", "not-configured"),
        message="DevOps Technical Test - Platform Engineer",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
