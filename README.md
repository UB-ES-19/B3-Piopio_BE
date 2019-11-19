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

## LIKE
#### LIKE&UNLIKE a post:
```
POST /api/users/like/{postId}/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```
Response


```
Status: 201 Created
Content-Type: application/json

{
    "message": "LIKED!"
}
```

```
Status: 201 Created
Content-Type: application/json

{
    "message": "UNLIKED!"
}
```

#### USER'S LIKED POSTS' LIST:
```
POST /api/users/{user_id}/liked/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```

Response
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 8,
            "content": "gagagaga",
            "type": "<text>",
            "media": [
                {
                    "url": "http://..."
                }
            ],
            "user": {
                "id": 2,
                "username": "onebu",
                "email": "onebu@test.com",
                "profile": {
                    "first_name": "Jhon",
                    "last_name": "Ash"
                },
                "following_count": 2,
                "follower_count": 1,
                "followers": [
                    1
                ],
                "following": [
                    1
                ]
            },
            "created_at": "2019-11-18T17:41:53.561843Z"
        },
        {
            "id": 6,
            "content": "hohohoho",
            "type": "<text>",
            "media": [
                {
                    "url": "http://..."
                }
            ],
            "user": {
                "id": 2,
                "username": "onebu",
                "email": "onebu@test.com",
                "profile": {
                    "first_name": "Jhon",
                    "last_name": "Ash"
                },
                "following_count": 2,
                "follower_count": 1,
                "followers": [
                    1
                ],
                "following": [
                    1
                ]
            },
            "created_at": "2019-11-18T17:41:41.767335Z"
        }
    ]
}
```

## RETWEET
#### RETWEET&UNRETWEET a post:
```
POST /api/users/retweet/{postId}/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```
Response


```
Status: 201 Created
Content-Type: application/json

{
    "message": "RETWEETED!"
}
```

```
Status: 201 Created
Content-Type: application/json

{
    "message": "UNRETWEETED!"
}
```

#### USER'S RETWEETED POSTS' LIST:
```
POST /api/users/{user_id}/retweetd/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```

Response
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 8,
            "content": "gagagaga",
            "type": "<text>",
            "media": [
                {
                    "url": "http://..."
                }
            ],
            "user": {
                "id": 2,
                "username": "onebu",
                "email": "onebu@test.com",
                "profile": {
                    "first_name": "Jhon",
                    "last_name": "Ash"
                },
                "following_count": 2,
                "follower_count": 1,
                "followers": [
                    1
                ],
                "following": [
                    1
                ]
            },
            "created_at": "2019-11-18T17:41:53.561843Z"
        },
        {
            "id": 6,
            "content": "hohohoho",
            "type": "<text>",
            "media": [
                {
                    "url": "http://..."
                }
            ],
            "user": {
                "id": 2,
                "username": "onebu",
                "email": "onebu@test.com",
                "profile": {
                    "first_name": "Jhon",
                    "last_name": "Ash"
                },
                "following_count": 2,
                "follower_count": 1,
                "followers": [
                    1
                ],
                "following": [
                    1
                ]
            },
            "created_at": "2019-11-18T17:41:41.767335Z"
        }
    ]
}
```

## Follows
#### List all Followers:
```
GET /api/follows/
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "followers": [
                {
                    "id": 5,
                    "username": "sutikcram"
                }
            ],
            "id": 1,
            "username": "pepe"
        },
        {
            "followers": [],
            "id": 2,
            "username": "antonio"
        },
        {
            "followers": [],
            "id": 3,
            "username": "antonio2"
        },
        {
            "followers": [],
            "id": 4,
            "username": "qwerqwer"
        },
        {
            "followers": [],
            "id": 5,
            "username": "sutikcram"
        }
    ]
}
```

#### List all Followers by id:

```
GET /api/follows/{user_id}
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "username": "sutikcram",
            "email": "sutikcram@gmail.com",
            "profile": {
                "first_name": "marc",
                "last_name": "urgeello"
            },
            "following_count": 0,
            "follower_count": 1
        }
    ]
}
```

#### List all Followings:
```
GET /api/follows/
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "followings": [
                {
                    "id": 5,
                    "username": "sutikcram"
                }
            ],
            "id": 1,
            "username": "pepe"
        },
        {
            "followings": [],
            "id": 2,
            "username": "antonio"
        },
        {
            "followings": [],
            "id": 3,
            "username": "antonio2"
        },
        {
            "followings": [],
            "id": 4,
            "username": "qwerqwer"
        },
        {
            "followings": [],
            "id": 5,
            "username": "sutikcram"
        }
    ]
}
```

#### List all Followings by id:
```
GET /api/followings/{user_id}
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "username": "sutikcram",
            "email": "sutikcram@gmail.com",
            "profile": {
                "first_name": "marc",
                "last_name": "urgeello"
            },
            "following_count": 0,
            "follower_count": 1
        }
    ]
}
```


#### Follow another user:
```
POST /api/users/follow/
Host: localhost:8000
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access token>

{
    "username":"pepe"
}
```

Response
```
HTTP 200 OK
Content-Type: application/json

{
    "username": "Correct"
}
```

```
HTTP 404 Not Found
Content-Type: application/json

{
    "username": "The specified user does not exist"
}
```

#### Unfollow another user:
```
POST /api/users/unfollow/
Host: localhost:8000
Content-Type: application/json
Accept: application/json

{
    "username":"pepe"
}
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "username": "Correct"
}
```

```
HTTP 404 Not Found
Content-Type: application/json

{
    "username": "The specified user does not exist"
}
```

### List user's followers
```
GET /api/users/<user_id>/followers
Host: localhost:8000
Content-Type: application/json
Accept: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "username": "sutikcram",
            "email": "sutikcram@gmail.com",
            "profile": {
                "first_name": "marc",
                "last_name": "urgeello"
            },
            "following_count": 1,
            "follower_count": 2,
            "followers": [
                1,
                6
            ],
            "following": [
                1,
                6
            ]
        }
    ]
}
```

### List user's followings
```
GET /api/users/<user_id>/followings
Host: localhost:8000
Content-Type: application/json
Accept: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "username": "sutikcram",
            "email": "sutikcram@gmail.com",
            "profile": {
                "first_name": "marc",
                "last_name": "urgeello"
            },
            "following_count": 1,
            "follower_count": 2,
            "followers": [
                1,
                6
            ],
            "following": [
                1,
                6
            ]
        }
    ]
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
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "pepe",
            "email": "pepe@gmail.com",
            "profile": {
                "first_name": "pepe",
                "last_name": "manuel"
            }
        },
        {
            "id": 2,
            "username": "antonio",
            "email": "antonio@gmail.com",
            "profile": {
                "first_name": "pepe",
                "last_name": "manuel"
            }
        }
    ]
}
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

#### Get info from authenticated user
```
GET /api/users/me/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
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

#### Get a list of users by substring
```
GET /api/users/search/?username=pepe
Host: localhost:8000
Content-Type: application/json
Accept: application/json
```
Response
```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "pepe",
            "email": "pepe@gmail.com",
            "profile": {
                "first_name": "pepe",
                "last_name": "manuel"
            }
        }
    ]
}
```

# Posts
#### Get All Posts (with pagination):

```
GET /api/posts/
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "hola, buenas",
            "created_at": "2019-10-09T17:50:54.544053Z",
            "user": {
                "id": 1,
                "username": "pepe",
                "email": "pepe@gmail.com",
                "profile": {
                    "first_name": "pepe",
                    "last_name": "manuel"
                }
            }
        },
        {
            "id": 2,
            "content": "hey, que tal",
            "created_at": "2019-10-09T22:19:38.395935Z",
            "user": {
                "id": 1,
                "username": "pepe",
                "email": "pepe@gmail.com",
                "profile": {
                    "first_name": "pepe",
                    "last_name": "manuel"
                }
            }
        }
    ]
}
```
```
GET /api/posts/?limit=1
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json
{
    "count": 2,
    "next": "http://localhost:8000/api/posts/?limit=1&offset=1",
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "content",
            "created_at": "2019-10-11T15:05:05.973332Z",
            "user": {
                "id": 2,
                "username": "user",
                "email": "user@mail.com",
                "profile": {
                    "first_name": "user",
                    "last_name": "user"
                }
            }
        }
    ]
}
```
#### GET follwed users' & user's post

```
GET /api/posts/{user_id}/all_related/
Host: localhost:8000
Content-Type: application/json
```
Response
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 8,
            "content": "gagagaga",
            "type": "<text>",
            "media": [
                {
                    "url": "http://..."
                }
            ],
            "user": {
                "id": 2,
                "username": "onebu",
                "email": "onebu@test.com",
                "profile": {
                    "first_name": "Jhon",
                    "last_name": "Ash"
                },
                "following_count": 2,
                "follower_count": 1,
                "followers": [
                    1
                ],
                "following": [
                    1
                ]
            },
            "created_at": "2019-11-18T17:41:53.561843Z"
        },
        {
            "id": 6,
            "content": "hohohoho",
            "type": "<text>",
            "media": [
                {
                    "url": "http://..."
                }
            ],
            "user": {
                "id": 2,
                "username": "onebu",
                "email": "onebu@test.com",
                "profile": {
                    "first_name": "Jhon",
                    "last_name": "Ash"
                },
                "following_count": 2,
                "follower_count": 1,
                "followers": [
                    1
                ],
                "following": [
                    1
                ]
            },
            "created_at": "2019-11-18T17:41:41.767335Z"
        }
    ]
}

```
#### Get Post by ID:
```
GET /api/posts/<post_id>
Host: localhost:8000
Content-Type: application/json
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "id": 2,
    "content": "content",
    "type": "<text, image or video>",
    "media": [
        {
            "url": "http://..."
        }
    ],
    "created_at": "2019-10-07T18:42:09.566717Z",
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@mail.com",
        "profile": {
            "first_name": "user",
            "last_name": "user"
        }
    }
}
```
```
HTTP 404 Not Found
Content-Type: application/json

{
    "detail": "Not found."
}
```
#### Publish Post:
```
POST /api/posts/
Host: localhost:8000
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access token>

{
    "content": "<content>"
    "type": "<text, image or video>",
    "media" : [
    	{
    		"url": "http://..."
    	}
    ]
}
```
Response
```
HTTP 201 Created
Content-Type: application/json

{
    "id": 3,
    "content": "<content>",
    "type": "<text, image or video>",
    "media": [
        {
            "url": "http://..."
        }
    ],
    "created_at": "2019-10-11T15:23:34.257337Z",
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@mail.com",
        "profile": {
            "first_name": "user",
            "last_name": "user"
        }
    }
}
```
```
HTTP 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
#### Update Post:
```
PUT /api/posts/<post_id>/
Host: localhost:8000
Content-Type: application/json
Accept: application/json
Authorization: Bearer <access token>

{
    "content": "<new content>"
}
```
Response
```
HTTP 200 OK
Content-Type: application/json

{
    "id": 2,
    "content": "<new content>",
    "created_at": "2019-10-11T15:05:05.973332Z",
    "user": {
        "id": 2,
        "username": "user",
        "email": "user@mail.com",
        "profile": {
            "first_name": "user",
            "last_name": "user"
        }
    }
}
```
```
HTTP 404 Not Found
Content-Type: application/json

{
    "detail": "Not found."
}
```
```
HTTP 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```
HTTP 403 Forbidden
Content-Type: application/json

{
    "detail": "You are not the owner of this post."
}
```

#### Delete Post by ID:
```
DELETE /api/posts/<post_id>/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```
Response
```
HTTP 204 No Content
Content-Type: application/json
```
```
HTTP 404 Not Found
Content-Type: application/json

{
    "detail": "Not found."
}
```
```
HTTP 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
```
HTTP 403 Forbidden
Content-Type: application/json

{
    "detail": "You are not the owner of this post."
}
```
### Get posts from authenticated user
```
GET /api/users/posts/me/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "hola, buenas",
            "created_at": "2019-10-09T17:50:54.544053Z",
            "user": {
                "id": 1,
                "username": "pepe",
                "email": "pepe@gmail.com",
                "profile": {
                    "first_name": "pepe",
                    "last_name": "manuel"
                }
            }
        },
        {
            "id": 2,
            "content": "hey, que tal",
            "created_at": "2019-10-09T22:19:38.395935Z",
            "user": {
                "id": 1,
                "username": "pepe",
                "email": "pepe@gmail.com",
                "profile": {
                    "first_name": "pepe",
                    "last_name": "manuel"
                }
            }
        }
    ]
}
```
```
GET /api/posts/me/?limit=1
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```
Response
```
HTTP 200 OK
Content-Type: application/json
{
    "count": 2,
    "next": "http://localhost:8000/api/posts/?limit=1&offset=1",
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "content",
            "created_at": "2019-10-11T15:05:05.973332Z",
            "user": {
                "id": 2,
                "username": "user",
                "email": "user@mail.com",
                "profile": {
                    "first_name": "user",
                    "last_name": "user"
                }
            }
        }
    ]
}
```

```
HTTP 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
#### Get user's posts:
```
GET /api/users/<user_id>/posts/
Host: localhost:8000
Content-Type: application/json
Authorization: Bearer <access token>
```
```
HTTP 200 OK
Content-Type: application/json

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "content": "hola, buenas",
            "type": "text",
            "media": [],
            "user": {
                "id": 1,
                "username": "pepe",
                "email": "pepe@gmail.com",
                "profile": {
                    "first_name": "pepe",
                    "last_name": "manuel"
                },
                "following_count": 1,
                "follower_count": 3,
                "followers": [
                    5,
                    6
                ],
                "following": [
                    5,
                    6
                ]
            },
            "created_at": "2019-10-09T17:50:54.544053Z"
        },
        {
            "id": 2,
            "content": "hey, que tal",
            "type": "text",
            "media": [],
            "user": {
                "id": 1,
                "username": "pepe",
                "email": "pepe@gmail.com",
                "profile": {
                    "first_name": "pepe",
                    "last_name": "manuel"
                },
                "following_count": 1,
                "follower_count": 3,
                "followers": [
                    5,
                    6
                ],
                "following": [
                    5,
                    6
                ]
            },
            "created_at": "2019-10-09T22:19:38.395935Z"
        }
    ]
}
```
```
HTTP 401 Unauthorized
Content-Type: application/json

{
    "detail": "Authentication credentials were not provided."
}
```
