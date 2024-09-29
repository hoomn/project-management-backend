from django.http import HttpResponse


class HealthCheckMiddleware:
    """
    Middleware to handle AWS EB health checks
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Return a simple OK response for the health check
        if request.method == "GET" and request.path == "/":
            return HttpResponse("OK")

        # For all other requests, continue the normal process
        response = self.get_response(request)

        return response
