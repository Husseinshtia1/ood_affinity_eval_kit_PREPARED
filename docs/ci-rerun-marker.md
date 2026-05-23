# CI Rerun Marker

This file exists to trigger a fresh GitHub Actions run on the latest main branch after the API dependency fix.

Last purpose: verify that `apps.api.main` imports successfully after adding `email-validator` for Pydantic `EmailStr` schemas.
