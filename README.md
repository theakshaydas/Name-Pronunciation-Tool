# Name-Pronounciation-Tool
This project uses GCP's Text-to-Speech APIs and the power of python and FLASK to correctly pronounce your name! Crazy right!

# API Documentation

The documentation for the API can be accessed with the link below. This was
done to ensure that the documentation is interactive and can be directly used
by the user.

Publicly accesible Link:
https://documenter.getpostman.com/view/20992626/UyxjH6ec

# Instructions to deploying the following application to GCP

The instructions to deploy to GCP are given in the pdf Documentation/playbook.pdf in the repository.

# Instructions to run the app in your local machine

1. Checkout the code from github to your local machine.
2. Download the two json files which correspond to the GCP and cloud sql postgres credentials into the directory of the downloaded code.
3. URL to download can be found in the pdf file in the link : https://drive.google.com/file/d/1ok6oTpE8s1sZMeG1RN0absPaJWdBNV5j/view?usp=sharing
5. create a virtual environment of python the directory of the repository in local with the command:
      python -m venv venv
4. Activate the virtual environment by running the activate executable like this:
    Windows: venv\Scripts\activate.bat  MacOS: venv/bin/activate
5. Install all dependencies using pip install -r requirements.txt
6. Now you can run the main.py file using "python main.py"
7. And the application main page will be accesible in localhost:8080/
8. REST api endpoints can be obtained from the documentation link above.
