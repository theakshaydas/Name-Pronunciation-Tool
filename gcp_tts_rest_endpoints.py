import sys
import os
from flask import request , Response, jsonify
from flask_restful import Resource, Api
from flask_api import status
from re import fullmatch
from flasgger import Swagger, swag_from

from __main__ import app
from gcp_tts_calls import *
import main_tts_calls

swagger = Swagger(app)

@app.route("/api/standard/pronounce",methods=['GET'])
@swag_from('static/swagger_docs/get_standard_recording_api.yaml')
def get_standard_recording_api():
    if "name" not in request.args:
        return "Bad Request: Name field not given", status.HTTP_400_BAD_REQUEST
    name=request.args.get("name").replace("\"","")
    voice_name = None
    if "voice" in request.args:
        voice_name=request.args.get('voice').replace("\"","")
        if voice_name not in list_all_voices():
            return "Bad Request: Enter a valid voice name, you can get valid voice names from /api/get_voices", status.HTTP_400_BAD_REQUEST
    pitch,speed=0.0,1.0
    if "pitch" in request.args:
        try: 
            pitch=float(request.args.get('pitch'))
            if pitch<-20.0 or pitch >20.0:
                raise Exception("Not in range")
        except:
            return "Bad Request: Enter a valid pitch value [-20.0,20.0]", status.HTTP_400_BAD_REQUEST
    if "speed" in request.args:
        try:
            speed=float(request.args.get('speed'))
            if speed<0.25 or speed >4.0:
                raise Exception("Not in range")
        except:
            return "Bad Request: Enter a valid speed value [0.25,4.0]", status.HTTP_400_BAD_REQUEST
    
    return Response(text_to_wav(name,voice_name,pitch,speed),mimetype="audio/wav")

@app.route("/api/pronounce",methods=['GET'])
@swag_from('static/swagger_docs/get_recording_api.yaml')
def get_recording_api():
    if "name" not in request.args:
        return "Bad Request: Name field not given", status.HTTP_400_BAD_REQUEST
    name=request.args.get("name").replace("\"","")
    result=main_tts_calls.get_recording(name)
    email_id=request.args.get("email")
    if len(result)>1:
        if email_id:
            email_id=email_id.lower()
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not fullmatch(regex,email_id):
                return "Bad Request: Enter a valid email id", status.HTTP_400_BAD_REQUEST
            for i in result:
                if i["email_id"]==email_id:
                    return Response(i["audio"],mimetype="audio/wav")
            return "Bad Request: No valid record with given email id", status.HTTP_400_BAD_REQUEST
        else:
            popped_audios=[]
            for i in result:
                popped_audios.append(i.pop("audio"))
            for i in popped_audios:
                if i:
                    return jsonify({'listed_users': result})
            return Response(result[0]["audio"],mimetype="audio/wav")
    elif len(result)==1:
        if result[0]["email_id"]==email_id and email_id:
            return Response(result[0]["audio"],mimetype="audio/wav")
        if not email_id:
            return Response(result[0]["audio"],mimetype="audio/wav")
        else:
            return "Bad Request: No valid record with given email id", status.HTTP_400_BAD_REQUEST
    else:
        return Response(text_to_wav(name),mimetype="audio/wav")

@app.route("/api/get_language_codes",methods=['GET'])
@swag_from('static/swagger_docs/get_languages_api.yaml')
def get_languages_api():
    return jsonify({'language_codes':list_languages()})

@app.route("/api/get_voices",methods=['GET'])
@swag_from('static/swagger_docs/get_voices_api.yaml')
def get_voices_api():
    if "language_code" not in request.args:
        return jsonify({'voices':[list_all_voices()]})
    language=request.args.get("language_code")
    if language not in list_languages():
        return "Bad Request: The language_code given is not valid", status.HTTP_400_BAD_REQUEST
    if "gender" not in request.args:
        return jsonify({'voices':[list_all_voices(language)]})
    gender=request.args.get("gender")
    if gender not in ["MALE","FEMALE"]:
        return "Bad Request: The gender should be one of MALE or FEMALE", status.HTTP_400_BAD_REQUEST
    return jsonify({'voices':list_voices(language,gender)})

@app.route("/api/save_preferences",methods=['PUT'])
@swag_from('static/swagger_docs/save_preferences_api.yaml')
def save_preferences_api():
    if "name" not in request.form or "email" not in request.form or "voice" not in request.form or "password" not in request.form:
        return "Bad Request: One/many of compulsory fields (Name,email,voice,password) is not given", status.HTTP_400_BAD_REQUEST
    name=request.form.get("name").replace("\"","")
    email_id=request.form.get('email').lower()
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex,email_id):
        return "Bad Request: Enter a valid email id", status.HTTP_400_BAD_REQUEST
    password=request.form.get("password")
    if not main_tts_calls.authenticate(email_id,password,name)[0]:
        return "Unauthorized: The entered email id or password or name is incorrect", status.HTTP_401_UNAUTHORIZED
    voice=request.form.get('voice')
    if voice not in list_all_voices():
            return "Bad Request: Enter a valid voice name, you can get valid voice names from /api/get_voices", status.HTTP_400_BAD_REQUEST
    pitch,speed=0.0,1.0
    if "pitch" in request.form:
        pitch=float(request.form.get("pitch"))
        if pitch<-2.0 or pitch > 2.0:
            return "Bad Request: Enter a valid pitch value in the range [-2.0,2.0]", status.HTTP_400_BAD_REQUEST
    if "speed" in request.form:
        speed=float(request.form.get("speed"))
        if speed<0.25 or speed > 4.0:
            return "Bad Request: Enter a valid speed value in the range [0.25,4.0]", status.HTTP_400_BAD_REQUEST
    preferred_name=request.form.get("preferred_name")
    if preferred_name:
        if main_tts_calls.save_preferences(name,email_id,voice,speed,pitch,preferred_name) == 0:
            return "Successfully saved preferences!", status.HTTP_200_OK
    if main_tts_calls.save_preferences(name,email_id,voice,speed,pitch) == 0:
            return "Successfully saved preferences!", status.HTTP_200_OK


@app.route("/api/save_custom_recording",methods=['PUT'])
@swag_from('static/swagger_docs/save_recording_api.yaml')
def save_recording_api():
    if "name" not in request.form or "email" not in request.form or "password" not in request.form or "recording" not in request.files:
        return "Bad Request: One/many of compulsory fields (Name,email,password,audio file) is not given", status.HTTP_400_BAD_REQUEST
    name=request.form.get("name").replace("\"","")
    email_id=request.form.get('email').lower()
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex,email_id):
        return "Bad Request: Enter a valid email id", status.HTTP_400_BAD_REQUEST
    password=request.form.get("password")
    if not main_tts_calls.authenticate(email_id,password,name)[0]:
        return "Unauthorized: The entered email id or password or name is incorrect", status.HTTP_401_UNAUTHORIZED
    audio=request.files["recording"]
    audio.save(audio.filename)
    with open(audio.filename,'rb') as f:
        audio_file=f.read()
    os.remove(audio.filename)
    preferred_name=request.form.get("preferred_name")
    if preferred_name:
        if main_tts_calls.save_recordings(name,email_id,audio_file,preferred_name) == 0:
            return "Successfully saved recording!", status.HTTP_200_OK
    if main_tts_calls.save_recordings(name,email_id,audio_file) == 0:
            return "Successfully saved custom recording!", status.HTTP_200_OK

@app.route("/api/delete_custom_recording",methods=['DELETE'])
@swag_from('static/swagger_docs/delete_custom_recording.yaml')
def delete_custom_recording():
    if "name" not in request.form or "email" not in request.form or "password" not in request.form:
        return "Bad Request: One/many of compulsory fields (Name,email,password,audio file) is not given", status.HTTP_400_BAD_REQUEST
    name=request.form.get("name").replace("\"","")
    email_id=request.form.get('email').lower()
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex,email_id):
        return "Bad Request: Enter a valid email id", status.HTTP_400_BAD_REQUEST
    password=request.form.get("password")
    if not main_tts_calls.authenticate(email_id,password,name)[0]:
        return "Unauthorized: The entered email id or password or name is incorrect", status.HTTP_401_UNAUTHORIZED
    main_tts_calls.delete_recording(email_id)
    return "Successfully deleted custom_recording"

@app.route('/api/opt_out',methods=['DELETE'])
@swag_from('static/swagger_docs/delete_user.yaml')
def delete_user():
    if "name" not in request.form or "email" not in request.form or "password" not in request.form:
        return "Bad Request: One/many of compulsory fields (Name,email,password,audio file) is not given", status.HTTP_400_BAD_REQUEST
    name=request.form.get("name").replace("\"","")
    email_id=request.form.get('email').lower()
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not fullmatch(regex,email_id):
        return "Bad Request: Enter a valid email id", status.HTTP_400_BAD_REQUEST
    password=request.form.get("password")
    if not main_tts_calls.authenticate(email_id,password,name)[0]:
        return "Unauthorized: The entered email id or password or name is incorrect", status.HTTP_401_UNAUTHORIZED
    if main_tts_calls.delete_user(email_id):
        return "Successfully opted-out from the service, if you want to opt in contact the administrator!"

#Only for ADMIN
@app.route("/api/get_embed_code",methods=['POST'])
@swag_from('static/swagger_docs/get_embed_url.yaml')
def get_embed_url():
    if "name" not in request.form or "admin_email" not in request.form or "admin_password" not in request.form:
        return "Bad Request: One/many of compulsory fields (Name,admin_email,admin_password) is not given", status.HTTP_400_BAD_REQUEST
    name=request.form.get("name").replace("\"","")
    admin_email_id=request.form.get('admin_email').lower()
    admin_password=request.form.get('admin_password')
    user_email_id=request.form.get('user_email')
    if main_tts_calls.authenticate(admin_email_id, admin_password)[0]:
        if user_email_id:
            user_email_id=user_email_id.lower()
            return f"<audio controls src=\"http://localhost:8080/api/pronounce?name='{name}'&email='{user_email_id}'\"></audio>"
        else:
            return f"<audio controls src=\"http://localhost:8080/api/pronounce?name='{name}'\"></audio>"
    else:
        return "Unauthorized: The entered admin email id or password is incorrect", status.HTTP_401_UNAUTHORIZED

#Only for ADMIN ( INTERNAL USE ONLY )
@app.route("/api/add_user",methods=['PUT'])
@swag_from('static/swagger_docs/add_user.yaml')
def add_user():
    if "user_name" not in request.form or "admin_email" not in request.form or "admin_password" not in request.form or 'user_email' not in request.form or 'user_password' not in request.form:
        return "Bad Request: One/many of compulsory fields (Name,admin_email,admin_password,user_email,user_password) is not given", status.HTTP_400_BAD_REQUEST
    name=request.form.get('user_name')
    email_id=request.form.get('user_email').lower()
    password=request.form.get('user_password')
    admin_email=request.form.get('admin_email').lower()
    admin_password=request.form.get('admin_password')
    if main_tts_calls.authenticate(admin_email,admin_password)[0]:
        if main_tts_calls.check_user_presence(email_id):
            return "Bad Request: The given user is already present!", status.HTTP_400_BAD_REQUEST
        main_tts_calls.personadd(name,email_id,password)
        return f"Successfully created user with name {name}", status.HTTP_201_CREATED
    else:
        return "Unauthorized: The entered admin email id or password or name is incorrect", status.HTTP_401_UNAUTHORIZED
