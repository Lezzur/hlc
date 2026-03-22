"""
HLC Autoresearch — Config
===========================
THIS IS THE FILE THE AGENT MODIFIES.

Every tunable parameter for the HLC compression system lives here.
The agent edits this file, runs evaluate.py, checks the score,
keeps improvements, discards regressions.

DO NOT put evaluation logic here. That stays in evaluate.py (read-only).
"""

# ═══════════════════════════════════════════════════════════
# SYMBOL MAP — single-char replacements for high-frequency words
# Format: "word": "symbol"
# Rule: symbol must be 1 char. Word must be common. No collisions.
# ═══════════════════════════════════════════════════════════

SYMBOL_MAP = {
    "and": "+",
    "the": "^",
    "is": "$",
    "be": "$",
    "that": "~",
    "for": "@",
    "at": "@",
    "what": "#",
    "with": "&",
    "this": "!",
    "from": "%",
    "not": "*",
    "you": ";",
    "are": "<",
    "was": ">",
    "would": "{",
    "one": "}",
}

# ═══════════════════════════════════════════════════════════
# PHRASE CODEBOOK — multi-word phrases mapped to short codes
# Format: "phrase": "code"
# Rule: code must be shorter than phrase. Longer phrases = more savings.
# These are checked FIRST (Layer 1) — highest impact.
# Agent: ADD phrases here that appear in the test corpus.
#        Remove phrases that never hit. Keep codes short.
# ═══════════════════════════════════════════════════════════

PHRASE_CODEBOOK = {
    # Conversational
    "how are you": "α",
    "thank you": "β",
    "you're welcome": "γ",
    "nice to meet you": "δ",
    "good morning": "ε",
    "good night": "ζ",
    "i don't know": "η",
    "i don't think": "θ",
    "let me know": "ι",
    "as soon as possible": "κ",
    "by the way": "λ",
    "in my opinion": "μ",
    "to be honest": "ν",
    "on the other hand": "ξ",
    "at the same time": "ο",
    "for example": "π",
    "in order to": "ρ",
    "as well as": "σ",
    "such as": "τ",
    "due to": "υ",
    "in terms of": "φ",
    "in addition to": "χ",
    "as a result": "ψ",
    "in fact": "ω",
    "of course": "Α",
    "at least": "Β",
    "so far": "Γ",
    "right now": "Δ",
    "a lot of": "Ε",
    "kind of": "Ζ",
    "sort of": "Η",
    "more or less": "Θ",
    "up to": "Ι",
    "out of": "Κ",
    # Technical / LLM
    "it is important to note that": "Λ",
    "it should be noted that": "Μ",
    "in this case": "Ν",
    "for instance": "Ξ",
    "as mentioned above": "Ο",
    "based on": "Π",
    "in the context of": "Ρ",
    "according to": "Σ",
    "in particular": "Τ",
    "in other words": "Υ",
    "having said that": "Φ",
    "the fact that": "Χ",
    "in addition": "Ψ",
    "as well": "Ω",
    "there is": "Б",
    "there are": "В",
    "would be": "Г",
    "could be": "Д",
    "should be": "Е",
    "has been": "Ж",
    "have been": "З",
    "will be": "И",
    "going to": "Й",
    "able to": "К",
    "need to": "Л",
    "want to": "М",
    "have to": "Н",
    "used to": "О",
    "try to": "П",
    "seem to": "Р",
    # Agent / AI specific
    "context window": "С",
    "token cost": "Т",
    "language model": "У",
    "large language model": "Ф",
    "machine learning": "Х",
    "natural language": "Ц",
    # Common in professional writing
    "would like to": "Ш",
    "in order to": "Щ",
    "with respect to": "Ъ",
    "with regard to": "Ы",
    "take into account": "Ь",
    "keep in mind": "Э",
    "make sure": "Ю",
    "as a whole": "Я",
    "at this point": "Ѐ",
    "for the most part": "Ё",
    "that being said": "Ђ",
    "I would like to": "Ѓ",
    "please let me know": "Є",
    "I have reviewed": "Ѕ",
    "looking forward to": "І",
    # Phrases likely to appear in test corpus — AGENT SHOULD EXPAND THIS
    "it appears that": "Ї",
    "I would appreciate": "Ј",
    "if you could": "Љ",
    "we should also": "Њ",
    "let me look into": "Ћ",
    "don't hesitate to": "Ќ",
    "anything else": "Ў",
    "right away": "Џ",
    "on our end": "Ґ",
    "to your satisfaction": "Ғ",
    "is there anything": "Ҕ",
    "cost reduction": "Җ",
    "as well as": "Ҙ",
    "set up": "Қ",
    "make sure": "Ҝ",
    "figure out": "Ҟ",
    "talk about": "Ҡ",
    "think about": "Ң",
    "it can": "Ҥ",
    # High-frequency article phrases (exp 1)
    "and the": "Ҧ",
    "to the": "ҧ",
    "in the": "Ҩ",
    "of the": "ҩ",
    "with the": "Ҫ",
    "that the": "ҫ",
    "for the": "Ҭ",
    "on the": "ҭ",
    "through the": "Ү",
    "i wanted to": "ү",
    # More high-impact phrases (exp 2)
    "by the": "Ұ",
    "the new": "ұ",
    "from the": "Ҳ",
    "about the": "ҳ",
    "the model": "Ҵ",
    "the current": "ҵ",
    "for your": "Ҷ",
    "on your": "ҷ",
    "there are a few": "Ҹ",
    "and would like to": "ҹ",
    "by the end of": "Һ",
}

# ═══════════════════════════════════════════════════════════
# VOWEL STRIPPING PARAMETERS
# ═══════════════════════════════════════════════════════════

# Minimum word length to apply vowel stripping
MIN_VOWEL_STRIP_LENGTH = 4

# Words that should NEVER have vowels stripped (beyond the protected shorthand)
VOWEL_STRIP_EXCEPTIONS = {
    "area", "idea", "audio", "video", "radio", "ratio",
    "true", "false", "none", "null", "type", "file",
    "data", "meta", "base", "case", "code", "mode",
    "node", "note", "rule", "role", "rate", "state",
    "image", "queue", "value", "table", "quote",
}

# ═══════════════════════════════════════════════════════════
# PROTECTED SHORTHAND — NEVER reassign or modify these
# These already have established meanings in common usage
# ═══════════════════════════════════════════════════════════

PROTECTED_SHORTHAND = {
    "btw", "tldr", "rsvp", "fyi", "imo", "imho", "gtg", "brb", "afk",
    "asap", "diy", "eta", "faq", "fomo", "ftw", "gg", "idk", "irl",
    "jk", "lmk", "lol", "nvm", "omg", "omw", "rofl", "smh", "tbh",
    "tmi", "ttyl", "ty", "thx", "pls", "np", "wip", "wtf", "yolo",
    "msg", "info", "pic", "app", "dev", "doc", "docs", "admin", "auth",
    "api", "url", "html", "css", "js", "sql", "db", "ui", "ux",
}

# ═══════════════════════════════════════════════════════════
# MORPHOLOGICAL SUFFIX PATTERNS
# Format: (regex_pattern, suffix_code)
# Applied to find base word in codebook when exact match fails
# Order matters — first match wins
# ═══════════════════════════════════════════════════════════

MORPHOLOGICAL_PATTERNS = [
    (r"^(.+?)tion$", "tn"),
    (r"^(.+?)sion$", "sn"),
    (r"^(.+?)ment$", "mt"),
    (r"^(.+?)ness$", "ns"),
    (r"^(.+?)able$", "bl"),
    (r"^(.+?)ible$", "bl"),
    (r"^(.+?)ling$", "lng"),
    (r"^(.+?)ting$", "tng"),
    (r"^(.+?)ning$", "nng"),
    (r"^(.+?)ring$", "rng"),
    (r"^(.+?)sing$", "sng"),
    (r"^(.+?)ing$", "ng"),
    (r"^(.+?)ily$", "ly"),
    (r"^(.+?)ally$", "ly"),
    (r"^(.+?)ly$", "ly"),
    (r"^(.+?)ed$", "d"),
    (r"^(.+?)er$", "r"),
    (r"^(.+?)est$", "st"),
    (r"^(.+?)es$", "s"),
    (r"^(.+?)s$", "s"),
]

# Minimum base word length after suffix removal
MIN_BASE_LENGTH = 3
