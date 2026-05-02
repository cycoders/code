from hash_identifier_cli.hashes import HASHES_BY_HEX_LEN


def test_hashes_db_structure():
    assert isinstance(HASHES_BY_HEX_LEN, dict)
    for byte_len, hashes in HASHES_BY_HEX_LEN.items():
        assert isinstance(byte_len, int)
        for h in hashes:
            assert "name" in h
            assert "priority" in h and isinstance(h["priority"], int)
            assert "samples" in h and isinstance(h["samples"], list)


def test_sample_lengths():
    for byte_len, hashes in HASHES_BY_HEX_LEN.items():
        for h in hashes:
            sample = h["samples"][0]
            assert len(sample) == byte_len * 2  # hex len