# Backend Test - Django

The purpose is to develop an API allowing the management of user in a SaaS application

The code must be submitted via git, each functionnal milestone being commited to *master*, and the final result being the last commit on *master*.
Developments must be done in *develop*

## 1st Milestone: CRUD

A user is defined by the following attributes:
* First name
* Last name
* Login
* Email
* Job Title

The entry point is /users, and there is a unicity criteria on both "login" and "email"
All CRUD methods must be implemented

## 2nd Milestone: Authentication Basic

All the routes needs to be protected by Basic Authentication.
Hint: Adapt the user model AND the CRUD methods accordingly.

## 3rd Milestone:  Authentication Bearer

On top of Basic Auth, the routes can be accessed by a JWT token (https://jwt.io/)
* Header: `{'Authorisation': 'Bearer XXX' }`

The token can be generated via:
* endpoint: `/login`
* method: `POST`
* body: 
```
{
  'login': 'XXXX',
  'password': 'YYYY'
}
```

The token expire after one hour, and contain the name/last name and id of the user in its payload.

## 4th Milestone: Authorisation

In order to authorise the routes, users now have an extra attribute is_admin.
The authorisation matrix can be summarised as below:

* if (is_admin) is set to true:

|   |Own Profile|Other Users|
|---|-----------|-----------|
| C |   | X |
| R | X | X |
| U | X | X |
| D |   | X |

* if (is_admin) is set to false:

|   |Own Profile|Other Users|
|---|-----------|-----------|
| C |   |   |
| R | X |   |
| U | X |   |
| D |   |   |

## 5th Milestone: Docker

The application has to be dockerised

## Extra

The candidate if free to add some extra features. Such features might be commited to master with an extra file "EXTRA.md" which lists/describes the extra work.




