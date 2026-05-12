"""API response envelope regression tests."""

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError

from common.responses import error_response
from common.utils import custom_exception_handler


class ApiResponseEnvelopeTests(SimpleTestCase):
    """Validate structured error payloads without requiring a test database."""

    def test_error_response_should_include_structured_error_details(self):
        """Business errors should keep code/msg/data and expose stable details."""
        response = error_response(
            msg="参数错误",
            code=400,
            error_code="VALIDATION_ERROR",
            errors={"username": ["该字段不能为空。"]},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], 400)
        self.assertEqual(response.data["msg"], "参数错误")
        self.assertEqual(
            response.data["data"],
            {"errors": {"username": ["该字段不能为空。"]}},
        )
        self.assertEqual(response.data["error"]["type"], "VALIDATION_ERROR")
        self.assertEqual(
            response.data["error"]["details"],
            {"username": ["该字段不能为空。"]},
        )

    def test_exception_handler_should_flatten_field_message(self):
        """DRF validation errors should preserve field context in the message."""
        response = custom_exception_handler(
            ValidationError({"username": ["该字段不能为空。"]}),
            {"request": None},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["msg"], "username: 该字段不能为空。")
        self.assertEqual(response.data["error"]["type"], "ValidationError")
        self.assertEqual(
            response.data["data"],
            {"errors": {"username": ["该字段不能为空。"]}},
        )
