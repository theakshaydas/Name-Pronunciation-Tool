import sys
import os
import psycopg2
from sqlalchemy import create_engine, MetaData, Table, Column, Numeric, Integer, VARCHAR, func
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import json, re
from flask_sqlalchemy import SQLAlchemy

import gcp_tts_calls
from __main__ import app

f=open('involuted-ratio-349909-e81ee1f59eab.json')
cred = json.load(f)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(cred)

f1=open('postgres_authentication.json')
db_details=json.load(f1)
cloud_sql_instance_name = db_details['cloud_sql_instance_name']


# configuration
app.config["SECRET_KEY"] = "postgres"
app.config["SQLALCHEMY_DATABASE_URI"]= f"postgresql+psycopg2://{db_details['db_user']}:{db_details['db_password']}@{db_details['public_ip']}/{db_details['db_name']}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

db = SQLAlchemy(app)

bucket_name = 'custom_audio'
client = storage.Client(credentials=credentials, project='name-pronounciation-tool')
# client = storage.Client(project='name-pronounciation-tool')
bucket = client.get_bucket(bucket_name)


# Uploads a given filename from local machine
def upload_to_bucket(file_name):
    blob = bucket.blob(file_name)  # filename that will be saved
    blob.upload_from_filename(file_name)
    return 0


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email_id = db.Column(db.String(80), nullable=False)
    audio = db.Column(db.String(150), nullable=True)
    preferred_name = db.Column(db.String(30), nullable=True)
    password = db.Column(db.String(30), nullable=True)

    def __init(self, name, email_id, password):
        self.name = name
        self.email_id = email_id
        self.password = password

    def __init__(self, name, email_id, password, audio=None, preferred_name=None):
        self.name = name
        self.email_id = email_id
        self.audio = audio
        self.preferred_name = preferred_name
        self.password = password


# Can be removed
# Internal Use Only
def personadd(name, email_id, password):
    email_id = email_id.lower()
    entry = People(name, email_id, password)
    db.session.add(entry)
    db.session.commit()
    return 0


# Preferences can be given to be saved required name, email_id,voice,speed,pitch and preferred name is optional if already present in db not overwritten with None if not provided dont worry.
def save_preferences(name, email_id, voice, speed, pitch, preferred_name=str()):
    if preferred_name:
        audio_file_byte = gcp_tts_calls.text_to_wav(preferred_name, voice, pitch, speed)
    else:
        audio_file_byte = gcp_tts_calls.text_to_wav(name, voice, pitch, speed)
    result = People.query.filter_by(email_id=email_id).first()
    person_id = result.id
    filename = f"{person_id}.wav"
    with open(filename, "wb") as f:
        f.write(audio_file_byte)
    upload_to_bucket(filename)
    os.remove(filename)
    result.audio = filename
    result.preferred_name = preferred_name
    db.session.commit()
    return 0


# The audio file should be given in bytes form and if preferred name is entered can be given as well else will be None if not already present in database. Required -- audio,name,email_id
def save_recordings(name, email_id, audio_file, preferred_name=str()):
    result = People.query.filter_by(email_id=email_id).first()
    person_id = result.id
    filename = f"{person_id}.wav"
    with open(filename, "wb") as f:
        f.write(audio_file)
    upload_to_bucket(filename)
    os.remove(filename)
    result.audio = filename
    result.preferred_name = preferred_name
    db.session.commit()
    return 0


def get_all_user():
    result = People.query.filter_by().all()
    if len(result) >= 1:
        search_results = [
            {"name": p.name, "email_id": p.email_id, "preferred_name": p.preferred_name or "",
             "password": p.password, "audio": p.audio or ""}
            for p in result]
        return search_results
    else:
        return []


# Akshay -- If an employee is serached then list has atleast one element if non-employee is searched then list will be empty so akshay should call text_to_wav(name)
def get_recording(name):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    result = People.query.filter(func.lower(People.email_id) == func.lower(name)).all() \
        if re.fullmatch(regex, name) else People.query.filter(func.lower(People.name).like(name.lower() + '%')).all()
    if len(result) >= 1:
        search_results = []
        for p in result:
            is_saved = False
            if p.audio:
                file_path_gcp = p.audio
                audio = bucket.get_blob(file_path_gcp)
                audio.download_to_filename('temp.wav')
                with open('temp.wav', 'rb') as f:
                    audio_byte = f.read()
                os.remove('temp.wav')
                is_saved = True
            else:
                audio_byte = gcp_tts_calls.text_to_wav(name)

            dict_people = {"name": p.name, "email_id": p.email_id, "preferred_name": p.preferred_name,
                           "audio": audio_byte, "is_saved": is_saved}
            search_results.append(dict_people)
        return search_results
    # If nothing in database will return [] and Akshay has to call text_to_wav(name) method and not show the table in the UI
    else:
        return []


# Will authenticate if name and password given name is optional but if given will check if it matches with database
def authenticate(email_id, password, name=None):
    if name:
        result = People.query.filter_by(email_id=email_id, password=password).first()
        if result:
            if result.name.lower() == name.lower():
                return True, result.name
            else:
                return False, None
        return False, None
    result = People.query.filter_by(email_id=email_id, password=password).first()
    if result:
        return True, result.name
    return False, None


# After deleting recording thats saved will return preferred name if present else will return name
def delete_recording(email_id):
    result = People.query.filter_by(email_id=email_id).first()
    if result:
        if result.audio:
            try:
                blob = bucket.blob(result.audio)
                blob.delete()
            except:
                pass
            result.audio = None
            db.session.commit()

    if result.preferred_name:
        return result.preferred_name
    return result.name


def delete_user(email_id):
    result = People.query.filter_by(email_id=email_id).first()
    if result:
        db.session.delete(result)
        db.session.commit()
        return True
    return False


def check_user_presence(email_id):
    result = People.query.filter_by(email_id=email_id).first()
    if result:
        return True
    else:
        return False


def get_embed_code(name, user_email_id):
    return f"<audio controls src=\"http://localhost:8080/api/pronounce?name='{name}'&email='{user_email_id}'\"></audio>"
