from modules.plex import Plex


def test_plex_rating_key_returns_direct_id_tuples():
    plex = Plex.__new__(Plex)
    assert plex.get_rating_keys("plex_rating_key", [123, 456]) == [(123, "ratingKey"), (456, "ratingKey")]


def test_plex_id_returns_metadata_id_tuples():
    plex = Plex.__new__(Plex)
    assert plex.get_rating_keys("plex_id", ["63e3eedd166819851638a316"]) == [("63e3eedd166819851638a316", "plex")]
