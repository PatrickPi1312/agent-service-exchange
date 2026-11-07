"""Offline checks for the demo's write boundary; no service calls or real data."""

import contextlib
import copy
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import demo


def options():
    return {
        "environment": "synthetic_review_only",
        "mail_delivery": "disabled",
        "synthetic_test_payload": {
            "recipient": "lg-installationen",
            "contact": {"email": "review@example.invalid", "name": "SYNTHETIC REVIEW"},
            "description": "SYNTHETIC REVIEW ONLY: offline fixture",
        },
    }


class FixtureBoundaryTests(unittest.TestCase):
    def test_exact_synthetic_fixture_is_preserved(self):
        source = options()
        original = copy.deepcopy(source)
        self.assertEqual(
            demo.fixture_from(source, "lg-installationen"),
            original["synthetic_test_payload"],
        )
        self.assertEqual(source, original)

    def test_live_environment_or_mail_delivery_is_rejected(self):
        for field, value in (
            ("environment", "production"),
            ("environment", None),
            ("mail_delivery", "enabled"),
            ("mail_delivery", None),
        ):
            with self.subTest(field=field, value=value):
                source = options()
                source[field] = value
                with self.assertRaises(RuntimeError):
                    demo.fixture_from(source, "lg-installationen")

    def test_other_recipient_or_non_fixture_content_is_rejected(self):
        mutations = (
            ("recipient", "sauber-mit-sam"),
            ("description", "ordinary enquiry"),
            (
                "contact",
                {"email": "different@example.invalid", "name": "SYNTHETIC REVIEW"},
            ),
            (
                "contact",
                {"email": "review@example.invalid", "name": "Different fixture"},
            ),
        )
        for field, value in mutations:
            with self.subTest(field=field, value=value):
                source = options()
                source["synthetic_test_payload"][field] = value
                with self.assertRaises(RuntimeError):
                    demo.fixture_from(source, "lg-installationen")


class ClientBoundaryTests(unittest.IsolatedAsyncioTestCase):
    async def test_live_mode_only_uses_search_on_discovery_endpoint(self):
        calls = []

        class Client:
            def __init__(self, endpoint, **kwargs):
                self.endpoint = endpoint

            async def __aenter__(self):
                self_test.assertEqual(self.endpoint, demo.DISCOVERY)
                return self

            async def __aexit__(self, *args):
                pass

            async def list_tools(self):
                return SimpleNamespace(
                    tools=[SimpleNamespace(name="find_service_providers")]
                )

            async def call_tool(self, name, args):
                calls.append((name, args))
                return SimpleNamespace(is_error=False, structured_content={"items": []})

        self_test = self
        with (
            patch.object(demo, "Client", Client),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            await demo.run(live=True)
        self.assertEqual([name for name, _ in calls], ["find_service_providers"] * 2)

    async def test_tool_error_stops_before_reading_remote_error_data(self):
        class Client:
            async def call_tool(self, name, args):
                return SimpleNamespace(is_error=True)

        with self.assertRaises(RuntimeError):
            await demo.call(Client(), "find_service_providers")

    async def test_text_json_responses_are_supported(self):
        class Client:
            async def call_tool(self, name, args):
                return SimpleNamespace(
                    is_error=False,
                    structured_content=None,
                    content=[
                        SimpleNamespace(type="text", text=json.dumps({"items": []})),
                    ],
                )

        self.assertEqual(
            await demo.call(Client(), "find_service_providers"), {"items": []}
        )


if __name__ == "__main__":
    unittest.main()
