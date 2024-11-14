COOKIE_KEY = "labmate_session"
MAX_COOKIE_AGE = 3600
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_KEY = "ADMIN_PASSWORD"
DATABASE_URL_KEY = "DATABASE_URL"
RESERVED_USERNAMES = (
    ADMIN_USERNAME,
    "user",
    "users",
    "login",
    "logout",
    "register",
    "dashboard",
    "samples",
    "experiments",
    "archives",
    "measurements",
)
PUBLIC_ENDPOINTS = ("", "register", "login", "logout")
