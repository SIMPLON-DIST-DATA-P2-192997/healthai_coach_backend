FROM python:3.12-slim

WORKDIR /app

COPY admin_interface/requirements.txt admin_interface/requirements.txt
RUN pip install --no-cache-dir -r admin_interface/requirements.txt

COPY admin_interface/ admin_interface/

ENV GRADIO_SERVER_NAME=0.0.0.0
EXPOSE 7860

CMD ["python", "-m", "admin_interface.app_gradio"]
