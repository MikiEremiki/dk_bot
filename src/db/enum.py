import enum


class UserRole(enum.Enum):
    DEVELOPER = "разработчик"
    ADMIN = "админ"
    USER = "пользователь"
    GUEST = "гость"
