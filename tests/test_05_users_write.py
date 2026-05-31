"""
Section 5 — User: authenticated write operations (PUT / DELETE).

Requires ctx.state: user1_id, user1_token,
                    user2_id, user2_token (section 1).
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("5 · USER — WRITE OPERATIONS (auth required)")

    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")
    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")


    # 5-1  POST without auth → 401
    resp = ctx.req("POST", "/api/users", body={
        "password": "NoToken!1",
        "name": "Anon",
    })
    ctx.assert_status(resp, 401, "POST /api/users without auth → 401", auth_fail=True)

    # 5-2  PUT without auth → 401
    if user1_id:
        resp = ctx.req("PUT", "/api/users/" + str(user1_id),
                       body={"name": "No Token Edit"})
        ctx.assert_status(resp, 401,
                          f"PUT /api/users/{user1_id} without auth → 401",
                          auth_fail=True)

    # 5-3  DELETE without auth → 401
    if user1_id:
        resp = ctx.req("DELETE", "/api/users/" + str(user1_id))
        ctx.assert_status(resp, 401,
                          f"DELETE /api/users/{user1_id} without auth → 401",
                          auth_fail=True)

    # 5-4  PUT with valid auth — update own record
    if user1_id and token1:
        _auth_update_val = f"Updated User {user1_id}"
        resp = ctx.req("PUT", "/api/users/" + str(user1_id),
                       token=token1,
                       body={"name": _auth_update_val})
        if ctx.assert_status(resp, 200, f"PUT /api/users/{user1_id} by self → 200"):
            data = ctx.safe_json(resp)
            if data.get("name") == _auth_update_val:
                ctx.ok("name update persisted correctly")
            else:
                ctx.fail(f"name not updated: got {data.get('name')!r}")
            if not ctx.no_sensitive_field_in(data, "password", "PUT /api/users response"):
                ctx.warn("Password exposed in PUT /api/users response")

    # 5-5  Security note: auth entity has no owner_fk_field → no ownership guard
    if user1_id and user2_id and token2:
        resp = ctx.req("PUT", "/api/users/" + str(user1_id),
                       token=token2,
                       body={"bio": "Attempted update by another user"})
        if resp.status_code == 200:
            ctx.warn(
                f"SECURITY: user2 successfully updated user1's "
                "profile. The User entity is the auth principal; consider adding an "
                "explicit ownership guard if cross-user mutation should be forbidden."
            )
        elif resp.status_code == 403:
            ctx.ok("PUT /api/users/:id by non-owner correctly returns 403")

    # 5-6  PUT non-existent → 403 (auth check runs first)
    if token1:
        resp = ctx.req("PUT", "/api/users/9999999", token=token1,
                       body={"name": "Ghost"})
        ctx.assert_status(resp, 403,
                          "PUT /api/users/9999999 (authorization first) → 403")
