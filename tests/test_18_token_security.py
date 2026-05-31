"""
Section 18 — Token edge cases and JWT security.

Requires ctx.state: user1_token,
                    document1_id (from seed section).
"""

import requests as _requests
from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("18 · TOKEN EDGE CASES & SECURITY")

    target_id = ctx.state.get("document1_id")
    raw_token = ctx.state.get("user1_token", "")

    def _write_path() -> str:
        return "/api/documents/" + str(target_id)

    # 18-1  Malformed token (not a JWT) → 401
    if target_id:
        resp = ctx.req("PUT", _write_path(),
                       token="not.a.valid.jwt",
                       body={"title": "Malformed token attempt"})
        ctx.assert_status(resp, 401, "Request with malformed JWT → 401", auth_fail=True)

    # 18-2  Tampered signature (flip last char) → 401
    if target_id and raw_token and raw_token.count(".") == 2:
        parts = raw_token.split(".")
        sig = parts[2]
        tampered = sig[:-1] + ("A" if sig[-1] != "A" else "B")
        tampered_token = ".".join(parts[:2] + [tampered])
        resp = ctx.req("PUT", _write_path(),
                       token=tampered_token,
                       body={"title": "Tampered token"})
        ctx.assert_status(resp, 401, "Request with tampered JWT signature → 401", auth_fail=True)

    # 18-3  Empty Bearer value → 401
    if target_id:
        resp = ctx.req("PUT", _write_path(),
                       token="",
                       body={"title": "Empty token"})
        ctx.assert_status(resp, 401, "Request with empty token string → 401", auth_fail=True)

    # 18-4  Token with only two segments (missing signature) → 401
    if target_id and raw_token:
        two_part = ".".join(raw_token.split(".")[:2])
        resp = ctx.req("PUT", _write_path(),
                       token=two_part,
                       body={"title": "Two-segment JWT"})
        ctx.assert_status(resp, 401, "Two-segment JWT (no signature) → 401", auth_fail=True)

    # 18-5  Authorization header without "Bearer" scheme → 401
    if target_id and raw_token:
        headers = {
            "Content-Type": "application/json",
            "Authorization": raw_token,  # Raw token, no "Bearer " prefix
        }
        url = f"{ctx.base_url}/api/documents/{target_id}"
        print(f"  🚀  PUT /api/documents/<id> (Authorization without 'Bearer' prefix)")
        try:
            resp = _requests.request(
                "PUT", url,
                headers=headers, json={"title": "No bearer"}, timeout=10
            )
            if resp.status_code == 401:
                ctx.ok("Missing 'Bearer' prefix → 401")
            else:
                ctx.warn(
                    f"Authorization without 'Bearer' prefix returned HTTP {resp.status_code} "
                    "— middleware should require the 'Bearer' scheme explicitly"
                )
        except Exception as exc:
            ctx.fail(f"Request failed: {exc}")

    # 18-6  JWT payload should not contain sensitive fields
    if raw_token:
        payload = ctx.decode_jwt(raw_token)
        if payload is None:
            ctx.fail("Could not decode JWT payload for inspection")
        else:
            if "password" in payload:
                ctx.warn(
                    "SECURITY: JWT payload contains 'password' field. "
                    "Tokens are base64-decodable without a secret and should "
                    "never carry credentials."
                )
            else:
                ctx.ok("JWT payload does NOT contain 'password'")

    # 18-7  JWT should have an 'exp' claim
    if raw_token:
        payload = ctx.decode_jwt(raw_token)
        if payload:
            if "exp" not in payload:
                ctx.warn("JWT payload has no 'exp' claim — tokens never expire!")
            else:
                ctx.ok(f"JWT has 'exp' claim (expiry timestamp: {payload['exp']})")

    # 18-8  JWT should have an 'iat' claim (issued-at)
    if raw_token:
        payload = ctx.decode_jwt(raw_token)
        if payload:
            if "iat" not in payload:
                ctx.warn("JWT payload is missing 'iat' (issued-at) claim")
            else:
                ctx.ok("JWT has 'iat' claim")
