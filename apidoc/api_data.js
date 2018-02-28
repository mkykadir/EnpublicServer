define({ "api": [
  {
    "type": "get",
    "url": "/api/achievement/:key",
    "title": "Get Achievement Details",
    "name": "AchievementDetails",
    "group": "Gamification",
    "description": "<p>Get detailed information of achievement identified by key value</p>",
    "version": "1.0.0",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "key",
            "description": "<p>Unique ID of achievement, key value</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success-Response",
          "content": "HTTP/1.1 200 OK\n{\n    \"date\": 1519208927000,\n    \"desc\": \"Achievement description\",\n    \"key\": \"achv-key\"\n}",
          "type": "json"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "date",
            "description": "<p>Date of achievement gain</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "desc",
            "description": "<p>Description of achievement</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "key",
            "description": "<p>Identifier for achievement</p>"
          }
        ]
      }
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
    "groupTitle": "Gamification"
  },
  {
    "type": "post",
    "url": "/api/achievement",
    "title": "Add New Achievement",
    "name": "AddAchievement",
    "permission": [
      {
        "name": "adminperm",
        "title": "Admin Permission Required",
        "description": "<p>This call designed and developed for management console and only intended for admin use only from managemenet console.</p>"
      }
    ],
    "group": "Gamification",
    "description": "<p>Add new achievement to the system</p>",
    "version": "1.0.0",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "desc",
            "description": "<p>Description of achievement</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "key",
            "description": "<p>Unique identifier for achievement</p>"
          }
        ]
      }
    },
    "filename": "./new_app.py",
    "groupTitle": "Gamification"
  },
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
    "url": "/api/achievement",
    "title": "Achievements Gained by User",
    "name": "UserAchievements",
    "permission": [
      {
        "name": "userperm",
        "title": "User Permission Required",
        "description": "<p>This call requires user permissions to work, users' credentials should be passed through header with BasicAuth.</p>"
      }
    ],
    "group": "User",
    "description": "<p>Get list of achievement that were gained by user during usage of system</p>",
    "version": "1.0.0",
    "header": {
      "fields": {
        "Header": [
          {
            "group": "Header",
            "type": "String",
            "optional": false,
            "field": "authorization",
            "description": "<p>BasicAuth value of username and password pair</p>"
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
            "type": "achivementObject[]",
            "optional": false,
            "field": "result",
            "description": "<p>List of achievements</p>"
          },
          {
            "group": "Success 200",
            "type": "Date",
            "optional": false,
            "field": "date",
            "description": "<p>Date of achievement gain</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "desc",
            "description": "<p>Description of achievement</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "key",
            "description": "<p>Identifier for achievement</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success-Response:",
          "content": "HTTP/1.1 200 OK\n{\n    \"result\": [\n        {\n            \"date\": 1519208927000,\n            \"desc\": \"Achievement description\",\n            \"key\": \"achv-key\"\n        }\n    ]\n}",
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
            "description": "<p>BasicAuth value of username and password pair</p>"
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
