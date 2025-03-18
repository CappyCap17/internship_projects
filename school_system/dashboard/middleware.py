from django.http import HttpResponseForbidden

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  
        # Required for middleware chain

    def __call__(self, request):
        # Code executed before view
        response = self.get_response(request)  
        # Actual view execution
        # Code executed after view
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.user.is_authenticated:
            if 'principal' in request.path and not request.user.role == 'P':
                return HttpResponseForbidden()  
                # Block access if path contains 'principal' but user isn't Principal
            # Add similar checks for other roles
