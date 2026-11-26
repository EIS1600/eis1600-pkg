"""Temporal migration regression tests for provenance, token alignment and replay."""

import copy
import unittest
import ujson

from eis1600.dates.temporal import apply_temporal, recognise_segment


class TemporalTest(unittest.TestCase):
    def test_retag_and_replay(self):
        tokens = ["تُوفِّي", "في", "رمضان", "سنة", "أربعين"]
        df = {
            "TOKENS": dict(enumerate(tokens)),
            "SECTIONS": dict.fromkeys(range(5)),
            "TAGS_LISTS": dict(
                enumerate(
                    [["P1B"], None, ["ÜL1X09L"], ["Y2D0040Y0640", "ÜY2X0010Y"], None]
                )
            ),
            "NER_LABELS": dict.fromkeys(range(5), "O"),
        }
        yml = {
            "UID": "u",
            "dates": [{"date": 10}],
            "min_date": 5,
            "max_date": 10,
            "headings": {"h1": "سنة سبعمائة", "page_tag": "PageV01P700"},
        }
        row = apply_temporal({"yml": yml, "df": ujson.dumps(df)})
        self.assertEqual(yml["dates_headings"], [700])
        self.assertEqual(
            yml["dates"], [{"entity": "سنة أربعين", "date": 640, "cat": "D"}]
        )
        self.assertEqual((yml["min_date"], yml["max_date"]), (570, 640))
        manual = yml["temporal_entities"][0]
        self.assertEqual(
            (manual["source"], manual["year_hijri"], manual["month"]), ("manual", 40, 9)
        )
        merged = ujson.loads(row["df"])["TAGS_LISTS"]
        self.assertEqual(merged["3"], ["Y2D0040Y0640"])
        self.assertEqual(merged["0"], ["P1B"])
        self.assertEqual(apply_temporal(copy.deepcopy(row)), row)

    def test_normalization_keeps_source_indices(self):
        tokens = ["توفي", "سنة", "أربع", "[", "عشرة", "]", "وثلاثمائة"]
        (item,) = recognise_segment(tokens, [None] * len(tokens), "body", 8)
        self.assertEqual(
            (item["year_hijri"], item["start_token"], item["end_token"], item["tag"]),
            (314, 9, 15, "ÜY6D0314Y"),
        )

    def test_other_kinds(self):
        for words, kind in [
            ("توفي يوم الجمعة", "weekday"),
            ("توفي في القرن الثامن", "century"),
            ("قدم في رمضان", "month"),
        ]:
            t = words.split()
            entities = recognise_segment(t, [None] * len(t), "body")
            self.assertEqual([e["entity_type"] for e in entities], [kind])
