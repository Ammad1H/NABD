# NABD app + API image. Build: docker build -t nabd .   (see docker-compose.yml)
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/nabd
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt
# Only what the app needs: code, playbook, contract outputs and cached raw data.
COPY app/ app/
COPY playbook/ playbook/
COPY data/raw/ data/raw/
COPY results/ results/
COPY ledger/ ledger/
RUN mkdir -p app/audit && useradd -m nabd && chown -R nabd /srv/nabd
USER nabd
EXPOSE 8501 8000
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
