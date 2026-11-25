"""Check place-mention boundaries when the two model outputs disagree."""
import unittest

from eis1600.nlp.utils import merge_ner_with_toponym_classes


class TestLocationMerge(unittest.TestCase):
    def test_merge_preserves_all_entity_boundaries(self):
        entities = ["ÜT2", "ÜT1", "ÜT3", "ÜP2S", None]
        roles = [float("nan"), "ÜT2R", "ÜT3D", "ÜT1V", "ÜT1K"]
        self.assertEqual(merge_ner_with_toponym_classes(entities, roles),
                         ["ÜT2X", "ÜT1R", "ÜT3D", "ÜP2S", None])

    def test_misaligned_tokens_fail(self):
        with self.assertRaises(ValueError):
            merge_ner_with_toponym_classes(["ÜT1"], [])
