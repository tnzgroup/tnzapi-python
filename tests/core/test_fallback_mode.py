from tnzapi.core.fallback_mode import normalize_fallback_mode


def test_none_passes_through_unchanged():
    assert normalize_fallback_mode(None) is None


def test_list_of_values_is_comma_joined():
    assert normalize_fallback_mode(["Voice", "RCS"]) == "Voice, RCS"


def test_list_translates_whatsapp_to_wapp():
    assert normalize_fallback_mode(["Voice", "WhatsApp"]) == "Voice, WAPP"


def test_single_item_list_has_no_trailing_comma():
    assert normalize_fallback_mode(["SMS"]) == "SMS"


def test_tuple_is_also_accepted():
    assert normalize_fallback_mode(("Voice", "RCS")) == "Voice, RCS"


def test_plain_string_passes_through_unchanged_for_backward_compat():
    assert normalize_fallback_mode("SMS") == "SMS"
    assert normalize_fallback_mode("Voice") == "Voice"


def test_plain_whatsapp_string_translates_to_wapp():
    assert normalize_fallback_mode("WhatsApp") == "WAPP"


def test_prejoined_multi_value_string_is_not_retokenized():
    # A caller who already pre-joined a string themselves is left completely
    # alone - normalize_fallback_mode only tokenizes actual list/tuple input,
    # never splits an opaque string on its own initiative.
    assert normalize_fallback_mode("Voice, WhatsApp") == "Voice, WhatsApp"
