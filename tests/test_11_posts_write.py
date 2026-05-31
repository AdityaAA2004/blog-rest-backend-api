"""
Section 11 — Post: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  post1_id, post2_id, post3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("11 · POST — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    post1_id = ctx.state.get("post1_id")
    post2_id = ctx.state.get("post2_id")
    post3_id = ctx.state.get("post3_id")
    _create_path = "/api/users/posts"

    # 11-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "title": "Anon Test",
        "content": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/users/posts without auth → 401",
                      auth_fail=True)

    # 11-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/users/posts empty body → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"content": "This is test content for a blog post."})
        ctx.assert_status(resp, 400, "POST post missing title → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"title": "Test Post Title"})
        ctx.assert_status(resp, 400, "POST post missing content → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"title": "Spoof Test", "content": "Spoofing content here.",
                             "authorId": user2_id})
        data = ctx.safe_json(resp)
        if resp.status_code == 201 and data.get("authorId") == user1_id:
            ctx.ok("ownership spoofing prevented — authorId correctly overridden")
        elif resp.status_code == 201 and data.get("authorId") == user2_id:
            ctx.warn("SECURITY: ownership spoofing succeeded — authorId accepted from body")
        if resp.status_code == 201:
            ctx.state["spoofed_post_id"] = data.get("id")

    # 11-update  PUT happy path → 200
    if post1_id and token1:
        _update_val: str | int = "Updated Post"
        resp = ctx.req("PUT", "/api/posts/" + str(post1_id),
                       token=token1,
                       body={"title": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/posts/{post1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("title") == _update_val:
                ctx.ok("Updated 'title' returned correctly")
            else:
                ctx.fail("Updated 'title' mismatch in response")
    else:
        ctx.skip("PUT /api/posts/:id by owner — seed ID or token not available")

    # 11-auth  PUT without auth → 401
    if post1_id:
        resp = ctx.req("PUT", "/api/posts/" + str(post1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/posts/{post1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/posts/:id without auth — seed ID not available")

    # 11-owner  PUT by non-owner → 403
    if post1_id and token2:
        resp = ctx.req("PUT", "/api/posts/" + str(post1_id),
                       token=token2,
                       body={"title": "Hijack attempt"})
        ctx.assert_status(resp, 403,
                          f"PUT /api/posts/{post1_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/posts/:id by non-owner — seed ID or token2 not available")

    # 11-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/posts/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/posts/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/posts/9999999 — token not available")

    # 11-delete-noauth  DELETE without auth → 401
    if post2_id:
        resp = ctx.req("DELETE", "/api/posts/" + str(post2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/posts/{post2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/posts/:id without auth — seed ID2 not available")

    # 11-delete-nonowner  DELETE by non-owner → 403
    if post2_id and token2:
        resp = ctx.req("DELETE", "/api/posts/" + str(post2_id),
                       token=token2)
        ctx.assert_status(resp, 403,
                          f"DELETE /api/posts/{post2_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/posts/:id by non-owner — seed ID2 or token2 not available")

    # 11-delete-owner  DELETE by owner → 204
    if post2_id and token1:
        resp = ctx.req("DELETE", "/api/posts/" + str(post2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/posts/{post2_id} by owner → 204"):
            ctx.state["post2_deleted"] = True
    else:
        ctx.skip("DELETE /api/posts/:id by owner — seed ID2 or token not available")

    # 11-get-deleted  GET after delete → 404
    if post2_id and ctx.state.get("post2_deleted"):
        resp = ctx.req("GET", "/api/posts/" + str(post2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/posts/{post2_id} after deletion → 404")

    # 11-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/posts/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/posts/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/posts/9999999 — token not available")
