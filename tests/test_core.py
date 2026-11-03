"""Fast stdlib tests (no media needed): python3 -m unittest discover tests"""
import json
import os
import tempfile
import unittest
from pathlib import Path


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["FW_PRODUCTIONS"] = self.tmp.name
        import importlib
        import framewright.util as util
        importlib.reload(util)
        import framewright.production as production
        importlib.reload(production)
        self.util, self.production = util, production

    def tearDown(self):
        self.tmp.cleanup()

    def test_srt_roundtrip_and_ass(self):
        from framewright import captions
        cues = [{"start": 0.5, "end": 2.25, "text": "Hello there, this is a fairly long caption line for testing wraps"}]
        srt = Path(self.tmp.name) / "a.srt"
        captions.write_srt(cues, srt)
        back = captions.parse_srt(srt)
        self.assertAlmostEqual(back[0]["start"], 0.5)
        self.assertEqual(back[0]["text"], cues[0]["text"])
        ass = captions.styled_ass(srt, Path(self.tmp.name) / "a.ass", 1080, 1920, "reel-center")
        text = ass.read_text()
        self.assertIn("PlayResY: 1920", text)
        self.assertIn("Dialogue: 0,0:00:00.50", text)

    def test_cue_grouping_breaks_on_sentence(self):
        from framewright.captions import _cues_from_words
        words = [{"word": w, "start": i * 0.3, "end": i * 0.3 + 0.25} for i, w in enumerate("One two. Three four.".split())]
        self.assertEqual(len(_cues_from_words(words)), 2)

    def test_claims_block_other_bots(self):
        os.environ["FW_BOT"] = "bot-a"
        prod = self.production.new("Claim test")
        self.production.claim(prod)
        os.environ["FW_BOT"] = "bot-b"
        with self.assertRaises(self.util.FwError):
            prod.check_claim()
        os.environ["FW_BOT"] = "bot-a"
        self.production.release(prod)
        os.environ["FW_BOT"] = "bot-b"
        prod.check_claim()  # free now

    def test_presets_are_consistent(self):
        delivery = self.util.preset("delivery")
        loud = self.util.preset("loudness")
        caps = self.util.preset("captions")
        for name, p in delivery.items():
            self.assertIn(p["loudness"], loud, name)
            self.assertIn(p["caption_style"], caps, name)


if __name__ == "__main__":
    unittest.main()
