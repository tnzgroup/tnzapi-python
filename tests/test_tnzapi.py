import pytest

from tnzapi import TNZAPI
from tnzapi.api.v300.messaging import Messaging as V3Messaging
from tnzapi.api.v300.reports import Reports as V3Reports
from tnzapi.api.v300.actions import Actions as V3Actions
from tnzapi.legacy.pre_v203.send import Send as LegacySend
from tnzapi.legacy.pre_v203.get import Get as LegacyGet
from tnzapi.legacy.pre_v203.set import Set as LegacySet


def test_messaging_routes_to_v3_facade():
    client = TNZAPI(AuthToken="test-token")

    assert isinstance(client.Messaging, V3Messaging)
    assert client.Messaging.user.AuthToken == "test-token"


def test_reports_routes_to_v3_facade():
    client = TNZAPI(AuthToken="test-token")

    assert isinstance(client.Reports, V3Reports)
    assert client.Reports.user.AuthToken == "test-token"


def test_actions_routes_to_v3_facade():
    client = TNZAPI(AuthToken="test-token")

    assert isinstance(client.Actions, V3Actions)
    assert client.Actions.user.AuthToken == "test-token"


def test_base_url_kwarg_passed_through_to_v3_facades():
    client = TNZAPI(AuthToken="test-token", BaseURL="http://localhost:9090/api/v3.00")

    assert client.Messaging.user.BaseURL == "http://localhost:9090/api/v3.00"


def test_messaging_property_is_cached_across_accesses():
    client = TNZAPI(AuthToken="test-token")

    assert client.Messaging is client.Messaging


def test_messaging_without_auth_token_raises():
    client = TNZAPI()

    with pytest.raises(ValueError):
        client.Messaging


def test_addressbook_now_routes_to_v3_facade():
    from tnzapi.api.v300.addressbook import Addressbook as V3Addressbook

    client = TNZAPI(AuthToken="test-token")

    assert isinstance(client.Addressbook, V3Addressbook)
    assert client.Addressbook.user.AuthToken == "test-token"


def test_addressbook_property_is_cached_across_accesses():
    client = TNZAPI(AuthToken="test-token")

    assert client.Addressbook is client.Addressbook


def test_send_get_set_still_route_to_pre_v203_legacy_classes():
    client = TNZAPI(AuthToken="test-token")

    assert isinstance(client.Send, LegacySend)
    assert isinstance(client.Get, LegacyGet)
    assert isinstance(client.Set, LegacySet)


def test_send_and_messaging_do_not_share_a_cache_slot():
    client = TNZAPI(AuthToken="test-token")

    client.Send

    assert isinstance(client.Messaging, V3Messaging)


def test_get_and_reports_do_not_share_a_cache_slot():
    client = TNZAPI(AuthToken="test-token")

    client.Get

    assert isinstance(client.Reports, V3Reports)


def test_set_and_actions_do_not_share_a_cache_slot():
    client = TNZAPI(AuthToken="test-token")

    client.Set

    assert isinstance(client.Actions, V3Actions)


def test_optout_routes_to_v3_optout_class():
    from tnzapi.api.v300.optout.builders.optout import OptOut

    client = TNZAPI(AuthToken="test-token")

    assert isinstance(client.OptOut, OptOut)
    assert client.OptOut.user.AuthToken == "test-token"


def test_optout_property_is_cached_across_accesses():
    client = TNZAPI(AuthToken="test-token")

    assert client.OptOut is client.OptOut


def test_optout_without_auth_token_raises():
    client = TNZAPI()

    with pytest.raises(ValueError):
        client.OptOut


def test_set_abort_no_longer_raises_module_not_found_error():
    # tnzapi/legacy/pre_v203/set/__init__.py used to import from
    # tnzapi.api.actions.abort (missing a .requests segment) - this was a
    # real, confirmed ModuleNotFoundError in production before Phase 7's
    # path fix. This test just proves the import resolves; it doesn't need
    # network access since it never calls Run().
    client = TNZAPI(AuthToken="test-token")

    abort = client.Set.Abort()

    assert abort is not None
