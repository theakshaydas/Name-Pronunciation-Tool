import base64
import io
from msilib.schema import File
import unittest

import werkzeug
import main_tts_calls
import gcp_tts_calls
from __main__ import app

class TestClass(unittest.TestCase):
    def test_get_language_codes(self):
        print("\nExecuting test_get_language_codes()..")
        tester=app.test_client(self)
        assert tester.get("/api/get_language_codes").status_code == 200
        print("test_get_language_codes() test successful!\n")

    def test_get_voices(self):
        print("Executing test_get_voices()..")
        tester=app.test_client(self)
        assert tester.get("/api/get_voices").status_code == 200
        assert tester.get("/api/get_voices?language_code=en-IN").status_code == 200
        assert tester.get("/api/get_voices?language_code=en-IN&gender=MALE").status_code ==200
        assert tester.get("/api/get_voices?language_code=en").status_code == 400
        assert tester.get("/api/get_voices?language_code=en-IN&gender=NOTRIGHT").status_code == 400
        print("test_get_voices() test successful!\n")

    def test_get_recording(self):
        print("Executing test_get_recording()..")
        tester=app.test_client(self)
        assert tester.get("/api/pronounce?name=admin").status_code == 200
        assert tester.get("/api/pronounce?name=习近平").status_code == 200
        assert tester.get("/api/pronounce?name=admin&email=admin@gmail.com").status_code == 200
        assert tester.get("/api/pronounce?name=admin&email=admin@yahoo.com").status_code == 400
        assert tester.get("/api/pronounce?name=admin&email=admin@gmail").status_code == 400
        print("test_get_recording() test successful!\n")

    def test_get_standard_recording(self):
        print("Executing test_get_standard_recording()..")
        tester=app.test_client(self)
        assert tester.get("/api/standard/pronounce?name=admin").status_code == 200
        assert tester.get("/api/standard/pronounce?name=Karthik Peddi&voice=en-IN-Wavenet-B&speed=0.25&pitch=1.5").status_code == 200
        assert tester.get("/api/standard/pronounce?name=Karthik Peddi&voice=en-IN-Wavenet&speed=0.25&pitch=1.5").status_code == 400
        assert tester.get("/api/standard/pronounce?name=Karthik Peddi&voice=en-IN-Wavenet-B&speed=4.2&pitch=1.5").status_code == 400
        assert tester.get("/api/standard/pronounce?name=Karthik Peddi&voice=en-IN-Wavenet-X&speed=0.25&pitch=3.0").status_code == 400
        print("test_get_standard_recording() test successful!\n")

    def test_save_preferences(self):
        print("Executing test_save_preferences()..")
        tester,name,email_id,password,voice,speed,pitch=app.test_client(self),"admin","admin@gmail.com","H@ckathon22","en-IN-Wavenet-B","2.0","0.5"
        invalid_email="admin@yahoo.com"
        invalid_speed="-0.2"
        invalid_pitch="-23.0"
        invalid_pass="Hello2321@"
        invalid_voice="Invalid voice_code"
        assert tester.put("/api/save_preferences",data=dict(
            name=name,email=email_id,password=password,voice=voice,speed=speed,pitch=pitch
        )).status_code==200
        assert tester.put("/api/save_preferences",data=dict(
            name=name,email=invalid_email,password=password,voice=voice,speed=speed,pitch=pitch
        )).status_code == 401
        assert tester.put("/api/save_preferences",data=dict(
            name=name,email=email_id,password=password,voice=invalid_voice,speed=speed,pitch=pitch
        )).status_code == 400
        assert tester.put("/api/save_preferences",data=dict(
            name=name,email=email_id,password=password,voice=voice,speed=invalid_speed,pitch=pitch
        )).status_code == 400
        assert tester.put("/api/save_preferences",data=dict(
            name=name,email=email_id,password=password,voice=voice,speed=speed,pitch=invalid_pitch
        )).status_code == 400
        assert tester.put("/api/save_preferences",data=dict(
            name=name,email=email_id,password=invalid_pass,voice=voice,speed=speed,pitch=invalid_pitch
        )).status_code == 401
        print("test_save_preferences() test successful!\n")

def run_tests():
    testclass=TestClass()
    testclass.test_get_language_codes()
    testclass.test_get_voices()
    testclass.test_get_recording()
    testclass.test_get_standard_recording()
    testclass.test_save_preferences()
    print("Executed 5/5 test all tests successful!")

