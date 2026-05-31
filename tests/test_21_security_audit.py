"""
Section 21 — Security audit: sensitive field leakage.

Checks that sensitive fields never appear in any response body or JWT payload,
and that auth endpoints don't echo back plaintext credentials.

Requires ctx.state: user1_id, user1_token.
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("21 · SECURITY — SENSITIVE FIELDS AUDIT")

    user1_id = ctx.state.get("user1_id")
    token = ctx.state.get("user1_token", "")

    # 21-1  GET /api/users list — no sensitive fields
    resp = ctx.req("GET", "/api/users")
    if resp.status_code == 200:
        items = ctx.safe_json(resp).get("data", [])
        if not ctx.no_sensitive_field_in(items, "password", "GET /api/users list"):
            ctx.warn(
                "SECURITY: 'password' field is EXPOSED in GET /api/users list. "
                "Ensure safeSelect excludes password from all read queries."
            )
        else:
            ctx.ok("'password' field absent from all records in GET /api/users")

    # 21-2  GET /api/users/:id — no sensitive fields
    if user1_id:
        resp = ctx.req("GET", "/api/users/" + str(user1_id))
        if resp.status_code == 200:
            data = ctx.safe_json(resp)
            if not ctx.no_sensitive_field_in(data, "password", f"GET /api/users/{user1_id}"):
                ctx.warn(f"SECURITY: 'password' exposed in GET /api/users/{user1_id}")
            else:
                ctx.ok(f"'password' absent from GET /api/users/{user1_id}")

    # 21-3  JWT payload — no sensitive fields
    if token:
        payload = ctx.decode_jwt(token)
        if payload is None:
            ctx.fail("Could not decode JWT payload for audit")
        else:
            if "password" in payload:
                ctx.warn(
                    "SECURITY CRITICAL: JWT payload contains 'password' field. "
                    "Tokens are base64-decodable by anyone."
                )
            else:
                ctx.ok("JWT payload does NOT contain 'password' field")

    # 21-4  JWT expiry present
    if token:
        payload = ctx.decode_jwt(token)
        if payload and "exp" not in payload:
            ctx.warn("JWT has no 'exp' claim — tokens never expire (session cannot be revoked)")
        elif payload:
            ctx.ok("JWT 'exp' claim present")

    # 21-5  Fresh register — plaintext sensitive field must not appear in response
    audit_email = ctx.unique_email("audit_sec")
    resp = ctx.req("POST", "/auth/register", body={
        "email": audit_email,
        "password": "AuditPass!99x",
        "email": "Audit User",
        "name": "Audit User",
    })
    if resp.status_code == 201:
        raw_body = resp.text
        if "AuditPass!99x" in raw_body:
            ctx.warn(
                "SECURITY CRITICAL: Plaintext 'password' 'AuditPass!99x' found verbatim "
                "in /auth/register response body!"
            )
        elif '"password"' in raw_body:
            ctx.warn("SECURITY: 'password' key present in /auth/register response JSON")
        else:
            ctx.ok("Plaintext 'password' does NOT appear in /auth/register response body")

    # 21-6  Login response must not contain sensitive fields
    if ctx.state.get("email1"):
        resp = ctx.req("POST", "/auth/login", body={
            "email": ctx.state["email1"],
            "password": "SecurePass1!",
        })
        if resp.status_code == 200:
            raw_body = resp.text
            if "SecurePass1!" in raw_body:
                ctx.warn("SECURITY CRITICAL: Plaintext 'password' found in /auth/login response!")
            elif '"password"' in raw_body:
                ctx.warn("SECURITY: 'password' key present in /auth/login response JSON")
            else:
                ctx.ok("Plaintext 'password' does NOT appear in /auth/login response")

    # 21-7  Helmet security headers should be present
    resp = ctx.req("GET", "/health")
    if resp.status_code == 200:
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "strict-transport-security",
        ]
        present = [h for h in security_headers if h in resp.headers]
        missing = [h for h in security_headers if h not in resp.headers]
        if present:
            ctx.ok(f"Helmet security headers present: {present}")
        if missing:
            ctx.warn(
                f"Helmet security headers missing: {missing}. "
                "Ensure helmet() middleware is registered before routes."
            )
