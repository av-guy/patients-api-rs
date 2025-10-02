FROM python:3.12-slim

LABEL maintainer="av-guy"

WORKDIR /patients_api
COPY . /patients_api
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "patients_api.main:app", "host", "0.0.0.0", "--port", "8000"]

