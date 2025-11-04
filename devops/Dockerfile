FROM python:3.11.5
ENV PYTHONUNBUFFERED 1
COPY requirements.txt config.yaml setup.py /workdir/

RUN apt-get update
RUN apt-get install sudo -y build-essential \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx
RUN pip install --no-cache-dir -r /workdir/requirements.txt
RUN apt-get clean
COPY app/ /workdir/app/
COPY ml/ /workdir/ml/

WORKDIR /workdir

CMD ["EXPOSE", "1736"]
# Run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "1736"]
