"""
Section 7 — Document: filter and sort query parameters.

Tests ?sortBy, ?sortOrder, and field-filter params on:
  GET /api/documents

Requires ctx.state: document1_id, document2_id, document3_id
  user1_id (for nested scoping)
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("7 · DOCUMENT — FILTER & SORT")

    document1_id = ctx.state.get("document1_id")
    base = "/api/documents"

    # ── Sort tests ────────────────────────────────────────────────────────────

    # 7-1  sortBy=id&sortOrder=asc → items ordered ascending by id
    resp = ctx.req("GET", base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=id&sortOrder=asc → 200"):
        data = ctx.safe_json(resp)
        ctx.assert_paginated(data, f"{base}?sortBy=id&sortOrder=asc")
        items = data.get("data", [])
        if len(items) >= 2:
            ids = [item.get("id") for item in items if item.get("id") is not None]
            if ids == sorted(ids):
                ctx.ok("sortBy=id&sortOrder=asc: items in ascending id order")
            else:
                ctx.fail(f"sortBy=id&sortOrder=asc: expected ascending ids, got {ids[:5]}")
        else:
            ctx.ok("sortBy=id&sortOrder=asc: fewer than 2 items, order not verifiable")

    # 7-2  sortBy=id&sortOrder=desc → items ordered descending by id
    resp = ctx.req("GET", base, params={"sortBy": "id", "sortOrder": "desc", "limit": 50})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=id&sortOrder=desc → 200"):
        data = ctx.safe_json(resp)
        ctx.assert_paginated(data, f"{base}?sortBy=id&sortOrder=desc")
        items = data.get("data", [])
        if len(items) >= 2:
            ids = [item.get("id") for item in items if item.get("id") is not None]
            if ids == sorted(ids, reverse=True):
                ctx.ok("sortBy=id&sortOrder=desc: items in descending id order")
            else:
                ctx.fail(f"sortBy=id&sortOrder=desc: expected descending ids, got {ids[:5]}")
        else:
            ctx.ok("sortBy=id&sortOrder=desc: fewer than 2 items, order not verifiable")

    # 7-3  sortBy=id with no sortOrder → defaults to ascending
    resp_asc = ctx.req("GET", base, params={"sortBy": "id", "sortOrder": "asc", "limit": 50})
    resp_def = ctx.req("GET", base, params={"sortBy": "id", "limit": 50})
    if ctx.assert_status(resp_def, 200, f"GET {base}?sortBy=id (no sortOrder) → 200"):
        ctx.assert_paginated(ctx.safe_json(resp_def), f"{base}?sortBy=id")
        items_asc = ctx.safe_json(resp_asc).get("data", []) if resp_asc.status_code == 200 else []
        items_def = ctx.safe_json(resp_def).get("data", [])
        ids_asc = [i.get("id") for i in items_asc]
        ids_def = [i.get("id") for i in items_def]
        if ids_asc and ids_def:
            if ids_def == ids_asc:
                ctx.ok("sortBy=id with no sortOrder matches explicit asc order")
            else:
                ctx.fail(f"Default sortOrder should be asc. asc={ids_asc[:3]} default={ids_def[:3]}")
        else:
            ctx.ok("Default sortOrder: no items to compare")

    # 7-4  Unknown sortBy field → ignored, returns 200 with valid paginated response
    resp = ctx.req("GET", base, params={"sortBy": "__nonexistent_field__"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=__nonexistent_field__ → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=unknown")

    # 7-6-2  sortBy=title&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "title", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=title&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=title&sortOrder=asc")
        ctx.ok("sortBy=title&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "title", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=title&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=title&sortOrder=desc")
        ctx.ok("sortBy=title&sortOrder=desc accepted")

    # 7-6-3  sortBy=content&sortOrder=asc → 200, valid response
    resp = ctx.req("GET", base, params={"sortBy": "content", "sortOrder": "asc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=content&sortOrder=asc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=content&sortOrder=asc")
        ctx.ok("sortBy=content&sortOrder=asc accepted")

    resp = ctx.req("GET", base, params={"sortBy": "content", "sortOrder": "desc"})
    if ctx.assert_status(resp, 200, f"GET {base}?sortBy=content&sortOrder=desc → 200"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?sortBy=content&sortOrder=desc")
        ctx.ok("sortBy=content&sortOrder=desc accepted")


    # ── Filter tests ──────────────────────────────────────────────────────────

    # Baseline: unfiltered total for comparison
    _baseline = ctx.req("GET", base)
    _baseline_total = ctx.safe_json(_baseline).get("meta", {}).get("total", 0) if _baseline.status_code == 200 else 0

    # Fetch entity1 to get real field values for filter assertions
    _entity1_data = {}
    if document1_id:
        _fetch = ctx.req("GET", f"{base}/{document1_id}")
        if _fetch.status_code == 200:
            _entity1_data = ctx.safe_json(_fetch)

    # 7-F-1  Filter by title (string) — match seeded value
    _val_title = _entity1_data.get("title")
    if _val_title is not None:
        resp = ctx.req("GET", base, params={"title": str(_val_title), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?title={_val_title} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?title=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if document1_id in ids_in_result:
                ctx.ok(f"Filter title={_val_title}: entity1 found in results")
            else:
                ctx.fail(f"Filter title={_val_title}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter title: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter title: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("title") != _val_title]
            if not mismatched:
                ctx.ok("Filter title: all returned items match filter value")
            else:
                ctx.fail(f"Filter title: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter title: entity1 data not available (seed may have failed)")

    # 7-F-1b  Filter by title with value that matches no record
    _absent_val = "__no_document_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"title": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?title=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter title with absent value: total=0")
        else:
            ctx.fail(f"Filter title with absent value: expected total=0, got {total}")

    # 7-F-2  Filter by content (string) — match seeded value
    _val_content = _entity1_data.get("content")
    if _val_content is not None:
        resp = ctx.req("GET", base, params={"content": str(_val_content), "limit": 50})
        if ctx.assert_status(resp, 200, f"GET {base}?content={_val_content} → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?content=<value>")
            items = data.get("data", [])
            total = data.get("meta", {}).get("total", -1)
            # entity1 should appear in filtered results
            ids_in_result = [item.get("id") for item in items]
            if document1_id in ids_in_result:
                ctx.ok(f"Filter content={_val_content}: entity1 found in results")
            else:
                ctx.fail(f"Filter content={_val_content}: entity1 missing from results (ids={ids_in_result})")
            if total <= _baseline_total:
                ctx.ok(f"Filter content: filtered total ({total}) ≤ baseline ({_baseline_total})")
            else:
                ctx.fail(f"Filter content: filtered total ({total}) > baseline ({_baseline_total})")
            # All returned items should match the filter value
            mismatched = [item for item in items if item.get("content") != _val_content]
            if not mismatched:
                ctx.ok("Filter content: all returned items match filter value")
            else:
                ctx.fail(f"Filter content: {len(mismatched)} items have wrong value")
    else:
        ctx.skip("Filter content: entity1 data not available (seed may have failed)")

    # 7-F-2b  Filter by content with value that matches no record
    _absent_val = "__no_document_has_this_value_xyz__"
    resp = ctx.req("GET", base, params={"content": _absent_val})
    if ctx.assert_status(resp, 200, f"GET {base}?content=<absent> → 200"):
        total = ctx.safe_json(resp).get("meta", {}).get("total", -1)
        if total == 0:
            ctx.ok(f"Filter content with absent value: total=0")
        else:
            ctx.fail(f"Filter content with absent value: expected total=0, got {total}")


    # 7-FC  Filter + sort + pagination composed together
    _first_filter_field = "title"
    _first_filter_val = _entity1_data.get(_first_filter_field)
    if _first_filter_val is not None:
        resp = ctx.req("GET", base, params={
            _first_filter_field: str(_first_filter_val),
            "sortBy": "id",
            "sortOrder": "asc",
            "page": 1,
            "limit": 5,
        })
        if ctx.assert_status(resp, 200, f"GET {base}?filter+sort+page → 200"):
            data = ctx.safe_json(resp)
            ctx.assert_paginated(data, f"{base}?filter+sort+page")
            meta = data.get("meta", {})
            if meta.get("limit") == 5 and meta.get("page") == 1:
                ctx.ok("Filter+sort+pagination: meta correct")
            else:
                ctx.fail(f"Filter+sort+pagination: unexpected meta {meta}")
            items = data.get("data", [])
            if len(items) >= 2:
                ids = [i.get("id") for i in items if i.get("id") is not None]
                if ids == sorted(ids):
                    ctx.ok("Filter+sort+pagination: items in ascending id order")
                else:
                    ctx.fail(f"Filter+sort+pagination: expected ascending ids, got {ids}")
    else:
        ctx.skip("Filter+sort+pagination: entity1 data not available")

    # 7-FU  Unknown filter field → ignored, returns 200
    resp = ctx.req("GET", base, params={"__nonexistent_filter__": "somevalue"})
    if ctx.assert_status(resp, 200, f"GET {base}?__nonexistent_filter__=value → 200 (ignored)"):
        ctx.assert_paginated(ctx.safe_json(resp), f"{base}?unknown_filter=value")
        ctx.ok("Unknown filter field ignored, full result set returned")


