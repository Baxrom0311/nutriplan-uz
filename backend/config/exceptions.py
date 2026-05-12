from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            "status": "error",
            "message": str(exc.detail) if hasattr(exc, 'detail') else str(exc),
            "errors": response.data if isinstance(response.data, dict) else {"detail": response.data}
        }
        response.data = custom_response
        
    return response
