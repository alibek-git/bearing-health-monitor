# Demo dashboard image. Build from the REPO ROOT (it needs analysis/):
#   docker build -f demo/Dockerfile -t bearing-demo .
#   docker run --rm -p 8000:8000 bearing-demo
# then open http://localhost:8000
FROM python:3.12-slim

WORKDIR /app
COPY demo/requirements.txt /tmp/req.txt
RUN pip install --no-cache-dir -r /tmp/req.txt

COPY analysis/ analysis/
COPY demo/ demo/

EXPOSE 8000
CMD ["uvicorn", "demo.app:app", "--host", "0.0.0.0", "--port", "8000"]
