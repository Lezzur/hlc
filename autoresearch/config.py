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
    # ASCII symbols (high-frequency words)
    "and": "+",
    "the": "^",
    "is": "$",
    "be": "ㅟ",    # fixed: was colliding with "is" on "$"
    "that": "~",
    "for": "@",
    "at": "ㄬ",    # fixed: was colliding with "for" on "@"
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
    "our": "\\",
    "can": "|",
    "have": "[",
    "been": "]",
    "has": "_",
    "more": "`",
    "all": "1",
    "new": "2",
    "time": "3",
    "like": "4",
    "any": "5",
    "into": "6",
    "down": "7",
    "about": "8",
    "but": "9",
    "out": "0",
    "first": "A",
    "next": "B",
    "your": "C",
    "their": "D",
    "there": "E",
    "data": "F",
    "which": "G",
    "other": "H",
    "them": "K",
    "well": "L",
    "work": "M",
    "make": "N",
    "know": "O",
    "see": "P",
    "good": "Q",
    "way": "R",
    "just": "S",
    "want": "T",
    "year": "U",
    "use": "V",
    "life": "W",
    "part": "X",
    "need": "Y",
    "feel": "Z",
    # Hangul Jamo — group 1 (unique, collision-free)
    "give": "ㄱ",
    "tell": "ㄴ",
    "come": "ㄷ",
    "call": "ㄹ",
    "ask": "ㄸ",
    "try": "ㅁ",
    "back": "ㅂ",
    "hand": "ㅄ",
    "mind": "ㅅ",
    "place": "ㅆ",
    "seem": "ㅇ",
    "mean": "ㅈ",
    "open": "ㅉ",
    "end": "ㅊ",
    "form": "ㅋ",
    "look": "ㅌ",
    "system": "ㅍ",
    "model": "ㅎ",
    # Hangul Jamo — group 2
    "day": "ㅏ",
    "right": "ㅑ",
    "high": "ㅒ",
    "case": "ㅓ",
    "point": "ㅔ",
    "group": "ㅕ",
    "number": "ㅖ",
    "person": "ㅗ",
    "thing": "ㅘ",
    "month": "ㅙ",
    "week": "ㅚ",
    "thought": "ㅝ",
    "find": "ㅞ",
    "talk": "ㅢ",
    "hold": "ㅣ",
    "move": "ㅤ",
    "sound": "ㅥ",
    "send": "ㅦ",
    "show": "ㅧ",
    "wait": "ㅨ",
    "follow": "ㅩ",
    "keep": "ㅪ",
    "start": "ㅫ",
    "turn": "ㅬ",
    "step": "ㅭ",
    "reach": "ㅮ",
    "build": "ㅯ",
    "change": "ㅰ",
    "happen": "ㅱ",
    "create": "ㅲ",
    "remove": "ㅳ",
    "apply": "ㅴ",
    "define": "ㅵ",
    "expand": "ㅶ",
    "reduce": "ㅷ",
    "enhance": "ㅸ",
    "display": "ㅹ",
    "require": "ㅺ",
    "provide": "ㅻ",
    "perform": "ㅼ",
    "support": "ㅽ",
    "handle": "ㅾ",
    "manage": "ㅿ",
    # Hangul Jamo — group 3
    "monitor": "㄀",
    "control": "㄁",
    "benefit": "㄂",
    "improve": "㄃",
    "increase": "㄄",
    "achieve": "ㄅ",
    "process": "ㄆ",
    "service": "ㄇ",
    "company": "ㄈ",
    "project": "ㄉ",
    "involve": "ㄊ",
    "generate": "ㄋ",
    "position": "ㄌ",
    "purpose": "ㄍ",
    "conduct": "ㄎ",
    "relate": "ㄏ",
    "depend": "ㄐ",
    "concern": "ㄑ",
    "develop": "ㄒ",
    "maintain": "ㄓ",
    "impact": "ㄔ",    # fixed: freed from achieve-dedup
    "deliver": "ㄕ",
    "response": "ㄖ",
    "feature": "ㄗ",
    "access": "ㄘ",
    "content": "ㄙ",
    "details": "ㄚ",
    "updates": "ㄛ",
    "issue": "ㄜ",
    "account": "ㄝ",
    "network": "ㄞ",
    "request": "ㄟ",
    "stream": "ㄠ",    # fixed: freed from service-dedup
    "option": "ㄡ",
    "status": "ㄢ",
    "result": "ㄣ",
    "method": "ㄤ",
    "period": "ㄥ",
    "reason": "ㄦ",
    "notice": "ㄧ",
    "review": "ㄨ",
    "health": "ㄩ",
    "safety": "ㄪ",
    "policy": "ㄫ",
    "center": "ㄭ",    # fixed: freed from control-dedup
    "effort": "ㄮ",
    "energy": "ㄯ",
    "action": "㄰",
    "growth": "ㄲ",
    "vision": "ㄳ",
    "member": "ㄵ",    # fixed: freed from effort-dedup
    "learn": "ㄶ",    # fixed: freed from result-dedup
    "record": "ㄺ",
    "break": "ㄻ",
    "force": "ㄼ",
    "cause": "ㄽ",
    "share": "ㄾ",
    "order": "ㄿ",    # fixed: freed from reach-dedup
    "trade": "ㅀ",
    "bring": "ㅃ",
    # Katakana — for remaining collision words (new unique symbols)
    "color": "ア",
    "cover": "イ",
    "close": "ウ",
    "level": "エ",
    "stage": "オ",
    "total": "カ",
    # Katakana — high-frequency words missing from map (exp 3)
    "will": "ソ",
    "before": "テ",
    "through": "タ",
    "they": "チ",
    "because": "ツ",
    "were": "ト",
    # Katakana — more high-frequency words (exp 4)
    "attention": "ナ",
    "different": "ニ",
    "something": "ヌ",
    "approach": "ネ",
    "should": "ノ",
    "please": "ハ",
    "team": "ヒ",
    "three": "フ",
    # Katakana — exp 5 batch
    "rate": "ヘ",
    "current": "ホ",
    "already": "マ",
    "while": "ミ",
    "think": "ム",
    "still": "メ",
    "once": "モ",
    "file": "ヤ",
    # Katakana — exp 6: long high-value words
    "significant": "ユ",
    "performance": "ヨ",
    "information": "ラ",
    "authentication": "リ",
    "minutes": "ル",
    "between": "レ",
    "include": "ロ",
    "without": "ワ",
    # Hiragana — exp 7: more long high-value words
    "configuration": "あ",
    "completely": "い",
    "appreciate": "う",
    "architecture": "え",
    "specific": "お",
    "analysis": "か",
    "available": "き",
    "improvement": "く",
    # Hiragana — exp 8: more high-value words
    "environment": "け",
    "implementation": "こ",
    "meeting": "さ",
    "techniques": "し",
    "processing": "す",
    "experience": "せ",
    "deployment": "そ",
    "additional": "た",
    # Hiragana — exp 9: more high-value words
    "provides": "ち",
    "historical": "つ",
    "relationships": "て",
    "computational": "と",
    "during": "な",
    "training": "に",
    "settings": "ぬ",
    "pipeline": "ね",
    # Hiragana — exp 10
    "requirements": "の",
    "augmentation": "は",
    "mechanism": "ひ",
    "important": "ふ",
    "framework": "へ",
    "dashboard": "ほ",
    "correctly": "ま",
    "problem": "み",
    # Hiragana — exp 11
    "credentials": "む",
    "constraints": "め",
    "application": "も",
    "thinking": "や",
    "strategy": "ゆ",
    "research": "よ",
    "patterns": "ら",
    "learning": "り",
    # Hiragana — exp 12
    "every": "る",
    "results": "れ",
    "message": "ろ",
    "changes": "わ",
    "using": "を",
    "schedule": "ん",
    "customer": "ヴ",
    "continue": "ヵ",
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
    # More unused high-value phrases (exp 5)
    "would like to": "ҽ",
    "the next": "Ҿ",
    "has been": "ҿ",
    "thank you for": "Ā",    # fixed: was colliding with "at this point" on Ѐ
    "there are": "ѐ",
    "the first": "Ă",        # fixed: was colliding with "I would like to" on Ѓ
    "need to": "ѓ",
    "wanted to": "Ą",        # fixed: was colliding with "I have reviewed" on Ѕ
    "you for your": "ѕ",
    "let me": "Ć",            # fixed: was colliding with "it appears that" on Ї
    # Long phrases (exp 7)
    "by the end of this": "ї",
    "within the next two weeks": "Ĉ",  # fixed: was colliding with "I would appreciate" on Ј
    # More unused phrases (exp 21)
    "at the": "ј",
    "like to": "Ċ",        # fixed: was colliding with "if you could" on Љ
    "with a": "љ",
    "all the": "Č",        # fixed: was colliding with "we should also" on Њ
    "going to": "њ",
    "the system": "Ď",    # fixed: was colliding with "let me look into" on Ћ
    "me know": "ћ",
    "we need": "Đ",        # fixed: was colliding with "don't hesitate to" on Ќ
    "lot of": "ќ",
    # Additional 3-word phrases (exp 28)
    "of the input": "Ē",  # fixed: was colliding with "anything else" on Ў
    "you through the": "ў",
    "want to make": "Ĕ",  # fixed: was colliding with "right away" on Џ
    "schedule a call": "џ",
    # More phrases (exp 36)
    "to our team": "Ė",    # fixed: was colliding with "on our end" on Ґ
    "about the project": "ґ",
    "help you with": "Ę",  # fixed: was colliding with "to your satisfaction" on Ғ
    "in the next": "ғ",
    # Corpus-derived phrases (exp 2) — Katakana codes (collision-free)
    "thank you for your": "キ",
    "i appreciate you": "ク",
    "within the next": "ケ",
    "the end of this": "コ",
    "and would like": "サ",
    "to discuss the": "シ",
    "to inform you that": "ス",
    "by the end of this week": "セ",
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
    (r"^(.+?)ity$", "ty"),
    (r"^(.+?)ous$", "us"),
    (r"^(.+?)ful$", "fl"),
    (r"^(.+?)less$", "ls"),
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
