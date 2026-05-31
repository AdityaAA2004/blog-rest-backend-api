"""
Section 16 — Nested routes: POST /api/users/posts
(canonical create for Post).

POST /api/users/posts is the canonical create endpoint for
Post — User is the primary parent. The parent ID (authorId)
is injected from the auth token, not from the URL.

PUT and DELETE use the direct /api/posts/:id routes.

Populates ctx.state: nested_post_id.
Requires ctx.state: user1_id, user1_token, user2_token.
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("16 · NESTED — POST /api/users/posts + direct PUT/DELETE")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")

    # 16-1  POST without auth → 401
    resp = ctx.req("POST", "/api/users/posts",
                   body={
                       "title": "Anon test",
                       "content": "Anon test",
                   })
    ctx.assert_status(resp, 401,
                      "POST /api/users/posts without auth → 401",
                      auth_fail=True)

    # 16-2  POST with auth — authorId injected from token
    nested_child_id = None
    if token1:
        resp = ctx.req("POST", "/api/users/posts",
                       token=token1,
                       body={
                           "title": 'Test Title 1',
                           "content": 'Test content 1',
                       })
        if ctx.assert_status(resp, 201, "Seed: Create nested Post (ownership test)"):
            data = ctx.safe_json(resp)
            nested_child_id = data.get("id")
            ctx.state["nested_post_id"] = nested_child_id
            if data.get("authorId") == user1_id:
                ctx.ok("authorId injected correctly from JWT")
            else:
                ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")

    # 16-3  POST missing required fields → 400
    if token1:
        resp = ctx.req("POST", "/api/users/posts",
                       token=token1,
                       body={
                           "content": "Missing field test",
                       })
        ctx.assert_status(resp, 400,
                          "POST /api/users/posts missing title → 400")
        resp = ctx.req("POST", "/api/users/posts",
                       token=token1,
                       body={
                           "title": "Missing field test",
                       })
        ctx.assert_status(resp, 400,
                          "POST /api/users/posts missing content → 400")

    # 16-4  PUT by owner → 200 (direct route)
    nested_child_id = ctx.state.get("nested_post_id")
    if nested_child_id and token1:
        resp = ctx.req("PUT", "/api/posts/" + str(nested_child_id),
                       token=token1,
                       body={
                           "title": "Updated via direct PUT",
                           "content": "Updated via direct PUT",
                       })
        if ctx.assert_status(resp, 200,
                             f"PUT /api/posts/{nested_child_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("title") == "Updated via direct PUT":
                ctx.ok("title update via direct PUT persisted correctly")
            else:
                ctx.fail(f"title not updated: {data.get('title')!r}")

    # 16-5  PUT by different user → 403 or 404
    if nested_child_id and token2:
        resp = ctx.req("PUT", "/api/posts/" + str(nested_child_id),
                       token=token2,
                       body={
                           "title": "Hijack attempt",
                           "content": "Hijack attempt",
                       })
        if resp.status_code in (403, 404):
            ctx.ok(f"PUT /api/posts/{nested_child_id} by non-owner → HTTP {resp.status_code} (correct)")
        else:
            ctx.auth(f"PUT /api/posts/{nested_child_id} by non-owner → unexpected HTTP {resp.status_code}")

    # 16-6  DELETE without auth → 401
    if nested_child_id:
        resp = ctx.req("DELETE", "/api/posts/" + str(nested_child_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/posts/{nested_child_id} no auth → 401",
                          auth_fail=True)

    # 16-7  DELETE by different user → 403 or 404
    if nested_child_id and token2:
        resp = ctx.req("DELETE", "/api/posts/" + str(nested_child_id),
                       token=token2)
        if resp.status_code in (403, 404):
            ctx.ok(f"DELETE /api/posts/{nested_child_id} by non-owner → HTTP {resp.status_code} (correct)")
        else:
            ctx.auth(f"DELETE /api/posts/{nested_child_id} by non-owner → unexpected HTTP {resp.status_code}")

    # 16-8  DELETE by owner → 204
    if nested_child_id and token1:
        resp = ctx.req("DELETE", "/api/posts/" + str(nested_child_id),
                       token=token1)
        if ctx.assert_status(resp, 204,
                             f"DELETE /api/posts/{nested_child_id} by owner → 204"):
            ctx.state.pop("nested_post_id", None)
