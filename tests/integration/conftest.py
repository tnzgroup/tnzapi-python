import os

import pytest

from tnzapi import TNZAPI


@pytest.fixture(autouse=True)
def _isolate_from_local_env():
    # Overrides tests/conftest.py's autouse fixture of the same name: unit tests
    # must never see a developer's real .env/.env.local/.env.test values, but
    # this whole subtree is the one place in the suite that needs them - they're
    # already loaded into os.environ by tests/conftest.py's module-level
    # load_dotenv() calls, so simply not clearing them here is enough.
    yield


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        pytest.skip(f"{name} not set - copy .env.test.example to .env.test and fill in a real value to run this test")
    return value


@pytest.fixture(scope="session")
def live_client():
    # Having TNZ_AUTH_TOKEN configured is not itself permission to fire live
    # requests - a developer or CI job can have a real token set for unrelated
    # reasons and not realize `pytest -m integration` sends real messages.
    # TNZ_RUN_LIVE_TESTS=1 is a second, deliberate confirmation that running
    # this suite (real sends, real cost) is actually intended right now.
    if os.environ.get("TNZ_RUN_LIVE_TESTS") != "1":
        pytest.skip("TNZ_RUN_LIVE_TESTS=1 not set - this suite sends real messages and can incur real cost; set it explicitly to confirm that's intended")
    auth_token = _require_env("TNZ_AUTH_TOKEN")
    return TNZAPI(AuthToken=auth_token)


@pytest.fixture
def workflow_send_allowed():
    # Workflow has no Mode="Test" equivalent (see test_messaging_send.py) - the
    # configured WorkflowTemplateID actually executes on every run. Require a
    # separate, explicit confirmation beyond TNZ_RUN_LIVE_TESTS so triggering
    # it is never just a side effect of running the rest of the suite.
    if os.environ.get("TNZ_ALLOW_WORKFLOW_SEND") != "1":
        pytest.skip(
            "TNZ_ALLOW_WORKFLOW_SEND=1 not set - confirm TNZ_TEST_WORKFLOW_TEMPLATE_ID "
            "points at a template that's safe to trigger repeatedly before setting this"
        )


@pytest.fixture
def test_mobile():
    return _require_env("TNZ_TEST_MOBILE")


@pytest.fixture
def test_fax():
    return _require_env("TNZ_TEST_FAX")


@pytest.fixture
def test_email():
    return _require_env("TNZ_TEST_EMAIL")


@pytest.fixture
def test_workflow_template_id():
    return _require_env("TNZ_TEST_WORKFLOW_TEMPLATE_ID")


@pytest.fixture
def test_whatsapp_template_id():
    return _require_env("TNZ_TEST_WHATSAPP_TEMPLATE_ID")


@pytest.fixture
def test_whatsapp_from_number():
    return _require_env("TNZ_TEST_WHATSAPP_FROM_NUMBER")


@pytest.fixture
def test_message_id():
    return _require_env("TNZ_TEST_MESSAGE_ID")


@pytest.fixture
def test_message_channel():
    return _require_env("TNZ_TEST_MESSAGE_CHANNEL")
