#!/bin/bash
# Script to fix opentelemetry package versions for compatibility

pip install opentelemetry-api==1.31.1
pip install opentelemetry-sdk==1.31.1
pip install opentelemetry-exporter-otlp-proto-common==1.36.0
pip install opentelemetry-exporter-otlp-proto-grpc==1.36.0
pip install opentelemetry-instrumentation==0.52b1
pip install opentelemetry-instrumentation-aiohttp-client==0.52b1
pip install opentelemetry-instrumentation-asgi==0.52b1
pip install opentelemetry-instrumentation-dbapi==0.52b1
pip install opentelemetry-instrumentation-django==0.52b1
pip install opentelemetry-instrumentation-fastapi==0.52b1
pip install opentelemetry-instrumentation-flask==0.52b1
pip install opentelemetry-instrumentation-httpx==0.52b1
pip install opentelemetry-instrumentation-openai==0.39.0
pip install opentelemetry-instrumentation-psycopg2==0.52b1
pip install opentelemetry-instrumentation-requests==0.52b1
pip install opentelemetry-instrumentation-urllib==0.52b1
pip install opentelemetry-instrumentation-urllib3==0.52b1
pip install opentelemetry-instrumentation-wsgi==0.52b1
pip install opentelemetry-proto==1.36.0
pip install opentelemetry-resource-detector-azure==0.1.5
pip install opentelemetry-semantic-conventions==0.52b1
pip install opentelemetry-semantic-conventions-ai==0.4.3
pip install opentelemetry-util-http==0.52b1
