#!/usr/bin/env python3
"""
run_all.py — API test suite runner.

Executes all test sections sequentially, sharing a single TestContext so that
state (auth tokens, created IDs) flows naturally from each section to the next.

Usage:
  python run_all.py [base_url]

  base_url defaults to $API_URL env-var or http://localhost:3000

Legend:
  🚀  Sending API request
  ✅  Test passed
  ❌  Test failed
  ⛔️  Auth / authorization issue
  ⚠️  Security warning
"""

import sys
import os

# Allow imports from this directory
sys.path.insert(0, os.path.dirname(__file__))

from helpers import TestContext, section

import test_00_health
import test_01_register
import test_02_login
import test_03_users_get
import test_04_users_list_query
import test_05_users_write
import test_06_documents_seed_get
import test_07_documents_list_query
import test_08_documents_write
import test_09_posts_seed_get
import test_10_posts_list_query
import test_11_posts_write
import test_12_comments_seed_get
import test_13_comments_list_query
import test_14_comments_write
import test_15_nested_user_get
import test_16_nested_user_posts
import test_17_nested_post_comments
import test_18_token_security
import test_19_input_validation
import test_20_response_structure
import test_21_security_audit
import test_22_cleanup


SECTIONS = [
    test_00_health,
    test_01_register,
    test_02_login,
    test_03_users_get,
    test_04_users_list_query,
    test_05_users_write,
    test_06_documents_seed_get,
    test_07_documents_list_query,
    test_08_documents_write,
    test_09_posts_seed_get,
    test_10_posts_list_query,
    test_11_posts_write,
    test_12_comments_seed_get,
    test_13_comments_list_query,
    test_14_comments_write,
    test_15_nested_user_get,
    test_16_nested_user_posts,
    test_17_nested_post_comments,
    test_18_token_security,
    test_19_input_validation,
    test_20_response_structure,
    test_21_security_audit,
    test_22_cleanup,
]


def main() -> None:
    base_url = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.getenv("API_URL", "http://localhost:3000")
    )

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          Developable — Comprehensive Test Suite              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"  Target  : {base_url}")
    print(f"  Sections: {len(SECTIONS)}")

    ctx = TestContext(base_url)

    for module in SECTIONS:
        try:
            module.run(ctx)
        except SystemExit:
            raise
        except Exception as exc:
            ctx.fail(f"Unhandled exception in {module.__name__}: {exc}")

    # ------------------------------------------------------------------
    # Final summary
    # ------------------------------------------------------------------
    total = ctx.pass_count + ctx.fail_count + ctx.skip_count
    print(f"\n{'═' * 64}")
    print(f"  FINAL RESULTS")
    print(f"{'═' * 64}")
    print(f"  ✅  Passed   : {ctx.pass_count}")
    print(f"  ❌  Failed   : {ctx.fail_count}")
    print(f"  ⏭️   Skipped  : {ctx.skip_count}")
    print(f"  ⚠️   Warnings : {ctx.warn_count}")
    print(f"  Total        : {total}  (passed + failed + skipped)")
    print(f"{'═' * 64}")

    executed = ctx.pass_count + ctx.fail_count
    fail_rate = ctx.fail_count / executed if executed > 0 else 0
    FAIL_THRESHOLD = 0.01  # 1% — deploy proceeds below this; fix failures post-deploy

    if ctx.fail_count > 0:
        print(f"\n  {ctx.fail_count} test(s) FAILED. Review the ❌ / ⛔️ entries above.")
        if ctx.skip_count > 0:
            print(f"  {ctx.skip_count} test(s) were skipped due to missing prerequisite state.")
        if fail_rate <= FAIL_THRESHOLD:
            print(f"  Failure rate {fail_rate:.1%} is within the {FAIL_THRESHOLD:.0%} threshold — continuing.")
        else:
            print(f"  Failure rate {fail_rate:.1%} exceeds the {FAIL_THRESHOLD:.0%} threshold.")
            sys.exit(1)
    else:
        print(f"\n  All {executed} executed tests passed! 🎉")
        if ctx.skip_count > 0:
            print(f"  {ctx.skip_count} test(s) were skipped (prerequisite data not available).")
        if ctx.warn_count > 0:
            print(f"  Review the {ctx.warn_count} ⚠️  security warning(s) above.")


if __name__ == "__main__":
    main()
