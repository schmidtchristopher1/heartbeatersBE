# app/swagger/guides.py

status_desc = {
    "responses": {
        200: {
            "description": "Status endpoint, returns app status",
            "schema": {
                "type": "object",
                "properties": {"status": {"type": "string", "example": "OK"}},
            },
        }
    }
}

register_desc = {
    "tags": ["Authentication"],
    "summary": "User Registration",
    "description": "Register a new user with personal details and credentials.",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "description": "JSON object containing user registration details.",
            "schema": {
                "type": "object",
                "properties": {
                    "first_name": {"type": "string", "example": "John"},
                    "last_name": {"type": "string", "example": "Doe"},
                    "email": {"type": "string", "example": "john@example.com"},
                    "password": {"type": "string", "example": "securepassword123"},
                    "gender": {"type": "string", "example": "male"},
                    "dob": {"type": "string", "example": "2004-03-03"},
                },
                "required": [
                    "first_name",
                    "last_name",
                    "email",
                    "password",
                    "gender",
                    "dob",
                ],
            },
        }
    ],
    "responses": {
        201: {
            "description": "User registered successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Registration successful"},
                },
            },
        },
        400: {
            "description": "Bad Request",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "First name is required"},
                },
            },
        },
        500: {
            "description": "Internal Server Error",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "An error occurred: <error_message>",
                    }
                },
            },
        },
    },
}

login_desc = {
    "tags": ["Authentication"],
    "summary": "User Login",
    "description": "Authenticate a user with email and password to generate a JWT token.",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "description": "JSON object containing user login details.",
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "john@example.com"},
                    "password": {"type": "string", "example": "securepassword123"},
                },
                "required": ["email", "password"],
            },
        }
    ],
    "responses": {
        200: {
            "description": "Successful Login",
            "schema": {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "example": "eyJhbGciOiJIUzI1NiIsInR5...",
                    },
                },
            },
        },
        400: {
            "description": "Bad Request - Missing email or password",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Email is required",
                    }
                },
            },
        },
        401: {
            "description": "Unauthorized - Invalid credentials",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Unknown email address",
                    }
                },
            },
        },
    },
}

files_desc = {
    "tags": ["Files"],
    "summary": "Upload a file",
    "description": "Endpoint to upload a file for a specific patient. Only .json and .csv files are allowed.",
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "type": "string",
            "required": True,
            "description": "JWT token in the format 'Bearer <token>'",
        },
        {
            "name": "patient_id",
            "in": "formData",
            "type": "string",
            "required": True,
            "description": "ID of the patient",
        },
        {
            "name": "file",
            "in": "formData",
            "type": "file",
            "required": True,
            "description": "File to upload. Only .json and .csv files are allowed.",
        },
    ],
    "responses": {
        200: {
            "description": "File uploaded successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "File uploaded successfully",
                    }
                },
            },
        },
        400: {
            "description": "Bad Request - Missing or invalid fields",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Patient ID is required"}
                },
            },
        },
        401: {
            "description": "Unauthorized - Missing or invalid JWT token",
            "schema": {
                "type": "object",
                "properties": {
                    "msg": {"type": "string", "example": "Missing Authorization Header"}
                },
            },
        },
    },
}

get_patients_desc = {
    "tags": ["Patients"],
    "summary": "Retrieve a list of patients",
    "description": "Get a paginated list of patients with optional filters (e.g., name, email, gender).",
    "parameters": [
        {
            "name": "page",
            "in": "query",
            "type": "integer",
            "required": False,
            "description": "Page number",
        },
        {
            "name": "limit",
            "in": "query",
            "type": "integer",
            "required": False,
            "description": "Number of records per page",
        },
        {
            "name": "name",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filter by name",
        },
        {
            "name": "email",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filter by email",
        },
        {
            "name": "gender",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filter by gender",
        },
    ],
    "responses": {
        200: {
            "description": "Successful response",
            "schema": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer", "example": 1},
                    "page": {"type": "integer", "example": 1},
                    "limit": {"type": "integer", "example": 10},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "example": 1},
                                "name": {"type": "string", "example": "John Doe"},
                                "email": {
                                    "type": "string",
                                    "example": "john@example.com",
                                },
                                "gender": {"type": "string", "example": "male"},
                                "active": {"type": "boolean", "example": True},
                            },
                        },
                    },
                },
            },
        },
        401: {"description": "Unauthorized"},
    },
}

get_patient_desc = {
    "tags": ["Patients"],
    "summary": "Retrieve a specific patient",
    "description": "Get details of a specific patient by ID.",
    "parameters": [
        {
            "name": "patient_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID of the patient",
        },
    ],
    "responses": {
        200: {
            "description": "Successful response",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "name": {"type": "string", "example": "John Doe"},
                    "email": {"type": "string", "example": "john@example.com"},
                    "gender": {"type": "string", "example": "male"},
                    "telecom": {
                        "type": "object",
                        "properties": {
                            "system": {"type": "string", "example": "email"},
                            "value": {"type": "string", "example": "john@example.com"},
                        },
                    },
                    "active": {"type": "boolean", "example": True},
                },
            },
        },
        401: {"description": "Unauthorized"},
        404: {"description": "Patient not found"},
    },
}

logout_desc = {
    "tags": ["Authentication"],
    "summary": "Logout a user",
    "description": "Logs out a user by deactivating their account in the database.",
    "parameters": [
        {
            "in": "body",
            "name": "body",
            "required": True,
            "description": "JSON object containing the user's email to logout.",
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "john.doe@example.com",
                    },
                },
                "required": ["email"],
            },
        }
    ],
    "responses": {
        200: {
            "description": "User logged out successfully",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "User logged out successfully",
                    }
                },
            },
        },
        400: {
            "description": "Bad Request - Missing required fields",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Email is required"},
                },
            },
        },
        401: {
            "description": "Unauthorized - Invalid email address",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Unknown email address",
                    }
                },
            },
        },
        500: {
            "description": "Internal Server Error - An error occurred during the logout process",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "An error occurred: <error_message>",
                    }
                },
            },
        },
    },
}
