FROM python:3.11.5
ENV PYTHONUNBUFFERED 1
COPY requirements.txt  /workdir/requirements.txt
RUN apt-get update
RUN apt-get install sudo -y build-essential \
    python3-pip \
    python3-dev 
RUN pip install --no-cache-dir -r /workdir/requirements.txt
RUN apt-get clean
COPY ./  /workdir/
WORKDIR /workdir

# Run the applicatio
CMD ["EXPOSE", "4666"]
CMD ["python3", "main.py"]
