"""
Section 14 — Comment: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  comment1_id, comment2_id, comment3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("14 · COMMENT — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    comment1_id = ctx.state.get("comment1_id")
    comment2_id = ctx.state.get("comment2_id")
    comment3_id = ctx.state.get("comment3_id")
    post1_id = ctx.state.get("post1_id")
    _create_path = f"/api/posts/{post1_id}/comments"

    # 14-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "body": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/posts/:id/comments without auth → 401",
                      auth_fail=True)

    # 14-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/posts/:id/comments empty body → 400")

    # 14-val-body  missing body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST comment missing body → 400")

    # 14-spoof  ownership spoofing
    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"body": "Spoofing attempt comment text", "authorId": user2_id})
        data = ctx.safe_json(resp)
        if resp.status_code == 201 and data.get("authorId") == user1_id:
            ctx.ok("ownership spoofing prevented — authorId correctly overridden")
        elif resp.status_code == 201 and data.get("authorId") == user2_id:
            ctx.warn("SECURITY: ownership spoofing succeeded — authorId accepted from body")
        if resp.status_code == 201:
            ctx.state["spoofed_comment_id"] = data.get("id")

    # 14-update  PUT happy path → 200
    if comment1_id and token1:
        _update_val: str | int = "Updated Comment"
        resp = ctx.req("PUT", "/api/comments/" + str(comment1_id),
                       token=token1,
                       body={"body": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/comments/{comment1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("body") == _update_val:
                ctx.ok("Updated 'body' returned correctly")
            else:
                ctx.fail("Updated 'body' mismatch in response")
    else:
        ctx.skip("PUT /api/comments/:id by owner — seed ID or token not available")

    # 14-auth  PUT without auth → 401
    if comment1_id:
        resp = ctx.req("PUT", "/api/comments/" + str(comment1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/comments/{comment1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/comments/:id without auth — seed ID not available")

    # 14-owner  PUT by non-owner → 403
    if comment1_id and token2:
        resp = ctx.req("PUT", "/api/comments/" + str(comment1_id),
                       token=token2,
                       body={"title": "Hijack attempt"})
        ctx.assert_status(resp, 403,
                          f"PUT /api/comments/{comment1_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/comments/:id by non-owner — seed ID or token2 not available")

    # 14-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/comments/9999999", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/comments/9999999 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/comments/9999999 — token not available")

    # 14-delete-noauth  DELETE without auth → 401
    if comment2_id:
        resp = ctx.req("DELETE", "/api/comments/" + str(comment2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/comments/{comment2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/comments/:id without auth — seed ID2 not available")

    # 14-delete-nonowner  DELETE by non-owner → 403
    if comment2_id and token2:
        resp = ctx.req("DELETE", "/api/comments/" + str(comment2_id),
                       token=token2)
        ctx.assert_status(resp, 403,
                          f"DELETE /api/comments/{comment2_id} by non-owner → 403",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/comments/:id by non-owner — seed ID2 or token2 not available")

    # 14-delete-owner  DELETE by owner → 204
    if comment2_id and token1:
        resp = ctx.req("DELETE", "/api/comments/" + str(comment2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/comments/{comment2_id} by owner → 204"):
            ctx.state["comment2_deleted"] = True
    else:
        ctx.skip("DELETE /api/comments/:id by owner — seed ID2 or token not available")

    # 14-get-deleted  GET after delete → 404
    if comment2_id and ctx.state.get("comment2_deleted"):
        resp = ctx.req("GET", "/api/comments/" + str(comment2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/comments/{comment2_id} after deletion → 404")

    # 14-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/comments/9999999", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/comments/9999999 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/comments/9999999 — token not available")
