"""
Section 6 — Document: seed data + unauthenticated GET operations.

Creates documents that subsequent sections depend on.

Populates ctx.state: document1_id, document2_id, document3_id.
Requires ctx.state:
  user1_id, user1_token, user2_token, user2_id
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("6 · DOCUMENT — SEED & GET (unauthenticated reads)")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")
    user1_id = ctx.state.get("user1_id")
    user2_id = ctx.state.get("user2_id")

    # --- Seed: create documents ---

    _create_path = "/api/documents"
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "title": 'Test Title 1',
        "content": 'Test content 1',
    })
    if ctx.assert_status(resp, 201, "Seed: Create document1"):
        data = ctx.safe_json(resp)
        ctx.state["document1_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token1,
                   body={
        "title": 'Test Title 2',
        "content": 'Test content 2',
    })
    if ctx.assert_status(resp, 201, "Seed: Create document2"):
        data = ctx.safe_json(resp)
        ctx.state["document2_id"] = data.get("id")
    resp = ctx.req("POST", _create_path,
                   token=token2,
                   body={
        "title": 'Test Title 3',
        "content": 'Test content 3',
    })
    if ctx.assert_status(resp, 201, "Seed: Create document3"):
        data = ctx.safe_json(resp)
        ctx.state["document3_id"] = data.get("id")

    # --- GET tests ---

    # 6-1  Paginated list
    resp = ctx.req("GET", "/api/documents")
    if ctx.assert_status(resp, 200, "GET /api/documents → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), "GET /api/documents")

    # 6-2  Pagination: page=2, limit=1
    resp = ctx.req("GET", "/api/documents", params={"limit": 1, "page": 2})
    if ctx.assert_status(resp, 200, "GET /api/documents?limit=1&page=2"):
        meta = ctx.safe_json(resp).get("meta", {})
        if meta.get("page") == 2 and meta.get("limit") == 1:
            ctx.ok("Pagination page=2, limit=1 meta correct")
        else:
            ctx.fail(f"Unexpected meta: {meta}")
        if meta.get("hasPrev") is True:
            ctx.ok("meta.hasPrev=true on page 2")
        else:
            ctx.fail(f"Expected hasPrev=true on page 2, got {meta.get('hasPrev')}")

    # 6-3  GET by ID
    document1_id = ctx.state.get("document1_id")
    if document1_id:
        resp = ctx.req("GET", "/api/documents/" + str(document1_id))
        if ctx.assert_status(resp, 200, f"GET /api/documents/{document1_id} → 200"):
            data = ctx.safe_json(resp)
            if data.get("id") == document1_id:
                ctx.ok("Document id matches requested id")
            else:
                ctx.fail(f"Document id mismatch: {data.get('id')} vs {document1_id}")
    else:
        ctx.skip("GET /api/documents/:id — seed ID not available (seed may have failed)")

    # 6-4  Non-existent → 404
    resp = ctx.req("GET", "/api/documents/00000000-0000-4000-8000-000000000000")
    ctx.assert_status(resp, 404, "GET /api/documents/00000000-0000-4000-8000-000000000000 → 404")

    # 6-5  Non-numeric ID → 400
    resp = ctx.req("GET", "/api/documents/notanid")
    ctx.assert_status(resp, 400, "GET /api/documents/notanid → 400 (invalid ID)")

    # 6-6  Negative ID → 400 or 404
    resp = ctx.req("GET", "/api/documents/-5")
    if resp.status_code in (400, 404):
        ctx.ok(f"GET /api/documents/-5 → HTTP {resp.status_code} (acceptable)")
    else:
        ctx.fail(f"GET /api/documents/-5 → unexpected HTTP {resp.status_code}")
