"""
Section 1 — Auth: Register.

Populates ctx.state with:
  user1_token, user1_id
  user2_token, user2_id
  user3_token, user3_id  (temporary, deleted in cleanup)
  email1 (string used for login)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("1 · AUTH — REGISTER")

    email1 = ctx.unique_email("alice")
    email2 = ctx.unique_email("bob")
    email3 = ctx.unique_email("charlie")

    # Persist login credentials so the login section can reuse them
    ctx.state["email1"] = email1
    ctx.state["email2"] = email2

    # --- Valid registrations ---

    resp = ctx.req("POST", "/auth/register", body={
        "email": email1,
        "password": "SecurePass1!",
        "name": 'Test Name 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Register user1"):
        data = ctx.safe_json(resp)
        ctx.state["user1_token"] = data.get("token", "")
        ctx.state["user1_id"] = data.get("user", {}).get("id")
        if not ctx.no_sensitive_field_in(data, "password", "register response"):
            ctx.warn("password found in register response")
        _jwt = ctx.decode_jwt(ctx.state["user1_token"])
        if not ctx.no_sensitive_field_in(_jwt, "password", "JWT payload"):
            ctx.warn("password found in JWT payload")
    resp = ctx.req("POST", "/auth/register", body={
        "email": email2,
        "password": "AnotherPass9#",
        "name": 'Test Name 2',
        "bio": 'Test description 2',
    })
    if ctx.assert_status(resp, 201, "Seed: Register user2"):
        data = ctx.safe_json(resp)
        ctx.state["user2_token"] = data.get("token", "")
        ctx.state["user2_id"] = data.get("user", {}).get("id")
        if not ctx.no_sensitive_field_in(data, "password", "register response"):
            ctx.warn("password found in register response")
        _jwt = ctx.decode_jwt(ctx.state["user2_token"])
        if not ctx.no_sensitive_field_in(_jwt, "password", "JWT payload"):
            ctx.warn("password found in JWT payload")
    resp = ctx.req("POST", "/auth/register", body={
        "email": email3,
        "password": "TempPass3$",
        "name": 'Test Name 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Register user3"):
        data = ctx.safe_json(resp)
        ctx.state["user3_token"] = data.get("token", "")
        ctx.state["user3_id"] = data.get("user", {}).get("id")
        if not ctx.no_sensitive_field_in(data, "password", "register response"):
            ctx.warn("password found in register response")
        _jwt = ctx.decode_jwt(ctx.state["user3_token"])
        if not ctx.no_sensitive_field_in(_jwt, "password", "JWT payload"):
            ctx.warn("password found in JWT payload")

    # --- Duplicate login field → 409 ---
    resp = ctx.req("POST", "/auth/register", body={
        "email": email1,
        "password": "SecurePass1!",
        "name": "Duplicate Test",
    })
    ctx.assert_status(resp, 409, "Register duplicate email → 409")

    # --- Missing required fields → 400 ---
    resp = ctx.req("POST", "/auth/register", body={
        "password": "SecurePass1!",
        "email": ctx.unique_email("no_name"),
    })
    ctx.assert_status(resp, 400, "Register without name → 400")

    # Missing password → 400
    resp = ctx.req("POST", "/auth/register", body={
        "email": ctx.unique_email("no_pw"),
        "name": "Test Value",
    })
    ctx.assert_status(resp, 400, "Register without password → 400")

    # Empty body → 400
    resp = ctx.req("POST", "/auth/register", body={})
    ctx.assert_status(resp, 400, "Register with empty body → 400")

    # Invalid email format → 400
    resp = ctx.req("POST", "/auth/register", body={
        "email": "not-an-email",
        "password": "SecurePass1!",
        "name": "Test Value",
    })
    ctx.assert_status(resp, 400, "Register with invalid email format → 400")

    # password too short → 400
    resp = ctx.req("POST", "/auth/register", body={
        "email": ctx.unique_email("short_pw"),
        "password": "1234567",
        "name": "Test Value",
    })
    ctx.assert_status(resp, 400, "Register with password <8 chars → 400")

    # Empty password → 400
    resp = ctx.req("POST", "/auth/register", body={
        "email": ctx.unique_email("empty_pw"),
        "password": "",
        "name": "Test Value",
    })
    ctx.assert_status(resp, 400, "Register with empty password → 400")

    # Truly unknown fields should be silently stripped → 201
    # Note: known fields with invalid values correctly return 400 — do not use them here
    resp = ctx.req("POST", "/auth/register", body={
        "email": ctx.unique_email("extra"),
        "password": "ExtraFields1!",
        "name": "Extra Fields Test",
        "isAdmin": True,
        "unknownField": "should_be_stripped",
    })
    ctx.assert_status(resp, 201, "Register with extra/unknown fields → 201 (stripped)")
