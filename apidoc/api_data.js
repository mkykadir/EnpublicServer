define({ "api": [
  {
    "type": "post",
    "url": "/api/signup",
    "title": "Register User",
    "name": "RegisterUser",
    "group": "User",
    "description": "<p>Register new client user to the system. Android client users and Android client application uses this call to register new user. This call doesn't work for admin users and management panel.</p>",
    "version": "1.0.0",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "username",
            "description": "<p>Username of the user</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "password",
            "description": "<p>Password of the user</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Full real name of the user</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "email",
            "description": "<p>E-Mail address of the user</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Example usage:",
          "content": "{\n    \"username\": \"user\",\n    \"password\": \"pass\",\n    \"name\": \"User Name\",\n    \"email\": \"user@provider.com\"\n}",
          "type": "json"
        }
      ]
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "username",
            "description": "<p>Username of the user</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Full real name of the user</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "email",
            "description": "<p>E-Mail address of the user</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success-Response:",
          "content": "HTTP/1.1 200 OK\n{\n    \"username\": \"user\",\n    \"name\": \"User Name\",\n    \"email\": \"user@provider.com\"\n}",
          "type": "json"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "AllErrors",
            "description": "<p>Error description will be returned in message</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Error-Response:",
          "content": "HTTP/1.1 500 Server Error\n{\n    \"message\": \"Error detail and explanation message\"\n}",
          "type": "json"
        }
      ]
    },
    "filename": "./new_app.py",
    "groupTitle": "User"
  },
  {
    "type": "get",
    "url": "/api/profile",
    "title": "Profile Information of User",
    "name": "UserProfile",
    "permission": [
      {
        "name": "userperm",
        "title": "User Permission Required",
        "description": "<p>This call requires user permissions to work, users' credentials should be passed through header with BasicAuth.</p>"
      }
    ],
    "group": "User",
    "description": "<p>Get profile information of the user. Android client uses this call to show users' profile.</p>",
    "version": "1.0.0",
    "header": {
      "fields": {
        "Header": [
          {
            "group": "Header",
            "type": "String",
            "optional": false,
            "field": "authorization",
            "description": "<p>BasicAuth value of username and password tuple</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "BasicAuth-Example",
          "content": "Basic dXNlcjpwYXNz",
          "type": "String"
        }
      ]
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "username",
            "description": "<p>Username of the user</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "name",
            "description": "<p>Full real name of the user</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "email",
            "description": "<p>E-Mail address of the user</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success-Response:",
          "content": "HTTP/1.1 200 OK\n{\n    \"username\": \"user\",\n    \"name\": \"User Name\",\n    \"email\": \"user@provider.com\"\n}",
          "type": "json"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "ServerErrors",
            "description": "<p>Error description will be returned in message</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Error-Response:",
          "content": "HTTP/1.1 500 Server Error\n{\n    \"message\": \"Error detail and explanation message\"\n}",
          "type": "json"
        }
      ]
    },
    "filename": "./new_app.py",
    "groupTitle": "User"
  }
] });
