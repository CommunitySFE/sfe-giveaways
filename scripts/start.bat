@echo off
echo starting flask server
cd ../venv/Scripts
set FLASK_APP=server.serverapp
set FLASK_ENV=development
echo test
flask run