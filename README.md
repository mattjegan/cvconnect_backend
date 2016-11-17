# CVConnect Backend

## Requirements
- [Python3](https://www.python.org/downloads/)

## Getting Started
Once you have installed Python3 create a virtualenv outside of this directory and activate it, most people store them in their root directory:

```
cd /
virtualenv CVConnect
source CVConnect/bin/activate
```

Then you will need to `cd` into this project directory `cvconnect_backend` and then run `pip install -r requirements.txt`
This will install django and rest_framework and any other dependencies we add.

Now that we have all the dependencies, we can migrate our database and run the api:

```
export LOCAL=true
python manage migrate
gunicorn cvconnect_backend.cvconnect_backend.wsgi --timeout 60 --keep-alive 5 --log-file -
```

## API Documentation

The api root can now be accessed at `http://cvconnect-api.herokuapp.com/`

### Auth
  First you will need to create a user at `127.0.0.1:8000/api/users/` and then POST:
  
  ```javascript
  {
      "username": "<username>",
      "password": "<password>"
  }
  ```
  to `127.0.0.1:8000/api-token-auth/` which will return the authorization token which will be required by other endpoints to be used. To use the auth token when using the api include `Authorization: Token <token>` in the HTTP headers. Example response from the auth endpoint:
  
  ```javascript
  {
      "token": "a112e88afc98f008de9008"
  }
  ```

### Users
#### UserList
  127.0.0.1:8000/api/users/
  Get Users: GET

  ```javascript
  [
    {
      "id": 1,
      "username": "matt",
      "email": "matt@matt.io",
      "first_name": "matt",
      "last_name": "matt"
    },
    {
      "id": 2,
      "username": "david",
      "email": "david@david.io",
      "first_name": "david",
      "last_name": "david"
    }
  ]
  ```
  
  Create User: POST
  ```javascript
  {
    "username": "matt",
    "password": "mybrilliantpassword",
    "email": "matt@matt.io",
    "first_name": "matt",
    "last_name": "matt"
  }
  ```

#### UserDetail
  127.0.0.1:8000/api/users/:username/
 
  Get User: GET
  
  ```javascript
  {
    "id": 1,
    "username": "matt",
    "email": "matt@matt.io",
    "first_name": "matt",
    "last_name": "matt"
  }
  ```

  Update User: PATCH
  
  ```javascript
  {
    "id": 1,
    "username": "matt",
    "email": "matt@matt.io",
    "first_name": "matt",
    "last_name": "matt"
  }
  ```

### Profiles
#### ProfileList
  127.0.0.1:8000/api/profiles/
  
  Get Profiles: GET
  
  ```javascript
  [
    {
      "id": 1,
      "skills": "python",
      "user": 1
    },
    {
      "id": 2,
      "skills": "java, c",
      "user": 2
    }
  ]
  ```
  
  Create Profile: POST
  
  ```javascript
  {
    "skills": "python",
    "user": 1
  }
  ```
  
#### ProfileDetail
  127.0.0.1:8000/api/profiles/:username/

  Get Profile: GET
  
  ```javascript
  {
    "id": 1,
    "skills": "python",
    "user": 1
  }
  ```
  
  Update Profile: PATCH
  
  ```javascript
  {
    "id": 1,
    "skills": "python, java, haskell",
    "user": 1
  }
  ```

### JobPostings
#### JobList
  127.0.0.1:8000/api/jobs/
  
  Get Jobs: GET
  
  ```javascript
  [
    {
      "id": 1,
      "company": "Nozama",
      "description": "good jobads",
      "compensation": 1000000,
      "recruiter": 1
    },
    {
      "id": 2,
      "company": "Elgoog",
      "description": "Some desc",
      "compensation": 20000,
      "recruiter": 1
    }
  ]
  ```
  
  Create Job: POST
  
  ```javascript
  {
    "company": "my company name",
    "description": "some desc",
    "compensation": 0,
    "recruiter": 1
  }
  ```
  
#### JobDetail
  127.0.0.1:8000/api/jobs/:job_id/
  
  Get Job: GET
  
  ```javascript
  {
    "id": 2,
    "company": "Elgoog",
    "description": "Some desc",
    "compensation": 20000,
    "recruiter": 1
  }
  ```
  
  Update Job: PATCH
  
  ```javascript
  {
    "id": 2,
    "company": "Updated Elgoog",
    "description": "Some updated desc",
    "compensation": 30000,
    "recruiter": 1
  }
  ```

### JobApplications
#### JobApplicationsList
  127.0.0.1:8000/api/jobs/:job_id/applications/
  
  Get Job Applications: GET
  
  ```javascript
  [
    {
      "id": 1,
      "job_posting": 1,
      "profile": 1
    },
    {
      "id": 2,
      "job_posting": 1,
      "profile": 1
    }
  ]
  ```
  
  Create Job Application: POST
  
  ```javascript
  {
    "job_posting": 1,
    "profile": 1
  }
  ```

#### JobApplicationsDetail
  127.0.0.1:8000/api/jobs/:job_id/applications/:application_id/
  
  Get Job Application: GET
  
  ```javascript
  {
    "id": 2,
    "job_posting": 1,
    "profile": 1
  }
  ```
  
  Update Job Application: PATCH
  
  ```javascript
  {
    "id": 2,
    "job_posting": 1,
    "profile": 1
  }
  ```
