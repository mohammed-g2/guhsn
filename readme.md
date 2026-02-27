
### Testing Emails
- edit environment variables: in ".env" file
```
# Mail config
MAIL_SERVER="127.0.0.1"
MAIL_PORT=1025
MAIL_USE_TLS=0
MAIL_USERNAME=
MAIL_PASSWORD=
```

- run python testing email server
```
cd app/scripts
python mail_server.py
```