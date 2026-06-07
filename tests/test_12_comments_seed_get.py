"""
Section 12 — Comment: seed data + unauthenticated GET operations.

Creates comments that subsequent sections depend on.

Populates ctx.state: comment1_id, comment2_id, comment3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
  post1_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("12 · COMMENT — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    post1_id = ctx.state.get("post1_id")

    # --- Seed: create comments ---

    _create_path = f"/api/posts/{post1_id}/comments"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "body": 'Test content 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create comment1"):
        data = ctx.safe_json(resp)
        ctx.state["comment1_id"] = data.get("id")
        if data.get("authorId") == user1_id:
            ctx.ok("authorId injected from JWT")
        else:
            ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")
        if data.get("postId") == post1_id:
            ctx.ok("postId injected from URL param")
        else:
            ctx.fail(f"postId mismatch: expected {post1_id}, got {data.get('postId')}")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "body": 'Test content 2',
    })
    if ctx.assert_status(resp, 201, "Seed: Create comment2"):
        data = ctx.safe_json(resp)
        ctx.state["comment2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "body": 'Test content 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create comment3"):
        data = ctx.safe_json(resp)
        ctx.state["comment3_id"] = data.get("id")

    # --- GET tests ---

    # 12-1  Paginated list
    resp = ctx.req("GET", "/api/comments")
    if ctx.assert_status(resp, 200, "GET /api/comments → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/comments")

    # 12-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/comments", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/comments?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 12-3  GET by ID
    comment1_id = ctx.state.get("comment1_id")
    if comment1_id:
        resp = ctx.req("GET", "/api/comments/" + str(comment1_id))
        if ctx.assert_status(resp, 200, f"GET /api/comments/{comment1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == comment1_id:
                ctx.ok("Comment id matches requested id")
            else:
                ctx.fail(f"Comment id mismatch: {data.get('id')} vs {comment1_id}")
    else:
        ctx.skip("GET /api/comments/:id — seed ID not available (seed may have failed)")

    # 12-4  Non-existent → 404
    resp = ctx.req("GET", "/api/comments/9999999")
    ctx.assert_status(resp, 404, "GET /api/comments/9999999 → 404")

    # 12-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/comments/notanid")
    ctx.assert_status(resp, 400, "GET /api/comments/notanid → 400 (invalid ID)")

    # 12-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/comments/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/comments/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/comments/-5 → unexpected HTTP {resp.status_code}")
