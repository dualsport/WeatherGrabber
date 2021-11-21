FROM python:3.6-alpine

WORKDIR /app

COPY WeatherGrabber.py /app
COPY settings.py /app
COPY requirements.txt /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python", "-u", "WeatherGrabber.py"]