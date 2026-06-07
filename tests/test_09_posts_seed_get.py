"""
Section 9 — Post: seed data + unauthenticated GET operations.

Creates posts that subsequent sections depend on.

Populates ctx.state: post1_id, post2_id, post3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("9 · POST — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")

    # --- Seed: create posts ---

    _create_path = "/api/users/posts"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "title": 'Test Title 1',
        "content": 'Test content 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create post1"):
        data = ctx.safe_json(resp)
        ctx.state["post1_id"] = data.get("id")
        if data.get("authorId") == user1_id:
            ctx.ok("authorId injected from JWT")
        else:
            ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")
        if data.get("authorId") == user1_id:
            ctx.ok("authorId injected from URL param")
        else:
            ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "title": 'Test Title 2',
        "content": 'Test content 2',
        "published": True,
    })
    if ctx.assert_status(resp, 201, "Seed: Create post2"):
        data = ctx.safe_json(resp)
        ctx.state["post2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "title": 'Test Title 3',
        "content": 'Test content 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create post3"):
        data = ctx.safe_json(resp)
        ctx.state["post3_id"] = data.get("id")

    # --- GET tests ---

    # 9-1  Paginated list
    resp = ctx.req("GET", "/api/posts")
    if ctx.assert_status(resp, 200, "GET /api/posts → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/posts")

    # 9-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/posts", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/posts?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 9-3  GET by ID
    post1_id = ctx.state.get("post1_id")
    if post1_id:
        resp = ctx.req("GET", "/api/posts/" + str(post1_id))
        if ctx.assert_status(resp, 200, f"GET /api/posts/{post1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == post1_id:
                ctx.ok("Post id matches requested id")
            else:
                ctx.fail(f"Post id mismatch: {data.get('id')} vs {post1_id}")
    else:
        ctx.skip("GET /api/posts/:id — seed ID not available (seed may have failed)")

    # 9-4  Non-existent → 404
    resp = ctx.req("GET", "/api/posts/9999999")
    ctx.assert_status(resp, 404, "GET /api/posts/9999999 → 404")

    # 9-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/posts/notanid")
    ctx.assert_status(resp, 400, "GET /api/posts/notanid → 400 (invalid ID)")

    # 9-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/posts/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/posts/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/posts/-5 → unexpected HTTP {resp.status_code}")
