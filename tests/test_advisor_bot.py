# Copyright (c) Westin Pals. Course: MSAI631, University of the Cumberlands.
# Licensed under the MIT License.
#
# Lightweight unit tests for the intent and response logic. These run
# without the Bot Framework Emulator:
#     python -m pytest -q
# or:
#     python tests/test_advisor_bot.py

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bots.advisor_bot import generate_reply, score_intents, resolve_course_detail


class GenerateReplyTests(unittest.TestCase):
    def test_greeting(self):
        reply = generate_reply("hello")
        self.assertIn("MSAI Advisor Bot", reply)

    def test_capabilities(self):
        reply = generate_reply("help")
        self.assertIn("Program overview", reply)

    def test_program_overview(self):
        reply = generate_reply("tell me about the MSAI program")
        self.assertIn("31 credit", reply)

    def test_course_detail_with_space(self):
        reply = generate_reply("what is MSAI 631?")
        self.assertIn("Natural Language Processing", reply)

    def test_course_detail_without_space(self):
        reply = generate_reply("MSAI632")
        self.assertIn("Deep Learning", reply)

    def test_typo_tolerance(self):
        # 'corses' should still hit the courses intent via fuzzy match.
        reply = generate_reply("what corses are required")
        self.assertIn("MSAI500", reply)

    def test_goodbye(self):
        reply = generate_reply("bye")
        self.assertIn("Goodbye", reply)

    def test_empty_input(self):
        reply = generate_reply("")
        self.assertIn("did not catch", reply)

    def test_punctuation_only(self):
        reply = generate_reply("???!!!")
        self.assertIn("did not catch", reply)

    def test_garbage_input_falls_back(self):
        reply = generate_reply("xqzpfll vvvbnk")
        self.assertIn("not sure", reply.lower())

    def test_capstone(self):
        reply = generate_reply("tell me about the capstone")
        self.assertIn("capstone", reply.lower())

    def test_careers(self):
        reply = generate_reply("what jobs can I get")
        self.assertIn("Machine Learning Engineer", reply)


class ScoringTests(unittest.TestCase):
    def test_scoring_returns_sorted_for_credits(self):
        ranked = score_intents("how many credit hours")
        # Top-ranked intent should be 'credits'.
        self.assertEqual(ranked[0][0], "credits")

    def test_course_code_resolution(self):
        self.assertIsNotNone(resolve_course_detail("info on msai 670"))
        self.assertIsNone(resolve_course_detail("hello there"))


if __name__ == "__main__":
    unittest.main()
