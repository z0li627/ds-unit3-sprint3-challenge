"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import openaq

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)
DB.init_app(APP)

api = openaq.OpenAQ()
status, body = api.measurements(city='Los Angeles', parameter='pm25')
date_value = []

def request_data(i):
  templist = body['results'][i]
  return templist

def get_nested(data, *args):
    if args and data:
        element  = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nested(value, *args[1:])

def addtolist(date_value):
  for i in range(0, 99, 1):
    templist2 = request_data(i)
    date_value.append(get_nested(templist2, "date", "utc"))
    date_value.append(get_nested(templist2, "value"))
    i += 1
  return date_value


@APP.route('/')
def root():
    """Base view."""
    addtolist(date_value)
    return str(date_value)

@APP.route('/save')
def savedb():
    """Saving values to the DB"""
    for i in range(0, 99, 1):
        alpha = date_value[i]
        i += 1
        beta = date_value[i]
        i += 1
        DB.session.add(Record(datetime=alpha, value=beta))
    #date_value1 = date_value[0::2]
    #date_value2 = [float(i) for i in date_value[1::2]]
    #date_value2 = str(date_value[1::2]) ...value=date_value2
    #DB.session.add(Record(datetime=date_value1))
    DB.session.commit()
    return "Saved"


class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return {'Date: ':self.datetime, 'Value: ':self.value}


@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    date_value = []
    addtolist(date_value)
    savedb()
    DB.session.commit()
    return 'Data refreshed!'
