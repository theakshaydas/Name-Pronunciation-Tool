import os
from flask import Flask

app = Flask(__name__)

import gcp_tts_rest_endpoints
import main_tts_calls
import flask_app
# from test_suite import run_tests


if __name__ == "__main__":
    # run_tests()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

