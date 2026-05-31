"""
Section 8 — Document: authenticated write operations (PUT / DELETE).

Requires ctx.state:
  user1_id, user1_token, user2_token
  document1_id, document2_id, document3_id (from seed section)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("8 · DOCUMENT — WRITE OPERATIONS")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    document1_id = ctx.state.get("document1_id")
    document2_id = ctx.state.get("document2_id")
    document3_id = ctx.state.get("document3_id")
    _create_path = "/api/documents"

    # 8-1  POST (canonical create path) without auth → 401
    resp = ctx.req("POST", _create_path, body={
        "title": "Anon Test",
        "content": "Anon Test",
    })
    ctx.assert_status(resp, 401,
                      "POST /api/documents without auth → 401",
                      auth_fail=True)

    # 8-2  POST with auth, empty body → 400
    if token1:
        resp = ctx.req("POST", _create_path, token=token1, body={})
        ctx.assert_status(resp, 400, "POST /api/documents empty body → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"content": "This is test document content."})
        ctx.assert_status(resp, 400, "POST document missing title → 400")

    if token1:
        resp = ctx.req("POST", _create_path, token=token1,
                       body={"title": "Test Document Title"})
        ctx.assert_status(resp, 400, "POST document missing content → 400")

    # 8-update  PUT happy path → 200
    if document1_id and token1:
        _update_val: str | int = "Updated Document"
        resp = ctx.req("PUT", "/api/documents/" + str(document1_id),
                       token=token1,
                       body={"title": _update_val})
        if ctx.assert_status(resp, 200,
                             f"PUT /api/documents/{document1_id} by owner → 200"):
            data = ctx.safe_json(resp)
            if data.get("title") == _update_val:
                ctx.ok("Updated 'title' returned correctly")
            else:
                ctx.fail("Updated 'title' mismatch in response")
    else:
        ctx.skip("PUT /api/documents/:id by owner — seed ID or token not available")

    # 8-auth  PUT without auth → 401
    if document1_id:
        resp = ctx.req("PUT", "/api/documents/" + str(document1_id),
                       body={"title": "Anon edit attempt"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/documents/{document1_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("PUT /api/documents/:id without auth — seed ID not available")


    # 8-notfound  PUT non-existent → 404
    if token1:
        resp = ctx.req("PUT", "/api/documents/00000000-0000-4000-8000-000000000000", token=token1,
                       body={"title": "Ghost update"})
        ctx.assert_status(resp, 404, "PUT /api/documents/00000000-0000-4000-8000-000000000000 (non-existent) → 404")
    else:
        ctx.skip("PUT /api/documents/00000000-0000-4000-8000-000000000000 — token not available")

    # 8-delete-noauth  DELETE without auth → 401
    if document2_id:
        resp = ctx.req("DELETE", "/api/documents/" + str(document2_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/documents/{document2_id} without auth → 401",
                          auth_fail=True)
    else:
        ctx.skip("DELETE /api/documents/:id without auth — seed ID2 not available")


    # 8-delete-owner  DELETE by owner → 204
    if document2_id and token1:
        resp = ctx.req("DELETE", "/api/documents/" + str(document2_id), token=token1)
        if ctx.assert_status(resp, 204, f"DELETE /api/documents/{document2_id} by owner → 204"):
            ctx.state["document2_deleted"] = True
    else:
        ctx.skip("DELETE /api/documents/:id by owner — seed ID2 or token not available")

    # 8-get-deleted  GET after delete → 404
    if document2_id and ctx.state.get("document2_deleted"):
        resp = ctx.req("GET", "/api/documents/" + str(document2_id))
        ctx.assert_status(resp, 404,
                          f"GET /api/documents/{document2_id} after deletion → 404")

    # 8-delete-notfound  DELETE non-existent → 404
    if token1:
        resp = ctx.req("DELETE", "/api/documents/00000000-0000-4000-8000-000000000000", token=token1)
        ctx.assert_status(resp, 404, "DELETE /api/documents/00000000-0000-4000-8000-000000000000 (non-existent) → 404")
    else:
        ctx.skip("DELETE /api/documents/00000000-0000-4000-8000-000000000000 — token not available")
