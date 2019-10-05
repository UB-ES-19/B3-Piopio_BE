# B3-Piopio_BE

# Installation guidelines
## MySQL:

- Using MySQL database: http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-mysql-for-django
- Change the database settings for your user, password and database.
- Linux problems: https://stackoverflow.com/questions/7475223/mysql-config-not-found-when-installing-mysqldb-python-interface

## Conda environment
- Conda environment creation with: conda env create -f environment.yml

# API calls

## Tokens
- <b>Get access and refresh token</b>: 

REQUEST:

POST api/token/
\
{\
    "email": "pepe@gmail.com",\
	"password": "pepePEPE1"\
} 

RESPONSE:
\
{\
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU3MDM2NTY2MiwianRpIjoiMTQ0MDY0ZDFmOTgwNGYwMzlmODhhODViZTcwOTA1OTUiLCJ1c2VyX2lkIjoxfQ.7DSOmCHvX9h0YNANFVZ0tyyoMfcX58psvePhpzOo5Oo",\
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTcwMjc5NTYyLCJqdGkiOiIyMTc3YzNhY2I4Yjk0ZTFmYWY5Nzk3Yzg2NTFmZDdmYSIsInVzZXJfaWQiOjF9.2dv4JQKawTNsUb0jKyie5fWyQ-RhYfWdylh5dNmTLxI"
}

- <b> Refresh access token </b>:

REQUEST:
\
POST api/token/refresh/
\
{\
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU3MDM2NTY2MiwianRpIjoiMTQ0MDY0ZDFmOTgwNGYwMzlmODhhODViZTcwOTA1OTUiLCJ1c2VyX2lkIjoxfQ.7DSOmCHvX9h0YNANFVZ0tyyoMfcX58psvePhpzOo5Oo"\
}

RESPONSE:
\
{\
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTcwMjc5OTA4LCJqdGkiOiIxYTEwNDRkM2E0YjY0YmI0OGJhYzE4Y2RmYmJmMWRiMSIsInVzZXJfaWQiOjF9.Rdt8lJdEFdz-4-rN-ziPYj2L58pdYlAWh6YevluGM94"\
}

## Users

- <b> Create User </b>:

REQUEST:
\
POST api/users/
\
{\
    "username": "test",\
    "email": "test@test.com",\
    "password": "Test1234@@@@",\
    "confirm_password": "Test1234@@@@",\
    "profile": {\
        "first_name": "Antonio",\
         "last_name": "Pepo"\
    }\
}

RESPONSE:
\
Errors or all the data passed to the user registration besides the password.

...