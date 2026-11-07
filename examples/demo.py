#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp==2.0.0"]
# ///
"""Real MCP calls, synthetic enquiries. No API key or model subscription needed.

    uv run examples/demo.py
    uv run examples/demo.py --live-read-only

Default: fixed isolated review endpoint; only server-provided synthetic fixtures.
Live mode: public provider search only. This example never submits to production.
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from uuid import uuid4

from mcp import Client

REVIEW = "https://api.eucompliance.tools/exchange-review/mcp"
DISCOVERY = "https://api.eucompliance.tools/exchange/discover/"
CASES = (
    (
        "L&G",
        "plumbing",
        "direct_installation_inquiry_options",
        "submit_direct_installation_inquiry",
        "lg-installationen",
    ),
    (
        "Sauber mit Sam",
        "office-cleaning",
        "direct_cleaning_inquiry_options",
        "submit_direct_cleaning_inquiry",
        "sauber-mit-sam",
    ),
)


def require_review(data):
    if data.get("environment") != "synthetic_review_only":
        raise RuntimeError("Expected isolated review environment; stopped.")


def fixture_from(options, recipient):
    require_review(options)
    if options.get("mail_delivery") != "disabled":
        raise RuntimeError("Review mail is not explicitly disabled; stopped.")
    payload = options.get("synthetic_test_payload", {})
    contact = payload.get("contact", {})
    if (
        payload.get("recipient") != recipient
        or contact.get("email") != "review@example.invalid"
        or contact.get("name") != "SYNTHETIC REVIEW"
        or not payload.get("description", "").startswith("SYNTHETIC REVIEW ONLY:")
    ):
        raise RuntimeError("Expected recipient-specific synthetic fixture; stopped.")
    return payload


async def call(client, name, args=None):
    result = await client.call_tool(name, args or {})
    if result.is_error:
        # Do not dump arbitrary remote error content into logs.
        raise RuntimeError(f"{name} returned a tool error; inspect the service status.")
    data = result.structured_content
    if data is None:
        for block in result.content:
            if block.type == "text":
                try:
                    candidate = json.loads(block.text)
                except (ValueError, TypeError):
                    continue
                if isinstance(candidate, dict):
                    data = candidate
                    break
    if not isinstance(data, dict):
        raise RuntimeError(f"{name} did not return structured JSON.")
    return data


async def run(live=False, json_output=False):
    started = time.monotonic()

    def emit(step, message, **data):
        event = {
            "elapsed_s": round(time.monotonic() - started, 3),
            "step": step,
            "message": message,
            **data,
        }
        print(json.dumps(event) if json_output else message, flush=True)

    endpoint = DISCOVERY if live else REVIEW
    emit(
        "start",
        "LIVE READ-ONLY: provider discovery; no enquiries."
        if live
        else "SYNTHETIC DEMO: real MCP calls; no mail, booking or payment.",
        endpoint=endpoint,
    )
    async with Client(endpoint, read_timeout_seconds=25) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        expected = {"find_service_providers"}
        if not live:
            expected.update(
                x for _, _, options, submit, _ in CASES for x in (options, submit)
            )
        if not expected.issubset(names):
            raise RuntimeError("Required tools are unavailable; stopped.")
        emit(
            "connected",
            f"Connected: {len(names)} tools discovered.",
            tool_count=len(names),
        )
        for label, trade, options_name, submit_name, recipient in CASES:
            providers = await call(
                client,
                "find_service_providers",
                {"country": "AT", "region": "wien", "trade": trade},
            )
            if not live:
                require_review(providers)
            count = len(providers.get("items", []))
            emit(
                "search",
                f"{label}: {count} matching provider profile(s) in Vienna.",
                provider=label,
                matches=count,
            )
            if live:
                continue
            options = await call(client, options_name)
            payload = fixture_from(options, recipient)
            emit(
                "fixture",
                f"{label}: synthetic fixture loaded; mail explicitly disabled.",
                provider=label,
            )
            args = {
                "payload": payload,
                "idempotency_key": "github-demo-" + str(uuid4()),
            }
            receipt = await call(client, submit_name, args)
            require_review(receipt)
            if (
                receipt.get("mail_delivery") != "disabled"
                or receipt.get("booking_confirmed") is not False
                or not receipt.get("inquiry_id")
            ):
                raise RuntimeError("Unexpected review receipt; stopped before retry.")
            emit(
                "receipt",
                f"{label}: synthetic enquiry received; no booking.",
                provider=label,
                inquiry_id=receipt["inquiry_id"],
                mail_delivery=receipt["mail_delivery"],
            )
            repeat = await call(client, submit_name, args)
            if repeat != receipt:
                raise RuntimeError("Repeated request returned a different receipt.")
            emit(
                "retry",
                f"{label}: identical retry returned the same receipt.",
                provider=label,
                idempotency_passed=True,
            )
    emit(
        "done",
        "PASS: live searches only; no submissions."
        if live
        else "PASS: both synthetic enquiry flows; mail disabled; identical retry receipts.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live-read-only",
        action="store_true",
        help="Search public profiles; never submit an enquiry.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit minimal JSON events, without payloads or customer data.",
    )
    args = parser.parse_args()
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.WARNING)
    try:
        asyncio.run(run(args.live_read_only, args.json))
    except (Exception, KeyboardInterrupt):
        print(
            "Demo stopped. No production enquiry was attempted. Check connectivity, service status or rate limits before running again.",
            file=sys.stderr,
        )
        sys.exit(1)
