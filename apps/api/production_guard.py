from .settings import Settings


def assert_safe_production_config(settings: Settings) -> None:
    if settings.environment.lower() not in {"production", "prod"}:
        return

    errors: list[str] = []

    if settings.jwt_secret_key == "CHANGE_ME_IN_PRODUCTION" or len(settings.jwt_secret_key) < 32:
        errors.append("JWT_SECRET_KEY must be set to a strong production secret.")

    if "prepared:prepared" in settings.database_url:
        errors.append("DATABASE_URL must not use the default development credentials in production.")

    if settings.smtp_host and (not settings.smtp_username or not settings.smtp_password):
        errors.append("SMTP_USERNAME and SMTP_PASSWORD are required when SMTP_HOST is configured.")

    if any(origin.startswith("http://localhost") for origin in settings.allowed_origins):
        errors.append("ALLOWED_ORIGINS must not include localhost in production.")

    if errors:
        raise RuntimeError("Production configuration is unsafe: " + " | ".join(errors))
