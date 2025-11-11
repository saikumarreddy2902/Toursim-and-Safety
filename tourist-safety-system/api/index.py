from backend.app import app

# This is the entry point for Vercel
def handler(request):
    return app(request.environ, request.start_response)
