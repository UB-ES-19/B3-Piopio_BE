# B3-Piopio_BE

# Installation guidelines
## MySQL:

- Using MySQL database: http://www.marinamele.com/taskbuster-django-tutorial/install-and-configure-mysql-for-django
- Change the database settings for your user, password and database.
- Linux problems: https://stackoverflow.com/questions/7475223/mysql-config-not-found-when-installing-mysqldb-python-interface

## Conda environment
- Conda environment creation with: conda env create -f environment.yml

## API calls

### Tokens
- <b>Get access and refresh token</b>: 

```
POST /api/token/ 
Host: localhost:8000
Content-Type: application/json
Accept: application/json

{
    "username": "<email or username>",
    "password": "pass"
}
```
Response
```
Status: 200 OK
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU3MDM2NTY2MiwianRpIjoiMTQ0MDY0ZDFmOTgwNGYwMzlmODhhODViZTcwOTA1OTUiLCJ1c2VyX2lkIjoxfQ.7DSOmCHvX9h0YNANFVZ0tyyoMfcX58psvePhpzOo5Oo",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTcwMjc5NTYyLCJqdGkiOiIyMTc3YzNhY2I4Yjk0ZTFmYWY5Nzk3Yzg2NTFmZDdmYSIsInVzZXJfaWQiOjF9.2dv4JQKawTNsUb0jKyie5fWyQ-RhYfWdylh5dNmTLxI"
}
```

- <b> Refresh access token </b>:

```
POST /api/token/refresh/
Host: localhost:8000
Content-Type: application/json
Accept: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTU3MDM2NTY2MiwianRpIjoiMTQ0MDY0ZDFmOTgwNGYwMzlmODhhODViZTcwOTA1OTUiLCJ1c2VyX2lkIjoxfQ.7DSOmCHvX9h0YNANFVZ0tyyoMfcX58psvePhpzOo5Oo"
}
```

Response

```
Status: 200 OK
Content-Type: application/json

{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNTcwMjc5OTA4LCJqdGkiOiIxYTEwNDRkM2E0YjY0YmI0OGJhYzE4Y2RmYmJmMWRiMSIsInVzZXJfaWQiOjF9.Rdt8lJdEFdz-4-rN-ziPYj2L58pdYlAWh6YevluGM94"
}
```

## Users
#### List Users:
```
GET /api/users/
Host: localhost:8000
Content-Type: application/json
```
Response
```
Status: 200 OK
Content-Type: application/json
[
    {
        "id": 1,
        "username": "test",
        "email": "user@test.com",
        "profile": {
            "first_name": "test",
            "last_name": "test"
        }
    },
    {
        "id": 2,
    ...
]
```
#### Get User:
```
GET /api/users/<id or username>/
Host: localhost:8000
Content-Type: application/json
```
Response
```
Status: 200 OK
Content-Type: application/json

{
    "id": 2,
    "username": "test",
    "email": "test@test.com",
    "profile": {
        "first_name": "test",
        "last_name": "test"
    }
}
```
```
Status: 404 Not Found
Content-Type: application/json

{
    "detail": "User Not Found"
}
```

#### Create User:

```
POST /api/users/
Host: localhost:8000
Content-Type: application/json
Accept: application/json

{
    "username": "user",
    "email": "user@mail.com",
    "password": "pass1234",
    "confirm_password": "pass1234",
    "profile": {
        "first_name": "user",
        "last_name": "user"
    }
}
```
Response

```
Status: 201 Created
Content-Type: application/json

{
    "id": 2,
    "username": "user",
    "email": "user@mail.com",
    "profile": {
        "first_name": "user",
        "last_name": "user"
    }
}
```
```
Status: 400 Bad Request
Content-Type: application/json

{
    "username": [
        "user with this username already exists."
    ],
    "email": [
        "user with this email already exists."
    ],
    "profile": {
        "first_name": [
            "This field is required."
        ],
        "last_name": [
            "This field is required."
        ]
    },
    "password": [
        "This password is too short. It must contain at least 8 characters.",
        "This password is too common."
    ]
}
```
#### Edit User:

```
POST /api/users/<id>/
Host: localhost:8000
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access token>

{
    "username": "test",
    "email": "user@mail.com",
    "profile": {
        "first_name": "cool",
        "last_name": "name"
    }
}
```

Response
```
Status: 200 OK
Content-Type: application/json

{
    "id": <id>,
    "username": "test",
    "email": "user@mail.com",
    "profile": {
        "first_name": "cool",
        "last_name": "name"
    }
}
```
```
Status: 403 Forbidden
Content-Type: application/json

{
    "detail": "You are not the owner of this user profile."
}
```
