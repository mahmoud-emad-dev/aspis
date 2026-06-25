"""Tests for aspis.protect — the pure 6-way hash-based decision engine.

Covers sha256_text (BOM/CRLF normalization), sha256_bytes (raw), the full
decide() truth table and its ordering edge cases, plan_runtime fan-out, and
summary aggregation. Behaviour-only: no file I/O, no ASPIS imports beyond the
module under test.
"""

from __future__ import annotations

import hashlib

import pytest

from aspis.protect import (
    Decision,
    DecisionKind,
    decide,
    plan_runtime,
    sha256_bytes,
    sha256_text,
    summary,
)

# Well-known SHA-256 digests (independent of this module).
SHA256_EMPTY = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
SHA256_ABC = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
SHA256_HELLO_WORLD = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

H0 = "0000000000000000000000000000000000000000000000000000000000000000"
H1 = "1111111111111111111111111111111111111111111111111111111111111111"
H2 = "2222222222222222222222222222222222222222222222222222222222222222"
H3 = "3333333333333333333333333333333333333333333333333333333333333333"


# --------------------------------------------------------------------------- #
# sha256_text
# --------------------------------------------------------------------------- #


class TestSha256Text:
    def test_known_abc(self):
        assert sha256_text("abc") == SHA256_ABC

    def test_known_empty(self):
        assert sha256_text("") == SHA256_EMPTY

    def test_known_hello_world(self):
        assert sha256_text("hello world") == SHA256_HELLO_WORLD

    def test_crlf_normalized_to_lf(self):
        # "a\r\nb" and "a\nb" must produce the same hash.
        assert sha256_text("a\r\nb") == sha256_text("a\nb")

    def test_crlf_matches_explicit_lf(self):
        assert sha256_text("a\r\nb") == hashlib.sha256(b"a\nb").hexdigest()

    def test_bare_cr_not_normalized(self):
        # A lone \r (not part of \r\n) is preserved, not turned into \n.
        assert sha256_text("a\rb") != sha256_text("a\nb")
        assert sha256_text("a\rb") == hashlib.sha256(b"a\rb").hexdigest()

    def test_leading_bom_stripped(self):
        assert sha256_text("\ufeffabc") == sha256_text("abc")
        assert sha256_text("\ufeffabc") == SHA256_ABC

    def test_trailing_bom_not_stripped(self):
        # Only a *leading* BOM is stripped; a trailing BOM is content.
        assert sha256_text("abc\ufeff") != sha256_text("abc")
        assert sha256_text("abc\ufeff") == hashlib.sha256("abc\ufeff".encode("utf-8")).hexdigest()

    def test_bom_only_string_hashes_as_empty(self):
        # A string that is just the BOM normalizes to empty.
        assert sha256_text("\ufeff") == SHA256_EMPTY

    def test_crlf_only_string_normalizes_to_lf(self):
        # "\r\n" normalizes to "\n" (CRLF->LF), NOT to empty -> hash of a single LF.
        assert sha256_text("\r\n") == sha256_text("\n")

    def test_unicode_cjk_deterministic(self):
        text = "你好世界"
        assert sha256_text(text) == hashlib.sha256(text.encode("utf-8")).hexdigest()

    def test_unicode_accented_deterministic(self):
        text = "café résumé naïve"
        assert sha256_text(text) == hashlib.sha256(text.encode("utf-8")).hexdigest()

    def test_unicode_emoji_deterministic(self):
        text = "agent 🛡️ shield 🚀"
        assert sha256_text(text) == hashlib.sha256(text.encode("utf-8")).hexdigest()

    def test_multiple_crlf_all_normalized(self):
        assert sha256_text("line1\r\nline2\r\nline3") == sha256_text("line1\nline2\nline3")

    def test_bom_plus_crlf_combined(self):
        # Leading BOM stripped, CRLF normalized -> same as plain LF text.
        assert sha256_text("\ufeffa\r\nb") == sha256_text("a\nb")


# --------------------------------------------------------------------------- #
# sha256_bytes
# --------------------------------------------------------------------------- #


class TestSha256Bytes:
    def test_known_bytes_abc(self):
        assert sha256_bytes(b"abc") == SHA256_ABC

    def test_no_normalization_raw_bytes(self):
        # Bytes pass through untouched: b"a\r\nb" is NOT normalized.
        assert sha256_bytes(b"a\r\nb") == hashlib.sha256(b"a\r\nb").hexdigest()
        assert sha256_bytes(b"a\r\nb") != hashlib.sha256(b"a\nb").hexdigest()

    def test_png_header_bytes(self):
        png = b"\x89PNG\r\n\x1a\n"
        assert sha256_bytes(png) == hashlib.sha256(png).hexdigest()

    def test_empty_bytes(self):
        assert sha256_bytes(b"") == SHA256_EMPTY

    def test_text_and_bytes_agree_when_no_normalization_needed(self):
        # For content with no BOM and no CRLF, text and bytes digests match.
        assert sha256_text("abc") == sha256_bytes(b"abc")


# --------------------------------------------------------------------------- #
# decide — the 6 cases
# --------------------------------------------------------------------------- #


class TestDecideCases:
    def test_add_no_live(self):
        d = decide(None, H1, H2)
        assert d.kind is DecisionKind.ADD

    def test_unchanged_live_equals_regen(self):
        d = decide(H1, H2, H1)
        assert d.kind is DecisionKind.UNCHANGED

    def test_unknown_live_no_snapshot(self):
        # live != regen and snapshot is None.
        d = decide(H1, None, H2)
        assert d.kind is DecisionKind.UNKNOWN

    def test_update_live_equals_snapshot(self):
        # live == snapshot, live != regen.
        d = decide(H1, H1, H2)
        assert d.kind is DecisionKind.UPDATE

    def test_protect_regen_equals_snapshot(self):
        # live != snapshot, regen == snapshot.
        d = decide(H1, H2, H2)
        assert d.kind is DecisionKind.PROTECT

    def test_conflict_all_differ(self):
        d = decide(H1, H2, H3)
        assert d.kind is DecisionKind.CONFLICT


# --------------------------------------------------------------------------- #
# decide — ordering edge cases (first match wins)
# --------------------------------------------------------------------------- #


class TestDecideOrdering:
    def test_add_fires_before_unknown_when_live_none(self):
        # live is None but snapshot is set -> still ADD (case 1 before case 3).
        d = decide(None, H1, H2)
        assert d.kind is DecisionKind.ADD

    def test_unchanged_fires_before_unknown(self):
        # live == regen with snapshot None -> UNCHANGED (case 2 before case 3).
        d = decide(H1, None, H1)
        assert d.kind is DecisionKind.UNCHANGED

    def test_all_none_is_add(self):
        d = decide(None, None, None)
        assert d.kind is DecisionKind.ADD

    def test_all_same_hash_is_unchanged(self):
        d = decide(H1, H1, H1)
        assert d.kind is DecisionKind.UNCHANGED

    def test_add_with_snapshot_and_regen_none(self):
        d = decide(None, H1, None)
        assert d.kind is DecisionKind.ADD

    def test_decision_carries_all_three_hashes(self):
        d = decide(H1, H2, H3)
        assert d.live_hash == H1
        assert d.snapshot_hash == H2
        assert d.regen_hash == H3

    def test_decision_carries_none_hashes(self):
        d = decide(None, None, None)
        assert d.live_hash is None
        assert d.snapshot_hash is None
        assert d.regen_hash is None

    def test_decision_is_frozen(self):
        d = decide(H1, H2, H3)
        with pytest.raises(Exception):
            d.live_hash = H2  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# plan_runtime
# --------------------------------------------------------------------------- #


class TestPlanRuntime:
    def test_empty_dicts(self):
        assert plan_runtime({}, {}, {}) == {}

    def test_union_of_keys(self):
        snapshot = {"a": H1}
        live = {"b": H2}
        regen = {"c": H3}
        result = plan_runtime(snapshot, live, regen)
        assert set(result) == {"a", "b", "c"}

    def test_correct_decision_per_path(self):
        snapshot = {"keep": H1, "edit": H1, "new": H1}
        live = {"keep": H1, "edit": H2, "new": H1}
        regen = {"keep": H1, "edit": H1, "new": H1}
        result = plan_runtime(snapshot, live, regen)
        assert result["keep"].kind is DecisionKind.UNCHANGED
        assert result["edit"].kind is DecisionKind.PROTECT
        # "new": live == regen == snapshot -> UNCHANGED
        assert result["new"].kind is DecisionKind.UNCHANGED

    def test_path_only_in_snapshot_is_add(self):
        # Path in snapshot but not in live or regen -> live_hash None -> ADD.
        result = plan_runtime({"orphan": H1}, {}, {})
        assert result["orphan"].kind is DecisionKind.ADD

    def test_path_only_in_regen_is_add(self):
        result = plan_runtime({}, {}, {"fresh": H1})
        assert result["fresh"].kind is DecisionKind.ADD

    def test_path_only_in_live_is_unknown(self):
        # live present, no snapshot, no regen -> live != regen(None) -> UNKNOWN.
        result = plan_runtime({}, {"stray": H1}, {})
        assert result["stray"].kind is DecisionKind.UNKNOWN

    def test_full_six_way_mixture(self):
        # Each path is set up so exactly one decide() case fires.
        snapshot = {
            "unch": H2,       # live==regen -> UNCHANGED (snapshot irrelevant)
            "upd": H1,        # live==snapshot, regen differs -> UPDATE
            "prot": H1,       # live!=snapshot, regen==snapshot -> PROTECT
            "conf": H2,       # all differ -> CONFLICT
        }  # "add" and "unk" deliberately absent -> snapshot_hash None
        live = {
            "unch": H1,
            "unk": H1,        # live present, no snapshot, live != regen -> UNKNOWN
            "upd": H1,
            "prot": H2,
            "conf": H1,
        }  # "add" deliberately absent -> live_hash None
        regen = {
            "unch": H1,
            "unk": H2,
            "upd": H2,
            "prot": H1,
            "conf": H3,
            "add": H0,        # present in regen so "add" is in the union; live absent -> ADD
        }
        result = plan_runtime(snapshot, live, regen)
        assert result["add"].kind is DecisionKind.ADD
        assert result["unch"].kind is DecisionKind.UNCHANGED
        assert result["unk"].kind is DecisionKind.UNKNOWN
        assert result["upd"].kind is DecisionKind.UPDATE
        assert result["prot"].kind is DecisionKind.PROTECT
        assert result["conf"].kind is DecisionKind.CONFLICT


# --------------------------------------------------------------------------- #
# summary
# --------------------------------------------------------------------------- #


class TestSummary:
    def test_all_six_keys_present(self):
        counts = summary({})
        assert set(counts) == set(DecisionKind)

    def test_empty_decisions_all_zero(self):
        counts = summary({})
        assert all(v == 0 for v in counts.values())

    def test_correct_counts_mixed(self):
        decisions = {
            "a": decide(None, None, None),            # ADD
            "b": decide(H1, None, H1),                # UNCHANGED
            "c": decide(H1, None, H2),                # UNKNOWN
            "d": decide(H1, H1, H2),                  # UPDATE
            "e": decide(H1, H2, H2),                  # PROTECT
            "f": decide(H1, H2, H3),                  # CONFLICT
            "g": decide(None, H1, H2),                 # ADD
        }
        counts = summary(decisions)
        assert counts[DecisionKind.ADD] == 2
        assert counts[DecisionKind.UNCHANGED] == 1
        assert counts[DecisionKind.UNKNOWN] == 1
        assert counts[DecisionKind.UPDATE] == 1
        assert counts[DecisionKind.PROTECT] == 1
        assert counts[DecisionKind.CONFLICT] == 1

    def test_total_equals_number_of_decisions(self):
        decisions = {
            "a": decide(None, None, None),
            "b": decide(H1, H1, H1),
            "c": decide(H1, H2, H3),
        }
        counts = summary(decisions)
        assert sum(counts.values()) == len(decisions)