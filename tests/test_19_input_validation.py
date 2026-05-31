"""
Section 19 — Input validation and edge cases.

Uses Document as the primary test entity.
Requires ctx.state: user1_token.
Populates ctx.state: long_title_document_id, xss_document_id, unicode_document_id
                     (kept for cleanup).
"""

import requests as _req
from helpers import TestContext, section

def run(ctx: TestContext) -> None:
    section("19 · INPUT VALIDATION & EDGE CASES")

    token1 = ctx.state.get("user1_token")

    # Resolve canonical create path — replace :id placeholder with actual parent ID from state
    _create_path = "/api/documents"


    # 19-1  Very long title (300 chars) — should be rejected or truncated
    long_value = "A" * 300
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "title": long_value,
                           "content": "Normal value",
                       })
        if resp.status_code in (400, 422):
            ctx.ok(f"POST document title=300 chars → HTTP {resp.status_code} (rejected)")
        elif resp.status_code == 201:
            ctx.warn(
                "POST document accepted 300-char title — "
                "consider .max(255) in the Zod 'title' schema"
            )
            ctx.state["long_title_document_id"] = ctx.safe_json(resp).get("id")

    # 19-2  Very long content (15 000 chars)
    long_content = "C" * 15_000
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "content": long_content,
                           "title": "Normal value",
                       })
        if resp.status_code in (400, 422):
            ctx.ok(f"POST document content=15000 chars → HTTP {resp.status_code} (rejected)")
        elif resp.status_code == 201:
            ctx.warn(
                "POST document accepted 15 000-char content — "
                "consider .max(10000) in the Zod schema"
            )
            ctx.state["long_content_document_id"] = ctx.safe_json(resp).get("id")

    # 19-3  XSS payload in content — stored verbatim (escaping is frontend responsibility)
    xss_payload = '<script>alert("xss")</script>'
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "title": "XSS Test",
                           "content": xss_payload,
                       })
        if resp.status_code == 201:
            ctx.warn(
                "XSS payload stored verbatim in DB — ensure HTML escaping is applied "
                "at render time (frontend responsibility)."
            )
            ctx.ok("API stored content without modification (escaping is frontend concern)")
            ctx.state["xss_document_id"] = ctx.safe_json(resp).get("id")
        else:
            ctx.ok(f"XSS payload rejected with HTTP {resp.status_code}")

    # 19-4  SQL injection in query param — server must not crash
    resp = ctx.req("GET", "/api/documents", params={"page": "1; DROP TABLE documents; --"})
    if resp.status_code == 200:
        ctx.ok("SQL injection in ?page param → 200 (gracefully handled / Prisma parameterised)")
    elif resp.status_code == 400:
        ctx.ok("SQL injection in ?page param → 400 (rejected by validation)")
    else:
        ctx.warn(f"SQL injection in page param → unexpected HTTP {resp.status_code}")

    # 19-5  SQL injection in path segment → 400 or 404
    resp = ctx.req("GET", "/api/documents/1; DROP TABLE documents --")
    if resp.status_code in (400, 404):
        ctx.ok(f"SQL injection in path segment → HTTP {resp.status_code} (handled)")
    else:
        ctx.warn(f"SQL injection in path segment → unexpected HTTP {resp.status_code}")

    # 19-6  Unicode / emoji — should round-trip correctly
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "title": "Unicode Test 🌍🚀",
                           "content": "Normal value",
                       })
        if ctx.assert_status(resp, 201, "POST document with Unicode/emoji → 201"):
            data = ctx.safe_json(resp)
            content_val = data.get("title", "")
            if "🌍" in content_val or "🚀" in content_val:
                ctx.ok("Unicode/emoji stored and returned correctly")
            else:
                ctx.fail("Emoji not present in returned response (field: title)")
            ctx.state["unicode_document_id"] = data.get("id")

    # 19-7  Empty string title → 400 (validation)
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={
                           "title": "",
                           "content": "Normal value",
                       })
        if resp.status_code == 400:
            ctx.ok("POST document with empty string title → 400 (validation)")
        elif resp.status_code == 201:
            ctx.warn(
                "POST document accepted empty string title — "
                "consider .min(1) in the Zod 'title' schema"
            )

    # 19-8  Non-numeric pagination params → fall back to defaults
    resp = ctx.req("GET", "/api/documents", params={"page": "abc", "limit": "xyz"})
    if ctx.assert_status(resp, 200, "GET /api/documents?page=abc&limit=xyz → 200 (defaults)"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 1 and meta.get("limit") == 20:
            ctx.ok("Non-numeric pagination params fall back to defaults page=1 limit=20")
        else:
            ctx.warn(f"Non-numeric pagination produced unexpected meta: {meta}")

    # 19-9  Integer overflow in ID
    big_id = 2 ** 53
    resp = ctx.req("GET", f"/api/documents/{big_id}")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/documents/{big_id} (integer overflow) → HTTP {resp.status_code} (handled)")
    else:
        ctx.warn(f"Integer overflow in ID → unexpected HTTP {resp.status_code}")

    # 19-10  Content-Type: text/plain body → 400 or 415
    if token1:
        url = f"{ctx.base_url}{_create_path}"
        print(f"  🚀  POST /api/documents (Content-Type: text/plain)")
        try:
            resp = _req.post(
                url,
                headers={"Authorization": f"Bearer {token1}", "Content-Type": "text/plain"},
                data='{"title":"value"}',
                timeout=10,
            )
            if resp.status_code in (400, 415):
                ctx.ok(f"POST with Content-Type: text/plain → HTTP {resp.status_code} (non-JSON body rejected)")
            else:
                ctx.warn(
                    f"POST with Content-Type: text/plain → HTTP {resp.status_code} "
                    "— Express json() middleware may have silently ignored the body"
                )
        except Exception as exc:
            ctx.fail(f"Request failed: {exc}")

    # 19-11  No body at all → 400
    if token1:
        url = f"{ctx.base_url}{_create_path}"
        print("  🚀  POST /api/documents (no body at all)")
        try:
            resp = _req.post(
                url,
                headers={"Authorization": f"Bearer {token1}", "Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status_code in (400, 422):
                ctx.ok(f"POST with no body → HTTP {resp.status_code} (validation rejected)")
            else:
                ctx.warn(f"POST with no body → HTTP {resp.status_code}")
        except Exception as exc:
            ctx.fail(f"Request failed: {exc}")
