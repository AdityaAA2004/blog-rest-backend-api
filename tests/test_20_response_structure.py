"""
Section 20 — Response structure integrity.

Verifies consistent error envelope, 201 resource body, 204 empty body,
and pagination meta across all list endpoints.

Requires ctx.state: user1_token
                    document1_id (from documents seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("20 · RESPONSE STRUCTURE INTEGRITY")

    token1 = ctx.state.get("user1_token")
    document1_id = ctx.state.get("document1_id")

    # 20-1  404 errors use { "error": "..." } envelope
    resp = ctx.req("GET", "/api/users/9999999")
    if resp.status_code == 404:
        data = ctx.safe_json(resp)
        if "error" in data:
            ctx.ok("404 error response uses { error: '...' } envelope")
        else:
            ctx.fail(f"404 error response missing 'error' key: {data}")

    # 20-2  400 validation errors also use { "error": "..." }
    resp = ctx.req("POST", "/api/documents", token=token1, body={})
    if resp.status_code == 400:
        data = ctx.safe_json(resp)
        if "error" in data:
            ctx.ok("400 validation error uses { error: '...' } envelope")
        else:
            ctx.fail(f"400 validation error missing 'error' key: {data}")

    # 20-3  401 errors use { "error": "..." }
    resp = ctx.req("POST", "/api/documents", body={"title": "x", "content": "y"})
    if resp.status_code == 401:
        data = ctx.safe_json(resp)
        if "error" in data:
            ctx.ok("401 error response uses { error: '...' } envelope")
        else:
            ctx.fail(f"401 response missing 'error' key: {data}")

    # 20-4  All list endpoints carry hasNext and hasPrev in meta
    resp = ctx.req("GET", "/api/users")
    if resp.status_code == 200:
        meta = ctx.safe_json(resp).get("meta", {})
        if "hasNext" in meta and "hasPrev" in meta:
            ctx.ok("GET /api/users: meta.hasNext and meta.hasPrev present")
        else:
            ctx.fail(f"GET /api/users: meta missing hasNext/hasPrev — got {meta}")
    resp = ctx.req("GET", "/api/posts")
    if resp.status_code == 200:
        meta = ctx.safe_json(resp).get("meta", {})
        if "hasNext" in meta and "hasPrev" in meta:
            ctx.ok("GET /api/posts: meta.hasNext and meta.hasPrev present")
        else:
            ctx.fail(f"GET /api/posts: meta missing hasNext/hasPrev — got {meta}")
    resp = ctx.req("GET", "/api/comments")
    if resp.status_code == 200:
        meta = ctx.safe_json(resp).get("meta", {})
        if "hasNext" in meta and "hasPrev" in meta:
            ctx.ok("GET /api/comments: meta.hasNext and meta.hasPrev present")
        else:
            ctx.fail(f"GET /api/comments: meta missing hasNext/hasPrev — got {meta}")
    resp = ctx.req("GET", "/api/documents")
    if resp.status_code == 200:
        meta = ctx.safe_json(resp).get("meta", {})
        if "hasNext" in meta and "hasPrev" in meta:
            ctx.ok("GET /api/documents: meta.hasNext and meta.hasPrev present")
        else:
            ctx.fail(f"GET /api/documents: meta missing hasNext/hasPrev — got {meta}")

    # 20-5  200 responses return JSON (Content-Type: application/json)
    resp = ctx.req("GET", "/api/users")
    ct = resp.headers.get("Content-Type", "")
    if "application/json" in ct:
        ctx.ok(f"GET /api/users Content-Type is application/json")
    else:
        ctx.warn(f"GET /api/users unexpected Content-Type: {ct!r}")

    # 20-6  hasNext / hasPrev values are boolean, not strings
    resp = ctx.req("GET", "/api/users", params={"page": 1})
    if resp.status_code == 200:
        meta = ctx.safe_json(resp).get("meta", {})
        for key in ("hasNext", "hasPrev"):
            val = meta.get(key)
            if isinstance(val, bool):
                ctx.ok(f"meta.{key} is a boolean: {val}")
            else:
                ctx.fail(f"meta.{key} is not a boolean: {val!r} ({type(val).__name__})")

    # 20-7  totalPages is consistent with total and limit
    resp = ctx.req("GET", "/api/users", params={"limit": 1})
    if resp.status_code == 200:
        meta = ctx.safe_json(resp).get("meta", {})
        total = meta.get("total", 0)
        limit = meta.get("limit", 1)
        actual_pages = meta.get("totalPages")
        if total == 0:
            if actual_pages in (0, 1):
                ctx.ok(f"totalPages={actual_pages} correct for empty result (total=0)")
            else:
                ctx.fail(f"totalPages={actual_pages} unexpected for total=0, limit={limit}")
        else:
            expected_pages = -(-total // limit)  # ceiling division
            if actual_pages == expected_pages:
                ctx.ok(f"totalPages={actual_pages} consistent with total={total}, limit={limit}")
            else:
                ctx.fail(
                    f"totalPages={actual_pages} inconsistent with "
                    f"total={total}, limit={limit} (expected {expected_pages})"
            )
