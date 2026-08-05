from dataclasses import dataclass, field

import pytest

from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tnzapi.core.model_proxy import ModelRequestMixin, project_model, require_id, resolve_id


@dataclass
class FakeResponseDTO:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    ID: str = None
    Owner: str = None
    Name: str = None
    Tags: list = field(default_factory=list)


@dataclass
class FakeRequestDTO:
    Name: str = None
    Tags: list = field(default_factory=list)
    Destinations: list = field(default_factory=list)
    Files: list = field(default_factory=list)


class FakeRequest(ModelRequestMixin):

    _request_model_cls = FakeRequestDTO

    def __init__(self):
        self.user = "fake-user"
        self.http = "fake-http"
        self._reset()


def test_set_applies_known_fields_and_is_chainable():
    req = FakeRequest()

    result = req.Set(Name="Jane")

    assert result is req
    assert req.Name == "Jane"


def test_set_raises_on_unknown_field():
    req = FakeRequest()

    with pytest.raises(ValueError):
        req.Set(Bogus="x")


def test_build_returns_independent_deep_copy():
    req = FakeRequest()
    req.Set(Name="Jane", Tags=["a"])

    model = req.Build()

    assert isinstance(model, FakeRequestDTO)
    assert model.Name == "Jane"

    req.Name = "Changed"
    req.Tags.append("b")
    assert model.Name == "Jane"
    assert model.Tags == ["a"]


def test_build_request_body_drops_empty_fields():
    req = FakeRequest()
    req.Set(Name="Jane")

    body = req._build_request_body()

    assert body == {"Name": "Jane"}


def test_first_invalid_field_reports_first_unknown_key():
    req = FakeRequest()

    assert req._first_invalid_field({"Name": "Jane"}) is None
    assert req._first_invalid_field({"Bogus": "x"}) == "Bogus"


def test_getattr_raises_attribute_error_instead_of_recursing_when_data_unset():
    obj = FakeRequest.__new__(FakeRequest)

    with pytest.raises(AttributeError):
        obj.Name


def test_user_and_http_are_real_instance_attributes_not_proxied():
    req = FakeRequest()

    assert req.user == "fake-user"
    assert req.http == "fake-http"


def test_first_invalid_field_accepts_valid_destination_dicts():
    req = FakeRequest()

    assert req._first_invalid_field({"Destinations": [{"ToNumber": "+64211111111"}]}) is None


def test_first_invalid_field_reports_unknown_key_inside_a_destination_dict():
    req = FakeRequest()

    assert req._first_invalid_field({"Destinations": [{"ToNunber": "+64211111111"}]}) == "ToNunber"


def test_first_invalid_field_accepts_destination_instances_in_the_list():
    req = FakeRequest()

    assert req._first_invalid_field({"Destinations": [Destination(ToNumber="+64211111111")]}) is None


def test_set_raises_on_unknown_key_inside_a_destination_dict():
    req = FakeRequest()

    with pytest.raises(ValueError, match="ToNunber"):
        req.Set(Destinations=[{"ToNunber": "+64211111111"}])


def test_apply_fields_converts_destination_instances_to_filtered_dicts():
    req = FakeRequest()

    req.Set(Destinations=[Destination(ToNumber="+64211111111", FirstName="Alice")])

    assert req.Destinations == [{"ToNumber": "+64211111111", "FirstName": "Alice"}]


def test_apply_fields_leaves_valid_dicts_unchanged():
    req = FakeRequest()

    req.Set(Destinations=[{"ToNumber": "+64211111111"}])

    assert req.Destinations == [{"ToNumber": "+64211111111"}]


def test_apply_fields_filters_out_empty_destination_instances():
    req = FakeRequest()

    req.Set(Destinations=[Destination(), Destination(ToNumber="+64211111111")])

    assert req.Destinations == [{"ToNumber": "+64211111111"}]


def test_first_invalid_field_does_not_crash_on_a_non_list_destinations_value():
    req = FakeRequest()

    assert req._first_invalid_field({"Destinations": None}) is None


def test_set_does_not_crash_on_destinations_equal_none():
    req = FakeRequest()

    req.Set(Destinations=None)

    assert req.Destinations is None


def test_apply_fields_converts_a_bare_string_using_the_primary_key():
    req = FakeRequest()

    req.Set(Destinations=["+64211111111"])

    assert req.Destinations == [{"ToNumber": "+64211111111"}]


def test_apply_fields_converts_a_mix_of_strings_dicts_and_destination_instances():
    req = FakeRequest()

    req.Set(Destinations=["+64211111111", {"ToNumber": "+64221111111"}, Destination(ToNumber="+64231111111")])

    assert req.Destinations == [
        {"ToNumber": "+64211111111"},
        {"ToNumber": "+64221111111"},
        {"ToNumber": "+64231111111"},
    ]


def test_first_invalid_field_rejects_a_non_string_non_dict_non_destination_item():
    req = FakeRequest()

    assert req._first_invalid_field({"Destinations": [123]}) == "Destinations item of type int"


def test_set_raises_on_a_non_string_non_dict_non_destination_destinations_item():
    req = FakeRequest()

    with pytest.raises(ValueError, match="Destinations item of type int"):
        req.Set(Destinations=[123])

def test_project_model_keeps_only_target_class_fields():
    response = FakeResponseDTO(Result="Success", ID="r-1", Owner="admin", Name="Jane", Tags=["a"])

    projected = project_model(response, FakeRequestDTO)

    assert isinstance(projected, FakeRequestDTO)
    assert projected.Name == "Jane"
    assert projected.Tags == ["a"]
    assert not hasattr(projected, "Result")
    assert not hasattr(projected, "ID")
    assert not hasattr(projected, "Owner")


def test_project_model_returns_independent_copy():
    response = FakeResponseDTO(Name="Jane", Tags=["a"])

    projected = project_model(response, FakeRequestDTO)
    projected.Tags.append("b")

    assert response.Tags == ["a"]


def test_resolve_id_extracts_field_from_a_response_instance():
    response = FakeResponseDTO(ID="r-1", Name="Jane")

    assert resolve_id(response, FakeResponseDTO, "ID") == "r-1"


def test_resolve_id_passes_through_a_plain_string_unchanged():
    assert resolve_id("r-1", FakeResponseDTO, "ID") == "r-1"


def test_resolve_id_raises_when_response_id_field_is_unset():
    response = FakeResponseDTO(Name="Jane")

    with pytest.raises(ValueError, match="ID"):
        resolve_id(response, FakeResponseDTO, "ID")


def test_resolve_id_accepts_a_legitimate_falsy_id_like_zero():
    response = FakeResponseDTO(ID=0, Name="Jane")

    assert resolve_id(response, FakeResponseDTO, "ID") == 0


def test_resolve_id_raises_when_response_id_field_is_empty_string():
    response = FakeResponseDTO(ID="", Name="Jane")

    with pytest.raises(ValueError, match="ID"):
        resolve_id(response, FakeResponseDTO, "ID")


def test_resolve_id_raises_when_none_is_passed_directly():
    with pytest.raises(ValueError, match="ID"):
        resolve_id(None, FakeResponseDTO, "ID")


def test_resolve_id_raises_when_an_empty_string_is_passed_directly():
    with pytest.raises(ValueError, match="ID"):
        resolve_id("", FakeResponseDTO, "ID")


def test_resolve_id_accepts_a_legitimate_falsy_id_like_zero_passed_directly():
    assert resolve_id(0, FakeResponseDTO, "ID") == 0


def test_require_id_passes_through_a_valid_id_unchanged():
    assert require_id("c-001", "ContactID") == "c-001"


def test_require_id_accepts_a_legitimate_falsy_id_like_zero():
    assert require_id(0, "ContactID") == 0


def test_require_id_raises_when_none():
    with pytest.raises(ValueError, match="ContactID"):
        require_id(None, "ContactID")


def test_require_id_raises_when_empty_string():
    with pytest.raises(ValueError, match="ContactID"):
        require_id("", "ContactID")


def test_first_invalid_field_accepts_valid_files_dict():
    req = FakeRequest()
    assert req._first_invalid_field({"Files": [{"Name": "a.pdf", "Data": "base64=="}]}) is None


def test_first_invalid_field_rejects_unknown_files_dict_key():
    req = FakeRequest()
    assert req._first_invalid_field({"Files": [{"Name": "a.pdf", "Bogus": "x"}]}) == "Bogus"


def test_first_invalid_field_accepts_file_attachment_instance_in_files():
    req = FakeRequest()
    assert req._first_invalid_field({"Files": [FileAttachment(Name="a.pdf", Data="base64==")]}) is None


def test_first_invalid_field_accepts_real_path_string_in_files(tmp_path):
    path = tmp_path / "a.pdf"
    path.write_bytes(b"x")
    req = FakeRequest()
    assert req._first_invalid_field({"Files": [str(path)]}) is None


def test_first_invalid_field_rejects_non_path_string_in_files():
    req = FakeRequest()
    result = req._first_invalid_field({"Files": ["definitely-not-a-real-file.pdf"]})
    assert result is not None
    assert "definitely-not-a-real-file.pdf" in result


def test_first_invalid_field_rejects_bad_type_in_files():
    req = FakeRequest()
    assert req._first_invalid_field({"Files": [123]}) == "Files item of type int"


def test_set_raises_on_files_with_unknown_key():
    req = FakeRequest()
    with pytest.raises(ValueError, match="Unknown argument: Bogus"):
        req.Set(Files=[{"Name": "a.pdf", "Bogus": "x"}])


def test_set_normalizes_files_list_of_dicts():
    req = FakeRequest()
    req.Set(Files=[{"Name": "a.pdf", "Data": "base64=="}])
    assert req.Files == [{"Name": "a.pdf", "Data": "base64=="}]


def test_set_normalizes_files_list_of_file_attachments():
    req = FakeRequest()
    req.Set(Files=[FileAttachment(Name="a.pdf", Data="base64==")])
    assert req.Files == [{"Name": "a.pdf", "Data": "base64=="}]


def test_set_normalizes_files_bare_path_strings(tmp_path):
    path1 = tmp_path / "a.pdf"
    path1.write_bytes(b"one")
    path2 = tmp_path / "b.pdf"
    path2.write_bytes(b"two")
    req = FakeRequest()

    req.Set(Files=[str(path1), str(path2)])

    assert [f["Name"] for f in req.Files] == ["a.pdf", "b.pdf"]


def test_set_raises_on_files_bare_non_path_string():
    req = FakeRequest()
    with pytest.raises(ValueError, match="not an existing file path"):
        req.Set(Files=["definitely-not-a-real-file.pdf"])
