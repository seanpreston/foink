# joynotes-backend


An API with the spec:

POST /api/note/
{
  "text": "some content",  // string up to 2048 chars long
  "rating": 5,  // int between 0 and 5
}

GET /api/note/:uuid/

GET /api/notes/?start=dd-mm-yyyy&end=dd-mm-yyyy&rating=:rating

These requests will require the header `Authorization: Token :token` to work, token is returned from either:

POST /api/signin/
{
  "username": ":username",
  "password": ":password"
}

POST /api/signup/

{
  "username": ":username",
  "password": ":password"
}