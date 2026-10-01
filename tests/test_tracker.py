from modules import tracker
from tests.tracker_fakes import FakeConvert, FakeRequests, FakeResponse

# --- parse_ids: same output tuples regardless of which provider's shape feeds it -----------------


def _flicklist_shaped(tmdb=None, tvdb=None, imdb=None, fldb=None, media_type="movie", title="Movie"):
    ids = {}
    if tmdb is not None:
        ids["tmdb"] = tmdb
    if tvdb is not None:
        ids["tvdb"] = tvdb
    if imdb is not None:
        ids["imdb"] = imdb
    if fldb is not None:
        ids["fldb"] = fldb
    return {"ids": ids, "media_type": media_type, "title": title}


def _flicklist_type_of(item):
    raw = str(item.get("media_type") or "").lower()
    if raw == "movie":
        return "movie"
    if raw in ("tv", "show"):
        return "show"
    return None


def _flicklist_native_id_of(item):
    return (item.get("ids") or {}).get("fldb")


def _wetrakr_shaped(id_=None, tmdb=None, tvdb=None, imdb=None, type_="movie", title="Movie"):
    ids = {}
    if tmdb is not None:
        ids["tmdb"] = tmdb
    if tvdb is not None:
        ids["tvdb"] = tvdb
    if imdb is not None:
        ids["imdb"] = imdb
    return {"id": id_, "ids": ids, "type": type_, "title": title}


def _wetrakr_type_of(item):
    return item.get("type")


def _wetrakr_native_id_of(item):
    return item.get("id")


def test_parse_ids_flicklist_shaped_and_wetrakr_shaped_produce_the_same_tuples():
    flicklist_item = _flicklist_shaped(tmdb=550, media_type="movie")
    wetrakr_item = _wetrakr_shaped(id_=99, tmdb=550, type_="movie")
    flicklist_result = tracker.parse_ids([flicklist_item], None, service="FlickList", type_of=_flicklist_type_of, native_id_of=_flicklist_native_id_of)
    wetrakr_result = tracker.parse_ids([wetrakr_item], None, service="WeTrakr", type_of=_wetrakr_type_of, native_id_of=_wetrakr_native_id_of)
    assert flicklist_result == wetrakr_result == [(550, "tmdb")]


def test_parse_ids_show_with_tvdb_only_matches_across_shapes():
    flicklist_item = _flicklist_shaped(tvdb=81189, media_type="show")
    wetrakr_item = _wetrakr_shaped(id_=5, tvdb=81189, type_="show")
    flicklist_result = tracker.parse_ids([flicklist_item], None, service="FlickList", type_of=_flicklist_type_of, native_id_of=_flicklist_native_id_of)
    wetrakr_result = tracker.parse_ids([wetrakr_item], None, service="WeTrakr", type_of=_wetrakr_type_of, native_id_of=_wetrakr_native_id_of)
    assert flicklist_result == wetrakr_result == [(81189, "tvdb")]


def test_parse_ids_dedupes_on_native_id_for_either_shape():
    items = [_wetrakr_shaped(id_=7, tmdb=550, type_="movie"), _wetrakr_shaped(id_=7, tmdb=550, type_="movie")]
    result = tracker.parse_ids(items, None, service="WeTrakr", type_of=_wetrakr_type_of, native_id_of=_wetrakr_native_id_of)
    assert result == [(550, "tmdb")]


# --- candidate_keys: native=None vs a native pair -------------------------------------------------


def test_candidate_keys_native_none_adds_no_extra_key():
    keys = tracker.candidate_keys({"tmdb": 550}, "movie", FakeConvert(), native=None)
    assert keys == {("movie", "tmdb", 550)}


def test_candidate_keys_native_pair_with_value_is_added():
    keys = tracker.candidate_keys({"tmdb": 550}, "movie", FakeConvert(), native=("wetrakr_id", 42))
    assert keys == {("movie", "tmdb", 550), ("movie", "wetrakr_id", 42)}


def test_candidate_keys_native_pair_with_none_value_is_skipped():
    keys = tracker.candidate_keys({"tmdb": 550}, "movie", FakeConvert(), native=("fldb", None))
    assert keys == {("movie", "tmdb", 550)}


# --- plan_list_sync: the four FlickList sync scenarios, re-expressed against the pure function ---


def _flicklist_ids_of(item):
    return item.get("ids") or {}


def _flicklist_native_id_of_ids_block(ids_block):
    return ("fldb", ids_block.get("fldb"))


def test_plan_list_sync_adds_new_and_removes_stale():
    desired = [({"tmdb": 550}, "movie")]
    current = [{"ids": {"tmdb": 999}, "media_type": "movie"}]
    add, remove, unmatched = tracker.plan_list_sync(desired, current, FakeConvert(), ids_of=_flicklist_ids_of, type_of=_flicklist_type_of_media, native_id_of=_flicklist_native_id_of_ids_block)
    assert add == [({"tmdb": 550}, "movie")]
    assert remove == [({"tmdb": 999}, "movie")]
    assert unmatched == 0


def _flicklist_type_of_media(item):
    # _media_type_of on FlickList: unrecognised falls back to "movie", not None.
    raw = str(item.get("media_type") or "").lower()
    return "show" if raw in ("tv", "show") else "movie"


def test_plan_list_sync_leaves_unmatched_current_items_in_place():
    desired = [({"tmdb": 550}, "movie")]
    current = [{"ids": {}, "media_type": "movie"}]
    add, remove, unmatched = tracker.plan_list_sync(desired, current, FakeConvert(), ids_of=_flicklist_ids_of, type_of=_flicklist_type_of_media, native_id_of=_flicklist_native_id_of_ids_block)
    assert add == [({"tmdb": 550}, "movie")]
    assert remove == []
    assert unmatched == 1


def test_plan_list_sync_unresolved_tvdb_conversion_does_not_delete_the_matching_tmdb_item():
    desired = [({"tvdb": 81189}, "show")]
    current = [{"ids": {"tmdb": 1396, "tvdb": 81189}, "media_type": "show"}]
    add, remove, unmatched = tracker.plan_list_sync(desired, current, FakeConvert(), ids_of=_flicklist_ids_of, type_of=_flicklist_type_of_media, native_id_of=_flicklist_native_id_of_ids_block)
    assert add == []
    assert remove == []
    assert unmatched == 0


def test_plan_list_sync_current_item_with_only_native_and_imdb_matches_desired_tmdb_via_convert():
    desired = [({"tmdb": 550}, "movie")]
    current = [{"ids": {"fldb": "flt_abc", "imdb": "tt0903747"}, "media_type": "movie"}]
    convert = FakeConvert(imdb_to_tmdb_map={"tt0903747": (550, "movie")})
    add, remove, unmatched = tracker.plan_list_sync(desired, current, convert, ids_of=_flicklist_ids_of, type_of=_flicklist_type_of_media, native_id_of=_flicklist_native_id_of_ids_block)
    assert add == []
    assert remove == []
    assert unmatched == 0


def test_plan_list_sync_with_wetrakr_style_native_id_of():
    # native_id_of returning WeTrakr's own numeric id instead of FlickList's fldb - same shape, different label/value source.
    def wetrakr_native_id_of(ids_block):
        return ("wetrakr_id", ids_block.get("wetrakr_id"))

    desired = [({"tmdb": 550}, "movie")]
    current = [{"ids": {"wetrakr_id": 42}, "media_type": "movie"}]
    add, remove, unmatched = tracker.plan_list_sync(desired, current, FakeConvert(), ids_of=_flicklist_ids_of, type_of=_flicklist_type_of_media, native_id_of=wetrakr_native_id_of)
    # No shared id between {"tmdb": 550} and {"wetrakr_id": 42} - both sides are genuinely unrelated, so both get treated independently.
    assert add == [({"tmdb": 550}, "movie")]
    assert remove == [({"wetrakr_id": 42}, "movie")]
    assert unmatched == 0


# --- _parse_error_body: the WeTrakr shapes plus Cloudflare HTML ----------------------------------


def test_parse_error_body_shape1_plain_message():
    response = FakeResponse(json_data={"message": "Too many requests. Please slow down."})
    assert tracker.TrackerAPI._parse_error_body(response) == "Too many requests. Please slow down."


def test_parse_error_body_shape2_error_code_plus_message():
    response = FakeResponse(json_data={"error": "PLAN_LIMIT_REACHED", "message": "List item limit reached"})
    assert tracker.TrackerAPI._parse_error_body(response) == "List item limit reached"


def test_parse_error_body_shape3_success_false_nested_error_object():
    response = FakeResponse(json_data={"success": False, "error": {"code": "INVALID_CURSOR", "message": "Cursor is invalid"}})
    assert tracker.TrackerAPI._parse_error_body(response) == "Cursor is invalid"


def test_parse_error_body_shape3_nested_error_object_falls_back_to_code_without_message():
    response = FakeResponse(json_data={"success": False, "error": {"code": "INVALID_CURSOR"}})
    assert tracker.TrackerAPI._parse_error_body(response) == "INVALID_CURSOR"


def test_parse_error_body_cloudflare_html_falls_back_to_raw_text():
    response = FakeResponse(content=b"<html>error 1010</html>", text="<html>error 1010</html>", raise_on_json=True, reason="Forbidden")
    assert tracker.TrackerAPI._parse_error_body(response) == "<html>error 1010</html>"


def test_parse_error_body_flicklist_detail_still_wins_when_both_detail_and_error_present():
    # FlickList's own shape (detail first) must still win under the widened shared priority order - no behaviour change for the acceptance test.
    response = FakeResponse(json_data={"detail": "invalid_scope", "error": "forbidden"})
    assert tracker.TrackerAPI._parse_error_body(response) == "invalid_scope"


# --- _request_paginated: page_params only on page 1, configurable page-count header -------------


class _FakeTracker(tracker.TrackerAPI):
    service = "Fake"
    base_url = "https://fake.example"
    page_count_header = "X-Fake-Page-Count"
    page_params = {"limit": 100}

    def _headers(self, anonymous=False):
        return {"User-Agent": "Fake/1.0"}


def make_fake_tracker(responses):
    t = _FakeTracker(FakeRequests(responses), read_only=False)
    return t


def test_request_paginated_sends_page_params_on_page_one_only():
    t = make_fake_tracker(
        [
            FakeResponse(json_data=[{"id": 1}], headers={"X-Fake-Page-Count": "2"}),
            FakeResponse(json_data=[{"id": 2}], headers={}),
        ]
    )
    results = t._request_paginated("/items")
    assert results == [{"id": 1}, {"id": 2}]
    page1_params = t.requests.gets[0][2]
    page2_params = t.requests.gets[1][2]
    assert page1_params == {"limit": 100}
    assert page2_params == {"page": 2}


def test_request_paginated_follows_configurable_page_count_header():
    t = make_fake_tracker([FakeResponse(json_data=[{"id": 1}], headers={"X-Fake-Page-Count": "1"})])
    results = t._request_paginated("/items")
    assert results == [{"id": 1}]
    assert len(t.requests.gets) == 1
