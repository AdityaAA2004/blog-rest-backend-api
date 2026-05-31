"""
Section 17 — Nested routes: GET/POST /api/posts/:id/comments.

Post is the primary parent of Comment. The postId
is injected from the URL param. The authorId (if present) is injected from JWT.

Populates ctx.state: parent_nested_comment_id.
Requires ctx.state:
  user1_id, user1_token, user2_id, user2_token
  post1_id, post3_id (from posts seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("17 · NESTED ROUTES — /api/posts/:id/comments")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    post1_id = ctx.state.get("post1_id")
    post3_id = ctx.state.get("post3_id")

    # 17-1  GET → 200 paginated, scoped to parent
    if post1_id:
        resp = ctx.req("GET",
                       "/api/posts/" + str(post1_id) + "/comments")
        if ctx.assert_status(resp, 200,
                             f"GET /api/posts/{post1_id}/comments → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"GET /api/posts/{post1_id}/comments")
            items = data.get("data", [])
            wrong = [item for item in items if item.get("postId") != post1_id]
            if wrong:
                ctx.fail(f"comments list contains items for other parents: {wrong}")
            else:
                ctx.ok(f"All comments correctly scoped to post1")

    # 17-2  GET pagination
    if post1_id:
        resp = ctx.req("GET",
                       "/api/posts/" + str(post1_id) + "/comments",
                       params={"limit": 1})
        if ctx.assert_status(resp, 200,
                             f"GET /api/posts/{post1_id}/comments?limit=1"):
            meta = ctx.safe_json(resp).get("meta", {})
            if meta.get("limit") == 1:
                ctx.ok("limit=1 respected on parent-nested comments")

    # 17-3  Non-existent parent → empty list (not 404)
    resp = ctx.req("GET", "/api/posts/9999999/comments")
    if ctx.assert_status(resp, 200,
                         "GET /api/posts/9999999/comments → 200 empty"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok("Non-existent parent's comments returns total=0")

    # 17-4  POST without auth → 401
    if post1_id:
        resp = ctx.req("POST",
                       "/api/posts/" + str(post1_id) + "/comments",
                       body={
                           "body": "Anonymous attempt",
                       })
        ctx.assert_status(resp, 401,
                          f"POST /api/posts/{post1_id}/comments without auth → 401",
                          auth_fail=True)

    # 17-5  POST with auth, missing required fields → 400
    if post1_id and token1:
        resp = ctx.req("POST",
                       "/api/posts/" + str(post1_id) + "/comments",
                       token=token1,
                       body={
                       })
        ctx.assert_status(resp, 400,
                          f"POST nested comments missing body → 400")

    # 17-6  POST with auth — postId injected from URL
    parent_nested_child_id = None
    if post1_id and token1:
        resp = ctx.req("POST",
                       "/api/posts/" + str(post1_id) + "/comments",
                       token=token1,
                       body={
                           "body": 'Test content 1',
                       })
        if ctx.assert_status(resp, 201, "Seed: Create nested Comment (parent-scoped)"):
            data = ctx.safe_json(resp)
            parent_nested_child_id = data.get("id")
            ctx.state["parent_nested_comment_id"] = parent_nested_child_id
            if data.get("postId") == post1_id:
                ctx.ok("postId injected correctly from URL param")
            else:
                ctx.fail(f"postId mismatch: expected {post1_id}, got {data.get('postId')}")
            if data.get("authorId") == user1_id:
                ctx.ok("authorId injected correctly from JWT")
            else:
                ctx.fail(f"authorId mismatch: expected {user1_id}, got {data.get('authorId')}")

    # 17-7  Security: owner FK spoofing via nested route
    if post1_id and token1 and user2_id:
        resp = ctx.req("POST",
                       "/api/posts/" + str(post1_id) + "/comments",
                       token=token1,
                       body={
                           "body": "Claimed by user2",
                           "authorId": "SPOOFED_VALUE",
                       })
        if resp.status_code == 201:
            data = ctx.safe_json(resp)
            spoofed_id = ctx.state.get("parent_nested_comment_id")
            if data.get("authorId") == user2_id:
                ctx.warn(
                    f"SECURITY: POST /api/posts/:id/comments allows arbitrary authorId — "
                    "should inject from JWT instead."
                )
                ctx.state["spoofed_comment_id"] = data.get("id")
            elif data.get("authorId") == user1_id:
                ctx.ok("POST nested: authorId spoof ignored, set from token")
