ERRORS = {
    "USER_NOT_FOUND": {
        "status": "error",
        "error": {"code": 404, "message": "No user found"},
    },
    "BAD_CREDS": {
        "status": "error",
        "error": {"code": 401, "message": "Unauthorized"},
    },
    "UNKNOWN": {
        "status": "error",
        "error": {"code": 500, "message": "Something went wrong"},
    },
}
