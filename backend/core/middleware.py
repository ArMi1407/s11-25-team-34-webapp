class StoreOldSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        # Crear session_key si no existe (anónimo)
        if not request.session.session_key:
            request.session.save()

        # Guardar old_session_key solo si es anónimo y no existe
        if user and not user.is_authenticated:
            if "old_session_key" not in request.session:
                request.session["old_session_key"] = request.session.session_key

        response = self.get_response(request)
        return response
