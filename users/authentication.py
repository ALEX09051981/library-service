from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        header = request.headers.get("Authorization")
        if header is None:
            return None
        return header.encode("utf-8")
