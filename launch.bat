@echo off
:: this tells Flask we want to run the built-in server in dev mode
set FLASK_ENV=development
:: make sure to use a very long random string here that cannot be guessed
set SECRET_KEY=RGVlcCBDYWRlbmNlIC0gTmFtZSBQcm9udW5jaWF0aW9uIFRvb2w=
:: this is the same Org URL found on your developer dashboard
:: for example, https://dev-860408.oktapreview.com
set OKTA_ORG_URL=dev-00396574.okta.com
:: this is the API authentication token we created
set OKTA_AUTH_TOKEN=00zLzDNBpo5g-Z4Q_xMfTw8_UobhmJ0B0BJ-ZrZyGU
:: set API key
:: set OKTA_API_KEY=00u51gn8jaDVWzhpe5d7
:: sets the entry point for flaskapp
set FLASK_APP=main.py
:: runs the app on port 8080
set FLASK_RUN_PORT=8080
:: run the flaskapp
python main.py