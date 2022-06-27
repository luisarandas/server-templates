:: @echo off
SET FLASK_APP=app
SET FLASK_ENV=development
flask run --no-debugger
:: pause
:: open -> http://127.0.0.1:5000/