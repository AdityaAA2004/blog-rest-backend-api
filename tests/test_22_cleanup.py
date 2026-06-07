"""
Section 22 — Cleanup: delete all test data created during the suite.

Order: child entities first (reverse dependency order).
"""

from helpers import TestContext, section


def run(ctx: TestContext) -> None:
    section("22 · CLEANUP — Remove test data")

    token1 = ctx.state.get("user1_token")
    token2 = ctx.state.get("user2_token")

    def _delete(path: str, token: str | None, label: str) -> None:
        if not token:
            ctx.warn(f"Cleanup: no token for {label}, skipping")
            return
        resp = ctx.req("DELETE", path, token=token)
        if resp.status_code == 403:
            # First token didn't own this resource; try the other user's token
            fallback = token2 if token is token1 else token1
            if fallback:
                resp = ctx.req("DELETE", path, token=fallback)
        if resp.status_code in (204, 404):
            ctx.ok(f"Cleanup: {label} removed (HTTP {resp.status_code})")
        elif resp.status_code == 403:
            ctx.warn(f"Cleanup: {label} → 403 Forbidden (neither token owns this resource)")
        else:
            ctx.warn(f"Cleanup: {label} → unexpected HTTP {resp.status_code}")

    # Cleanup comments
    comment_cleanups = [
        (ctx.state.get("comment1_id"), token1, "comment1_id"),
        (ctx.state.get("comment2_id"), token1, "comment2_id"),
        (ctx.state.get("comment3_id"), token1, "comment3_id"),
        (ctx.state.get("spoofed_comment_id"), token1, "spoofed_comment_id"),
        (ctx.state.get("long_title_comment_id"), token1, "long_title_comment_id"),
        (ctx.state.get("long_content_comment_id"), token1, "long_content_comment_id"),
        (ctx.state.get("xss_comment_id"), token1, "xss_comment_id"),
        (ctx.state.get("unicode_comment_id"), token1, "unicode_comment_id"),
    ]
    for eid, tok, label in comment_cleanups:
        if eid:
            _delete("/api/comments/" + str(eid), tok, label)

    # Cleanup posts
    post_cleanups = [
        (ctx.state.get("post1_id"), token1, "post1_id"),
        (ctx.state.get("post2_id"), token1, "post2_id"),
        (ctx.state.get("post3_id"), token1, "post3_id"),
        (ctx.state.get("spoofed_post_id"), token1, "spoofed_post_id"),
        (ctx.state.get("long_title_post_id"), token1, "long_title_post_id"),
        (ctx.state.get("long_content_post_id"), token1, "long_content_post_id"),
        (ctx.state.get("xss_post_id"), token1, "xss_post_id"),
        (ctx.state.get("unicode_post_id"), token1, "unicode_post_id"),
    ]
    for eid, tok, label in post_cleanups:
        if eid:
            _delete("/api/posts/" + str(eid), tok, label)

    # Cleanup documents
    document_cleanups = [
        (ctx.state.get("document1_id"), token1, "document1_id"),
        (ctx.state.get("document2_id"), token1, "document2_id"),
        (ctx.state.get("document3_id"), token1, "document3_id"),
        (ctx.state.get("spoofed_document_id"), token1, "spoofed_document_id"),
        (ctx.state.get("long_title_document_id"), token1, "long_title_document_id"),
        (ctx.state.get("long_content_document_id"), token1, "long_content_document_id"),
        (ctx.state.get("xss_document_id"), token1, "xss_document_id"),
        (ctx.state.get("unicode_document_id"), token1, "unicode_document_id"),
    ]
    for eid, tok, label in document_cleanups:
        if eid:
            _delete("/api/documents/" + str(eid), tok, label)

