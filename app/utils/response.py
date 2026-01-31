
def success_response(message: str = None, data: object = None, code: int = 200):
    """
    Standardized success response.
    """
    return {
        "status": "success",
        "code": code,
        "message": message,
        "data": data
    }

def error_response(message: str = None, errors: list = None, code: int = 400):
    """
    Standardized error response.
    """
    return {
        "status": "error",
        "code": code,
        "message": message,
        "errors": errors or []
    }
