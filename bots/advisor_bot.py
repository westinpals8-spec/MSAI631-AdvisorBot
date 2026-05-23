# Copyright (c) Westin Pals. Course: MSAI631, University of the Cumberlands.
# Licensed under the MIT License.
#
# AdvisorBot - a traditional (non-LLM) chatbot built on Microsoft Bot
# Framework. Extends the EchoBot sample into an academic advisor for
# the MS in Artificial Intelligence program at the University of the
# Cumberlands. Intent matching uses keyword scoring with difflib fuzzy
# matching plus a course-code regex shortcut.

from __future__ import annotations

import re
import string
from difflib import SequenceMatcher

from botbuilder.core import ActivityHandler, TurnContext


INTENTS = {
    "greeting": {
        "keywords": ["hi", "hello", "hey", "greetings", "howdy"],
        "response": (
            "Hi! I am the MSAI Advisor Bot. I can answer questions about "
            "the MS in Artificial Intelligence program at the University "
            "of the Cumberlands. Type \'help\' to see what I can do."
        ),
    },
    "capabilities": {
        "keywords": [
            "help", "capabilities", "menu", "commands", "options", "abilities",
        ],
        "response": (
            "Here is what I can help with:\n"
            "  1. Program overview      -> ask: tell me about the MSAI program\n"
            "  2. Course list           -> ask: what courses are required\n"
            "  3. Specific course info  -> ask: what is MSAI631\n"
            "  4. Credit hours          -> ask: how many credit hours\n"
            "  5. Time to complete      -> ask: how long does the degree take\n"
            "  6. Capstone              -> ask: tell me about the capstone\n"
            "  7. Career outcomes       -> ask: what jobs can I get\n"
            "  8. Goodbye               -> say bye to end the chat"
        ),
    },
    "program_overview": {
        "keywords": ["program", "msai", "degree", "masters", "overview"],
        "response": (
            "The MS in Artificial Intelligence at the University of the "
            "Cumberlands is a 31 credit hour graduate program designed for "
            "working professionals. Coursework spans machine learning, "
            "natural language processing, computer vision, and AI ethics, "
            "and culminates in a capstone project."
        ),
    },
    "courses": {
        "keywords": ["courses", "classes", "curriculum", "subjects", "required"],
        "response": (
            "Required courses typically include:\n"
            "  - MSAI500  Foundations of AI\n"
            "  - MSAI531  Machine Learning\n"
            "  - MSAI605  Reinforcement Learning\n"
            "  - MSAI631  Natural Language Processing (this course)\n"
            "  - MSAI632  Deep Learning\n"
            "  - MSAI670  AI Ethics and Society\n"
            "  - MSAI690  Capstone\n"
            "Ask: what is MSAI631 to drill into any course."
        ),
    },
    "credits": {
        "keywords": ["credits", "credit"],
        "response": (
            "The MSAI is a 31 credit hour degree: roughly 10 graduate "
            "courses at 3 credits each, plus a capstone."
        ),
    },
    "duration": {
        "keywords": ["long", "duration", "finish", "complete", "years", "months"],
        "response": (
            "Most students finish in 18 to 24 months by taking two courses "
            "per 8 week bi-term. Full time accelerated students can finish "
            "in about a year; working professionals often take longer."
        ),
    },
    "capstone": {
        "keywords": ["capstone", "thesis"],
        "response": (
            "The capstone is a semester long applied AI project. Students "
            "scope a real problem, build a working prototype, and present "
            "results in a written report and a recorded defense."
        ),
    },
    "careers": {
        "keywords": ["jobs", "career", "careers", "salary", "roles"],
        "response": (
            "Common roles for MSAI graduates include Machine Learning "
            "Engineer, Data Scientist, AI Product Manager, NLP Engineer, "
            "and Applied Research Scientist."
        ),
    },
    "thanks": {
        "keywords": ["thanks", "thank", "appreciate"],
        "response": "You are welcome. Anything else I can help with?",
    },
    "goodbye": {
        "keywords": ["bye", "goodbye", "exit", "quit"],
        "response": "Goodbye. Best of luck with your MSAI coursework.",
    },
}

COURSE_CATALOG = {
    "msai500": "MSAI500 Foundations of AI covers search, knowledge representation, logic, and intro ML.",
    "msai531": "MSAI531 Machine Learning covers supervised, unsupervised, and ensemble methods.",
    "msai605": "MSAI605 Reinforcement Learning covers MDPs, Q-learning, and policy gradients.",
    "msai631": "MSAI631 Natural Language Processing covers tokenization, embeddings, transformers, and a chatbot project.",
    "msai632": "MSAI632 Deep Learning covers feed forward, convolutional, and recurrent networks.",
    "msai670": "MSAI670 AI Ethics and Society covers fairness, accountability, and societal impact.",
    "msai690": "MSAI690 Capstone is a semester long applied AI project ending in a defense.",
}

INTENT_THRESHOLD = 0.85
FUZZY_FLOOR = 0.80
COURSE_CODE_RE = re.compile(r"\bmsai\s*0*(\d{3})\b", re.IGNORECASE)


def _normalize(text):
    if not text:
        return []
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return [t for t in text.split() if t]


def _fuzzy_token_match(token, keyword):
    if token == keyword:
        return 1.0
    if len(token) >= 4 and len(keyword) >= 4 and (token in keyword or keyword in token):
        return 0.9
    ratio = SequenceMatcher(None, token, keyword).ratio()
    return ratio if ratio >= FUZZY_FLOOR else 0.0


def score_intents(text):
    tokens = _normalize(text)
    if not tokens:
        return []
    scores = {}
    for intent_name, payload in INTENTS.items():
        keywords = payload["keywords"]
        best = 0.0
        for kw in keywords:
            kw_tokens = kw.split()
            per_kw = sum(
                max((_fuzzy_token_match(t, kt) for t in tokens), default=0.0)
                for kt in kw_tokens
            ) / max(len(kw_tokens), 1)
            if per_kw > best:
                best = per_kw
        scores[intent_name] = best
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def resolve_course_detail(text):
    m = COURSE_CODE_RE.search(text or "")
    if not m:
        return None
    code = "msai" + m.group(1)
    return COURSE_CATALOG.get(
        code,
        "I do not have a description for " + code.upper() + " on file yet, "
        "but it is likely a graduate elective.",
    )


def generate_reply(user_text):
    if not user_text or not _normalize(user_text):
        return (
            "I did not catch any words in that. Try asking something like "
            "what courses are required, or type help."
        )
    course_reply = resolve_course_detail(user_text)
    if course_reply:
        return course_reply
    ranked = score_intents(user_text)
    if not ranked:
        return "I am not sure what you meant. Type help to see what I can do."
    top_intent, top_score = ranked[0]
    if top_score < INTENT_THRESHOLD:
        return (
            "I am not sure I understood that. I can help with the MSAI "
            "program overview, courses, credits, duration, capstone, and "
            "career outcomes. Type help for the full menu."
        )
    return INTENTS[top_intent]["response"]


class AdvisorBot(ActivityHandler):
    async def on_message_activity(self, turn_context):
        user_text = (turn_context.activity.text or "").strip()
        reply = generate_reply(user_text)
        await turn_context.send_activity(reply)

    async def on_members_added_activity(self, members_added, turn_context):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    "Welcome to the MSAI Advisor Bot. Type help to get started."
                )
