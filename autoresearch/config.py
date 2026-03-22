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
    "be": ")",
    "that": "~",
    "for": "@",
    "at": "\"",
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
    "into": "ՠ",
    "down": "¦",
    "about": "8",
    "but": "9",
    "out": "0",
    "first": "A",
    "next": "B",
    "your": "C",
    "their": "D",
    "there": "Ӄ",
    "data": "F",
    "which": "G",
    "other": "ǈ",
    "them": "Ѥ",
    "well": "ƾ",
    "work": "ǎ",
    "make": "Ч",
    "know": "ѧ",
    "see": "ì",
    "good": "Ȭ",
    "way": "ǁ",
    "just": "S",
    "want": "һ",
    "year": "ǖ",
    "use": "V",
    "life": "ʩ",
    "part": "ߜ",
    "need": "Y",
    "feel": "Ն",
    # Hangul Jamo — group 1 (unique, collision-free)
    "give": "ȍ",
    "tell": "Ȑ",
    "come": "ȓ",
    "call": "ȕ",
    "ask": "Ȕ",
    "try": "ȝ",
    "back": "Ȟ",
    "hand": "Ƞ",
    "mind": "ȡ",
    "place": "Ȣ",
    "seem": "ȣ",
    "mean": "Ȥ",
    "open": "ȥ",
    "end": "Ȧ",
    "form": "ȧ",
    "look": "Ȩ",
    "system": "ȩ",
    "model": "Ȫ",
    # Hangul Jamo — group 2
    "day": "ȫ",
    "right": "Q",
    "high": "ȭ",
    "case": "Ȯ",
    "point": "ȯ",
    "group": "Ȱ",
    "number": "ȱ",
    "person": "Ȳ",
    "thing": "ȳ",
    "month": "ȴ",
    "week": "ȵ",
    "thought": "ȶ",
    "find": "ȷ",
    "talk": "ȹ",
    "hold": "Ⱥ",
    "move": "Ȼ",
    "sound": "ȼ",
    "send": "Ƚ",
    "show": "Ⱦ",
    "wait": "ȿ",
    "follow": "ɀ",
    "keep": "Ɂ",
    "start": "ɂ",
    "turn": "Ƀ",
    "step": "Ʉ",
    "reach": "Ʌ",
    "build": "Ɇ",
    "change": "ɇ",
    "happen": "Ɉ",
    "create": "ɉ",
    "remove": "Ɋ",
    "apply": "ɋ",
    "define": "Ɍ",
    "expand": "ɍ",
    "reduce": "Ɏ",
    "enhance": "ɏ",
    "display": "ɐ",
    "require": "ɑ",
    "provide": "ɒ",
    "perform": "ɓ",
    "support": "ɔ",
    "handle": "ɕ",
    "manage": "ɖ",
    # Hangul Jamo — group 3
    "monitor": "ǜ",
    "control": "ǝ",
    "benefit": "Ǟ",
    "improve": "ǟ",
    "increase": "Ǡ",
    "achieve": "ǡ",
    "process": "Ǣ",
    "service": "ǣ",
    "company": "Ǥ",
    "project": "ǥ",
    "involve": "Ǧ",
    "generate": "ǧ",
    "position": "Ǩ",
    "purpose": "ǩ",
    "conduct": "Ǫ",
    "relate": "ǫ",
    "depend": "Ǭ",
    "concern": "ǭ",
    "develop": "Ǯ",
    "maintain": "ǯ",
    "impact": "ǰ",    # fixed: freed from achieve-dedup
    "deliver": "Ǳ",
    "response": "ǲ",
    "feature": "ǳ",
    "access": "Ǵ",
    "content": "ǵ",
    "details": "Ƕ",
    "updates": "Ƿ",
    "issue": "Ǹ",
    "account": "ǹ",
    "network": "Ǻ",
    "request": "ǻ",
    "stream": "Ǽ",    # fixed: freed from service-dedup
    "option": "ǽ",
    "status": "Ǿ",
    "result": "ǿ",
    "method": "Ȁ",
    "period": "ȁ",
    "reason": "Ȃ",
    "notice": "ȃ",
    "review": "Ȅ",
    "health": "ȅ",
    "safety": "Ȇ",
    "policy": "ȇ",
    "center": "ȉ",    # fixed: freed from control-dedup
    "effort": "Ȋ",
    "energy": "ȋ",
    "action": "Ȍ",
    "growth": "Ȏ",
    "vision": "ȏ",
    "member": "ȑ",    # fixed: freed from effort-dedup
    "learn": "Ȓ",    # fixed: freed from result-dedup
    "record": "Ȗ",
    "break": "ȗ",
    "force": "Ș",
    "cause": "ș",
    "share": "Ț",
    "order": "ț",    # fixed: freed from reach-dedup
    "trade": "Ȝ",
    "bring": "ȟ",
    # Katakana — for remaining collision words (new unique symbols)
    "color": "Ʈ",
    "cover": "Ư",
    "close": "ư",
    "level": "Ʊ",
    "stage": "Ʋ",
    "total": "Ƴ",
    # Katakana — high-frequency words missing from map (exp 3)
    "will": "\x08",
    "before": "\x10",
    "through": "\x15",
    "they": "L",
    "because": "\x13",
    "were": "R",
    # Katakana — more high-frequency words (exp 4)
    "attention": "ǂ",
    "different": "ǃ",
    "something": "Ǆ",
    "approach": "ǅ",
    "should": "\x03",
    "please": "Ǉ",
    "team": "H",
    "three": "(",
    # Katakana — exp 5 batch
    "rate": "Ǌ",
    "current": "ǋ",
    "already": "ǌ",
    "while": "Ǎ",
    "think": "M",
    "still": "Ǐ",
    "once": "ǐ",
    "file": "Ǒ",
    # Katakana — exp 6: long high-value words
    "significant": "ǒ",
    "performance": "Ǔ",
    "information": "ǔ",
    "authentication": "Ǖ",
    "minutes": "U",
    "between": "\x11",
    "include": "ǘ",
    "without": "Ǚ",
    # Hiragana — exp 7: more long high-value words
    "configuration": "ƀ",
    "completely": "Ɓ",
    "appreciate": "Ƃ",
    "architecture": "ƃ",
    "specific": "Ƅ",
    "analysis": "ƅ",
    "available": "Ɔ",
    "improvement": "Ƈ",
    # Hiragana — exp 8: more high-value words
    "environment": "ƈ",
    "implementation": "Ɖ",
    "meeting": "Ɗ",
    "techniques": "Ƌ",
    "processing": "ƌ",
    "experience": "ƍ",
    "deployment": "Ǝ",
    "additional": "Ə",
    # Hiragana — exp 9: more high-value words
    "provides": "Ɛ",
    "historical": "Ƒ",
    "relationships": "ƒ",
    "computational": "Ɠ",
    "during": "\x16",
    "training": "ƕ",
    "settings": "Ɩ",
    "pipeline": "Ɨ",
    # Hiragana — exp 10
    "requirements": "Ƙ",
    "augmentation": "ƙ",
    "mechanism": "ƚ",
    "important": "ƛ",
    "framework": "Ɯ",
    "dashboard": "Ɲ",
    "correctly": "ƞ",
    "problem": "Ɵ",
    # Hiragana — exp 11
    "credentials": "Ơ",
    "constraints": "ơ",
    "application": "Ƣ",
    "thinking": "ƣ",
    "strategy": "Ƥ",
    "research": "ƥ",
    "patterns": "Ʀ",
    "learning": "Ƨ",
    # Hiragana — exp 12
    "every": "\x06",
    "results": "Ʃ",
    "message": "ƪ",
    "changes": "ƫ",
    "using": "Ƭ",
    "schedule": "ƭ",
    "customer": "ǚ",
    "continue": "Ǜ",
    # CJK — exp 13
    "most": "ɗ",
    "each": "\x0e",
    "wanted": "ɚ",
    "across": "\x18",
    "reports": "ɞ",
    "believe": "ɩ",
    "could": "ɘ",
    "allow": "ɨ",
    # CJK — exp 14
    "services": "ɜ",
    "properly": "ɶ",
    "possible": "ѵ",
    "language": "ɷ",
    "expenses": "ə",
    "detailed": "ʉ",
    "consider": "ʑ",
    "last": "ɛ",
    # CJK — exp 15
    "thresholds": "Й",
    "sufficient": "г",
    "strategies": "ʜ",
    "production": "ɟ",
    "window": "е",
    "rather": "ъ",
    "module": "ѩ",
    "market": "ɿ",
    # CJK — exp 16
    "sure": "ʓ",
    "five": "\x12",
    "token": "Ѳ",
    "tasks": "ʊ",
    "based": "ʀ",
    "after": "ѯ",
    "updated": "ӟ",
    "present": "Ӥ",
    # CJK — exp 17
    "percent": "=",
    "metrics": "ҡ",
    "however": "҃",
    "discuss": "Ѿ",
    "scheduled": "с",
    "reduction": "м",
    "recommend": "п",
    "potential": "҂",
    # CJK — exp 18
    "gradually": "і",
    "generates": "ӽ",
    "financial": "Ӱ",
    "currently": "ӱ",
    "modifications": "Ш",
    "compatibility": "ʃ",
    "subscription": "ҁ",
    "presentation": "ɫ",
    # CJK — exp 19: contractions + high-freq words
    "it's": "T",
    "you're": "N",
    "i've": "Ӳ",
    "don't": "ɦ",
    "then": "Ӵ",
    "cost": "ӹ",
    "upcoming": "ʤ",
    "timeline": "ʬ",
    # CJK — exp 20: more high-freq words
    "when": "\x01",
    "than": "\x02",
    "over": "\x0f",
    "long": "ӑ",
    "table": "ɱ",
    "stack": "Ҋ",
    "error": "҈",
    "within": "\x17",
    # CJK — exp 21: more high-freq words
    "second": "Ԃ",
    "really": "ԃ",
    "models": "ѭ",
    "having": "ӿ",
    "engine": "Ӓ",
    "budget": "қ",
    "supports": "Ӯ",
    "resource": "ʏ",
    # CJK — exp 22: 8-letter high-value words
    "practice": "Ә",
    "password": "ф",
    "original": "ʚ",
    "indexing": "и",
    "identity": "Ӝ",
    "followed": "Ӟ",
    "feedback": "ɹ",
    "features": "ӊ",
    # CJK — exp 23: more high-value words
    "everyone": "ʖ",
    "needed": "э",
    "working": "н",
    "usually": "т",
    "systems": "ʔ",
    "suggest": "ѿ",
    "started": "Ѭ",
    "running": "Ӷ",
    # CJK — exp 24: more high-value words
    "resolve": "ӵ",
    "renewal": "ы",
    "quality": "ѫ",
    "propose": "ӳ",
    "primary": "ӷ",
    "prepare": "ю",
    "objects": "Ѩ",
    "looking": "ʗ",
    # CJK — exp 25: more high-value words
    "hundred": "\x05",
    "formats": "ѥ",
    "finally": "Ѣ",
    "expense": "ђ",
    "browser": "є",
    "address": "ё",
    "where": "K",
    "weeks": "O",
    # CJK — exp 26: contractions + very long words
    "i'm": "ӧ",
    "let": "Ҍ",
    "how": "ҋ",
    "i'd": "ҥ",
    "had": "\x7f",
    "particularly": "Ѵ",
    "implementing": "Ѫ",
    "dependencies": "з",
    # CJK — exp 27: 11-letter high-value words
    "recommended": "ӥ",
    "projections": "Ӣ",
    "predictions": "ӣ",
    "outperforms": "Ӧ",
    "observation": "Ӭ",
    "discussions": "Ӫ",
    "development": "ӫ",
    "compression": "ɬ",
    # CJK — exp 28: 10-letter high-value words
    "unexpected": "ɯ",
    "understand": "ʟ",
    "underlying": "ѻ",
    "separately": "Ѻ",
    "resolution": "у",
    "regulatory": "ѳ",
    "parameters": "ɧ",
    "onboarding": "ө",
    # CJK — exp 29: more 10-letter words
    "mechanisms": "Ѹ",
    "management": "к",
    "individual": "ѷ",
    "indicators": "ѱ",
    "increasing": "ʂ",
    "frequently": "р",
    "expiration": "Ӡ",
    "everything": "Ө",
    # CJK — exp 30: more 10+ letter words
    "diagnostic": "҇",
    "describing": "҅",
    "dependency": "ʫ",
    "components": "ɥ",
    "associated": "ӡ",
    "assessment": "҄",
    "approaches": "Ѱ",
    "comfortable": "Ԇ",
    # CJK — exp 31: 9-letter words
    "yesterday": "ӌ",
    "warehouse": "ӎ",
    "validated": "Ӑ",
    "supported": "Ӌ",
    "statement": "җ",
    "reviewing": "Ӈ",
    "resources": "ҏ",
    "reporting": "Ҁ",
    # CJK — exp 32: more 9-letter words
    "reference": "ɠ",
    "questions": "ɣ",
    "quarterly": "ʦ",
    "published": "ʌ",
    "processed": "ʞ",
    "necessary": "ʨ",
    "magnitude": "ч",
    "instances": "ѡ",
    # CJK — exp 33: more 9-letter words
    "ingestion": "ɴ",
    "indicates": "Ӊ",
    "including": "҆",
    "following": "ɤ",
    "encourage": "ѣ",
    "effective": "ӯ",
    "discussed": "Ѡ",
    "direction": "я",
    # CJK — exp 34: remaining 9-letter + 5-letter high-count words
    "configure": "В",
    "conducted": "ʎ",
    "challenge": "Ѽ",
    "carefully": "ʍ",
    "until": "Ж",
    "those": "ш",
    "thank": "ԇ",
    "items": "Ԅ",
    # CJK — exp 35: more high-value words
    "compressions": "ɢ",
    "two": "/",
    "input": "ʐ",
    "hours": "\x19",
    "green": "б",
    "going": "Ӕ",
    "cache": "ӂ",
    "being": "ӻ",
    # CJK — exp 36: short high-count + 6-letter words
    "only": "Ӽ",
    "many": "Ԁ",
    "help": "Ѷ",
    "even": "Ҽ",
    "she": "W",
    "update": "ѝ",
    "output": "ь",
    "issues": "ʈ",
    # CJK — exp 37: more 6-letter words
    "twenty": "E",
    "things": "Ӆ",
    "stores": "ӆ",
    "report": "ӄ",
    "recent": "ʋ",
    "minute": "ӈ",
    "making": "в",
    "better": "х",
    # CJK — exp 40: remaining high-value word symbols
    "behind": "Ӏ",
    "around": "й",
    "answer": "ʣ",
    "allows": "ʛ",
    "algorithm": "ӓ",
    "breathing": "ɾ",
    "security": "ӗ",
    "requests": "ӕ",
    # CJK — exp 41: 8-letter value-14 words
    "wireless": "л",
    "verified": "Ӂ",
    "tradeoff": "ɸ",
    "thousand": "\x07",
    "starting": "ɮ",
    "slightly": "ʙ",
    "shipment": "ɪ",
    "sequence": "ʅ",
    # CJK — exp 42: more 8-letter words
    "rollback": "Ӗ",
    "reviewed": "ʧ",
    "relevant": "ц",
    "received": "ɲ",
    "question": "Ӹ",
    "prepared": "ʢ",
    "positive": "ʡ",
    "navigate": "ӝ",
    # CJK — exp 43: more 8-letter words
    "multiple": "ӭ",
    "modeling": "ѽ",
    "metadata": "ʝ",
    "location": "Ѯ",
    "findings": "ԁ",
    "document": "ɡ",
    "decision": "ʆ",
    "deadline": "ʒ",
    # CJK — exp 44: more 8-letter words
    "datasets": "ɳ",
    "contains": "Ӎ",
    "consists": "ɼ",
    "coherent": "ʪ",
    "choosing": "Ҏ",
    "capacity": "Ӛ",
    "business": "ӏ",
    "behavior": "ҍ",
    # CJK — exp 45: final 8-letter + short high-count words
    "applying": "о",
    "allowing": "Ѝ",
    "adjusted": "А",
    "achieves": "ʮ",
    "accessed": "ɰ",
    "set": "ʯ",
    "oil": "ʭ",
    "now": "ʠ",
    # CJK — exp 47: 4-letter high-count words
    "used": "ң",
    "task": "щ",
    "take": "Ӿ",
    "i'll": "ә",
    "here": "ʁ",
    "four": "\x04",
    "date": "ӛ",
    "blue": "ɻ",
    # CJK — exp 48: remaining short words
    "away": "Ѧ",
    "also": "ҟ",
    # CJK — exp 50: final word batch
    "years": "\x14",
    "users": "д",
    "track": "Ю",
    "times": "а",
    "these": "ʇ",
    "check": "ɭ",
    "batch": "ж",
    "layer": "Ӻ",
    # exp 2: high-value word symbols
    "approximately": "X",
    "dollars": "¡",
    "fifteen": "¢",
    "thirty": "\x1a",
    "requires": "¤",
    "automatically": "¥",
    "against": "7",
    "actually": "§",
    "whether": "¨",
    "under": "\x1b",
    "engineering": "ª",
    "organization": "«",
    "includes": "¬",
    "twelve": "­",
    "permissions": "®",
    "morning": "¯",
    "existing": "°",
    "intellectual": "±",
    "ninety": "²",
    "forty": "³",
    "seven": "´",
    "agreement": "µ",
    "version": "¶",
    "eighteen": "·",
    "months": "¸",
    "treatment": "¹",
    "implement": "º",
    "migration": "»",
    "sixty": "¼",
    "platform": "½",
    "fourteen": "¾",
    "doesn't": "¿",
    "arbitration": "À",
    "individuals": "Á",
    "correlation": "Â",
    "quarter": "Ã",
    "international": "Ä",
    "delivery": "Å",
    "standard": "Æ",
    "requested": "Ç",
    "property": "È",
    "milligrams": "É",
    "seconds": "Ê",
    "product": "Ë",
    "days": "Ì",
    "consistent": "Í",
    "compliance": "Î",
    "jurisdiction": "Ï",
    "fifty": "Ð",
    "eight": "Ñ",
    "personal": "Ò",
    "water": "Ó",
    "trying": "Ô",
    "events": "Õ",
    "complete": "Ö",
    "obligations": "×",
    "recovery": "Ø",
    "expected": "Ù",
    "suggests": "Ú",
    "separate": "Û",
    "annual": "Ü",
    "outcomes": "Ý",
    "residential": "Þ",
    "failure": "ß",
    "revenue": "à",
    "analytics": "á",
    "produce": "â",
    "variables": "ã",
    "exceeding": "ä",
    "least": "å",
    "third": "æ",
    "conditions": "ç",
    "effect": "è",
    "department": "é",
    "facilities": "ê",
    "real": "ë",
    "same": "P",
    "people": "í",
    "higher": "î",
    "regardless": "ï",
    "compared": "ð",
    "effects": "ñ",
    "symptoms": "ò",
    "prevent": "ó",
    "reported": "ô",
    "costs": "õ",
    "contract": "ö",
    "alternatives": "÷",
    "subject": "ø",
    "needs": "ù",
    "duration": "ú",
    "compensation": "û",
    "notification": "ü",
    "limited": "ý",
    "critical": "þ",
    "consistently": "ÿ",
    "modification": "ʰ",
    "several": "ʱ",
    "milliseconds": "ʲ",
    "kitchen": "ʳ",
    "industry": "ʴ",
    "relationship": "ʵ",
    "instructions": "ʶ",
    "event": "ʷ",
    "megabytes": "ʸ",
    "single": "ʹ",
    "target": "ʺ",
    "lifestyle": "ʻ",
    "both": "ʼ",
    "typically": "ʽ",
    "season": "ʾ",
    "structure": "ʿ",
    "eighty": "ˀ",
    "below": "ˁ",
    "consecutive": "˂",
    "discrepancy": "˃",
    "preferences": "˄",
    "state": "˅",
    "isn't": "ˆ",
    "replacement": "ˇ",
    "competitive": "ˈ",
    "appropriate": "ˉ",
    "distributed": "ˊ",
    "full": "ˋ",
    "straightforward": "ˌ",
    "must": "ˍ",
    "latency": "ˎ",
    "patient": "ˏ",
    "history": "ː",
    "they're": "ˑ",
    "pricing": "˒",
    "there's": "˓",
    "completing": "˔",
    "approved": "˕",
    "elevated": "˖",
    "physical": "˗",
    "memory": "˘",
    "exceeded": "˙",
    "reaching": "˚",
    "conference": "˛",
    "reasonable": "˜",
    "previous": "˝",
    "continuous": "˞",
    "resolved": "˟",
    "server": "ˠ",
    "yourself": "ˡ",
    "identifier": "ˢ",
    "provided": "ˣ",
    "initiating": "ˤ",
    "collection": "˥",
    "attorney": "˦",
    "small": "˧",
    "observed": "˨",
    "nobody": "˩",
    "jurisdictions": "˪",
    "opportunities": "˫",
    "manufacturing": "ˬ",
    "depending": "˭",
    "audit": "ˮ",
    "retention": "˯",
    "party": "˰",
    "gigabytes": "˱",
    "consumers": "˲",
    "sometimes": "˳",
    "documents": "˴",
    "committee": "˵",
    "rates": "˶",
    "estimated": "˷",
    "daily": "˸",
    "announced": "˹",
    "portfolio": "˺",
    "happening": "˻",
    "measuring": "˼",
    "component": "˽",
    "ten": "˾",
    "practices": "˿",
    "itself": "Ͱ",
    "aggregations": "ͱ",
    "hierarchical": "Ͳ",
    "inconsistent": "ͳ",
    "parking": "ʹ",
    "nothing": "͵",
    "measurements": "Ͷ",
    "surface": "ͷ",
    "severe": "͸",
    "tested": "͹",
    "weekly": "ͺ",
    "professional": "ͻ",
    "reading": "ͼ",
    "conversation": "ͽ",
    "receive": ";",
    "default": "Ϳ",
    "related": "΀",
    "administered": "΁",
    "temperatures": "΂",
    "gently": "΃",
    "reveals": "΄",
    "institutions": "΅",
    "dietary": "Ά",
    "restrictions": "·",
    # exp 3: remaining high-value words (savings >= 10)
    "happened": "԰",
    "activity": "Ա",
    "disaster": "Բ",
    "implemented": "Գ",
    "projects": "Դ",
    "contractual": "Ե",
    "immediately": "Զ",
    "moderate": "Է",
    "side": "Ը",
    "some": "Թ",
    "distinction": "Ժ",
    "deletion": "Ի",
    "funds": "Լ",
    "fails": "Խ",
    "advanced": "Ծ",
    "quiet": "Կ",
    "trust": "Հ",
    "approval": "Ձ",
    "code": "Ղ",
    "remediation": "Ճ",
    "gigabyte": "Մ",
    "light": "Յ",
    "its": "Z",
    "interest": "Շ",
    "early": "Ո",
    "class": "Չ",
    "included": "Պ",
    "risk": "Ջ",
    "revealed": "Ռ",
    "size": "Ս",
    "custom": "Վ",
    "points": "Տ",
    "rights": "Ր",
    "adjust": "Ց",
    "hour": "Ւ",
    "remembered": "Փ",
    "maintained": "Ք",
    "structural": "Օ",
    "entire": "Ֆ",
    "encryption": "՗",
    "less": "՘",
    "matter": "ՙ",
    "compelling": "՚",
    "proper": "՛",
    "accessible": "՜",
    "always": "՝",
    "common": "՞",
    "coffee": "՟",
    "his": "6",
    "hypothesis": "ա",
    "apparently": "բ",
    "direct": "գ",
    "shared": "դ",
    "categories": "ե",
    "per": "զ",
    "investment": "է",
    "never": "ը",
    "forward": "թ",
    "vaccine": "ժ",
    "overall": "ի",
    "imaging": "լ",
    "confirm": "խ",
    "count": "ծ",
    "watched": "կ",
    "rebuild": "հ",
    "remains": "ձ",
    "who": "ղ",
    "highest": "ճ",
    "largest": "մ",
    "built": "յ",
    "regular": "ն",
    "appears": "շ",
    "premium": "ո",
    "studies": "չ",
    "shows": "պ",
    "dataset": "ջ",
    "anxiety": "ռ",
    "reviews": "ս",
    "created": "վ",
    "walking": "տ",
    "storage": "ր",
    "since": "ց",
    "reverse": "ւ",
    "six": "փ",
    "chain": "ք",
    "evening": "օ",
    "library": "ֆ",
    "arising": "և",
    "factors": "ֈ",
    "pressed": "։",
    "uses": "֊",
    "decisions": "֋",
    "evaluated": "֌",
    "protected": "֍",
    "principle": "֎",
    "satellite": "֏",
    "may": "א",
    "temporary": "ב",
    "wednesday": "ג",
    "workspace": "ד",
    "plan": "ה",
    "expansion": "ו",
    "strongest": "ז",
    "improving": "ח",
    "maintains": "ט",
    "read": "י",
    "home": "ך",
    "preserved": "כ",
    "justifies": "ל",
    "showed": "ם",
    "proposal": "מ",
    "strong": "ן",
    "adapts": "נ",
    "intended": "ס",
    "email": "ע",
    "routes": "ף",
    "said": "פ",
    "dose": "ץ",
    "fully": "צ",
    "begin": "ק",
    "words": "ר",
    "deposits": "ש",
    "moment": "ת",
    "mobile": "ء",
    "takes": "آ",
    "risks": "أ",
    "giving": "ؤ",
    "exercise": "إ",
    "meantime": "ئ",
    "appear": "ا",
    "warranty": "ب",
    "sales": "ة",
    "uploaded": "ت",
    "taking": "ث",
    "minimize": "ج",
    "shares": "ح",
    "leads": "خ",
    "causes": "د",
    "shall": "ذ",
    "switch": "ر",
    "adults": "ز",
    "amount": "س",
    "panel": "ش",
    "november": "ص",
    "driven": "ض",
    "much": "ط",
    "executed": "ظ",
    "treating": "ع",
    "space": "غ",
    "category": "ػ",
    "image": "ؼ",
    "analysts": "ؽ",
    "beyond": "ؾ",
    "elements": "ؿ",
    "works": "ـ",
    "again": "ف",
    "caches": "ق",
    "final": "ك",
    "mass": "ل",
    "purposes": "م",
    "school": "ن",
    "recipe": "ه",
    "indirect": "و",
    "choose": "ى",
    "found": "ي",
    "backup": "ܐ",
    "gives": "ܑ",
    "fees": "ܒ",
    "comes": "ܓ",
    "produced": "ܔ",
    "combined": "ܕ",
    "transfer": "ܖ",
    "return": "ܗ",
    "episodes": "ܘ",
    "load": "ܙ",
    "push": "ܚ",
    "invoice": "ܛ",
    "binding": "ܜ",
    "carries": "ܝ",
    "cleanly": "ܞ",
    "another": "ܟ",
    "passive": "ܠ",
    "careful": "ܡ",
    "type": "ܢ",
    "shallow": "ܣ",
    "gradual": "ܤ",
    "success": "ܥ",
    "tier": "ܦ",
    "heavily": "ܧ",
    "retired": "ܨ",
    "best": "ܩ",
    "forcing": "ܪ",
    "garbage": "ܫ",
    "equally": "ܬ",
    "live": "ܭ",
    "line": "ܮ",
    "her": "ܯ",
    "caching": "ܰ",
    "parties": "ܱ",
    "written": "ܲ",
    "certain": "ܳ",
    "pain": "ܴ",
    "markets": "ܵ",
    "privacy": "ܶ",
    "vendors": "ܷ",
    "showing": "ܸ",
    # exp 15: common words in both train+val, savings >= 3
    "risen": "\x80",    # savings=9, train=2, val=1
    "solar": "\x81",    # savings=9, train=2, val=1
    "logic": "\x82",    # savings=9, train=2, val=1
    "lower": "\x83",    # savings=9, train=2, val=1
    "clear": "\x84",    # savings=9, train=2, val=1
    "write": "ߛ",    # savings=9, train=1, val=2
    "parts": "\x86",    # savings=9, train=2, val=1
    "alone": "\x87",    # savings=9, train=1, val=2
    "given": "\x88",    # savings=9, train=1, val=2
    "glass": "\x89",    # savings=9, train=2, val=1
    "usage": "\x8a",    # savings=9, train=1, val=2
    "store": "\x8b",    # savings=9, train=1, val=2
    "old": "\x8c",    # savings=9, train=8, val=1
    "fever": "\x8d",    # savings=9, train=1, val=2
    "we've": "\x8e",    # savings=9, train=2, val=1
    "later": "\x8f",    # savings=9, train=2, val=1
    "app": "\x90",    # savings=9, train=6, val=3
    "admin": "\x91",    # savings=9, train=1, val=2
    "latest": "\x92",    # savings=8, train=1, val=1
    "pull": "\x93",    # savings=8, train=3, val=1
    "viewer": "\x94",    # savings=8, train=1, val=1
    "height": "\x95",    # savings=8, train=1, val=1
    "little": "\x96",    # savings=8, train=1, val=1
    "street": "\x97",    # savings=8, train=1, val=1
    "assume": "\x98",    # savings=8, train=1, val=1
    "stress": "\x99",    # savings=8, train=1, val=1
    "trials": "\x9a",    # savings=8, train=1, val=1
    "bought": "\x9b",    # savings=8, train=1, val=1
    "left": "\x9c",    # savings=8, train=3, val=1
    "editor": "\x9d",    # savings=8, train=1, val=1
    "room": "\x9e",    # savings=8, train=3, val=1
    "repair": "\x9f",    # savings=8, train=1, val=1
    "vendor": "ݪ",    # savings=8, train=1, val=1
    "few": "ݫ",    # savings=8, train=6, val=2
    "unless": "ݬ",    # savings=8, train=1, val=1
    "nights": "ݭ",    # savings=8, train=1, val=1
    "caused": "ݮ",    # savings=8, train=1, val=1
    "launch": "ݯ",    # savings=8, train=1, val=1
    "free": "ݰ",    # savings=8, train=2, val=2
    "demand": "ݱ",    # savings=8, train=1, val=1
    "keys": "ݲ",    # savings=8, train=3, val=1
    "desk": "ݳ",    # savings=8, train=3, val=1
    "dosing": "ݴ",    # savings=8, train=1, val=1
    "cold": "ݵ",    # savings=8, train=3, val=1
    "enable": "ݶ",    # savings=8, train=1, val=1
    "global": "ݷ",    # savings=8, train=1, val=1
    "visual": "ݸ",    # savings=8, train=1, val=1
    "land": "ݹ",    # savings=8, train=3, val=1
    "images": "ݺ",    # savings=8, train=1, val=1
    "dry": "ݻ",    # savings=7, train=6, val=1
    "blood": "ݼ",    # savings=6, train=1, val=1
    "rules": "ݽ",    # savings=6, train=1, val=1
    "age": "ݾ",    # savings=6, train=5, val=1
    "valid": "ݿ",    # savings=6, train=1, val=1
    "signs": "ހ",    # savings=6, train=1, val=1
    "grown": "ށ",    # savings=6, train=1, val=1
    "might": "ނ",    # savings=6, train=1, val=1
    "sense": "ރ",    # savings=6, train=1, val=1
    "tired": "ބ",    # savings=6, train=1, val=1
    "queue": "ޅ",    # savings=6, train=1, val=1
    "flows": "ކ",    # savings=6, train=1, val=1
    "white": "އ",    # savings=6, train=1, val=1
    "lease": "ވ",    # savings=6, train=1, val=1
    "mode": "މ",    # savings=6, train=2, val=1
    "low": "ފ",    # savings=6, train=4, val=2
    "felt": "ދ",    # savings=6, train=2, val=1
    "text": "ތ",    # savings=6, train=2, val=1
    "plans": "ލ",    # savings=6, train=1, val=1
    "frame": "ގ",    # savings=6, train=1, val=1
    "trail": "ޏ",    # savings=6, train=1, val=1
    "award": "ސ",    # savings=6, train=1, val=1
    "cycle": "ޑ",    # savings=6, train=1, val=1
    "novel": "ޒ",    # savings=6, train=1, val=1
    "major": "ޓ",    # savings=6, train=1, val=1
    "bloom": "ޔ",    # savings=6, train=1, val=1
    "acute": "ޕ",    # savings=6, train=1, val=1
    "kids": "ޖ",    # savings=6, train=2, val=1
    "train": "ޗ",    # savings=6, train=1, val=1
    "fifth": "ޘ",    # savings=6, train=1, val=1
    "visit": "ޙ",    # savings=6, train=1, val=1
    "ahead": "ޚ",    # savings=6, train=1, val=1
    "note": "ޛ",    # savings=6, train=2, val=1
    "own": "ޜ",    # savings=6, train=4, val=2
    "term": "ޝ",    # savings=6, train=2, val=1
    "stood": "ޞ",    # savings=6, train=1, val=1
    "tend": "ޟ",    # savings=6, train=2, val=1
    "earth": "ޠ",    # savings=6, train=1, val=1
    "strip": "ޡ",    # savings=6, train=1, val=1
    "weird": "ޢ",    # savings=6, train=1, val=1
    "solid": "ޣ",    # savings=6, train=1, val=1
    "grief": "ޤ",    # savings=6, train=1, val=1
    "reads": "ޥ",    # savings=6, train=1, val=1
    "prior": "ޱ",    # savings=6, train=1, val=1
    "runs": "߀",    # savings=6, train=2, val=1
    "key": "߁",    # savings=5, train=4, val=1
    "off": "߂",    # savings=5, train=4, val=1
    "add": "߃",    # savings=5, train=3, val=2
    "body": "߄",    # savings=4, train=1, val=1
    "stop": "߅",    # savings=4, train=1, val=1
    "walk": "߆",    # savings=4, train=1, val=1
    "told": "߇",    # savings=4, train=1, val=1
    "too": "߈",    # savings=4, train=3, val=1
    "star": "߉",    # savings=4, train=1, val=1
    "role": "ߊ",    # savings=4, train=1, val=1
    "name": "ߋ",    # savings=4, train=1, val=1
    "top": "ߌ",    # savings=4, train=3, val=1
    "why": "ߍ",    # savings=4, train=2, val=2
    "tiny": "ߎ",    # savings=4, train=1, val=1
    "adds": "ߏ",    # savings=4, train=1, val=1
    "dead": "ߐ",    # savings=4, train=1, val=1
    "late": "ߑ",    # savings=4, train=1, val=1
    "hear": "ߒ",    # savings=4, train=1, val=1
    "main": "ߓ",    # savings=4, train=1, val=1
    "bear": "ߔ",    # savings=4, train=1, val=1
    "exit": "ߕ",    # savings=4, train=1, val=1
    "math": "ߖ",    # savings=4, train=1, val=1
    "debt": "ߗ",    # savings=4, train=1, val=1
    "say": "ߘ",    # savings=3, train=2, val=1
    "web": "ߙ",    # savings=3, train=2, val=1
    "bit": "ߚ",    # savings=3, train=2, val=1
    # NKo — train-only words (not in val), close train/val gap
    "million": "\u07dd",    # savings=65, train_only, count=13
    "infrastructure": "\u07de",    # savings=60, train_only, count=5
    "leadership": "\u07df",    # savings=56, train_only, count=7
    "collaboration": "\u07e0",    # savings=55, train_only, count=5
    "patients": "\u07e1",    # savings=54, train_only, count=9
    "participants": "\u07e2",    # savings=50, train_only, count=5
    "operations": "\u07e3",    # savings=48, train_only, count=6
    "integration": "\u07e4",    # savings=45, train_only, count=5
    "significantly": "\u07e5",    # savings=44, train_only, count=4
    "employees": "\u07e6",    # savings=42, train_only, count=6
    "switching": "\u07e7",    # savings=42, train_only, count=6
    "configured": "\u07e8",    # savings=40, train_only, count=5
    "average": "\u07e9",    # savings=40, train_only, count=8
    "protection": "\u07ea",    # savings=40, train_only, count=5
    "monitoring": "\u07f4",    # savings=40, train_only, count=5
    "seventy": "\u07f5",    # savings=40, train_only, count=8
    "maintenance": "\u07f6",    # savings=36, train_only, count=4
    "evidence": "\u07f7",    # savings=36, train_only, count=6
    "internal": "\u07f8",    # savings=36, train_only, count=6
    "accounts": "\u07f9",    # savings=36, train_only, count=6
    "acquisition": "\u07fa",    # savings=36, train_only, count=4
    "testing": "\u07fe",    # savings=35, train_only, count=7
    "customers": "\u07ff",    # savings=35, train_only, count=5
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
    "would be": "Г",
    "could be": "Д",
    "should be": "Е",
    "have been": "З",
    "will be": "И",
    "able to": "К",
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
    "in order to": "Щ",
    "with respect to": "Ъ",
    "with regard to": "Ы",
    "take into account": "Ь",
    "keep in mind": "Э",
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
    "thank you for your": "ƴ",
    "i appreciate you": "Ƶ",
    "within the next": "ƶ",
    "the end of this": "Ʒ",
    "and would like": "Ƹ",
    "to discuss the": "ƹ",
    "to inform you that": "ƺ",
    "by the end of this week": "ƻ",
    # High-value corpus phrases (exp 38) — Latin Extended A
    "the processing engine": "Ě",
    "thinking about": "Ĝ",
    "processing engine": "Ğ",
    "i've been": "Ġ",
    "the project": "Ģ",
    "the problem": "Ĥ",
    "your account": "Ħ",
    "the application": "Ĩ",
    # More corpus phrases (exp 39) — Latin Extended A
    "the ingestion pipeline": "Ī",
    "the computational cost": "Ĭ",
    "new onboarding process": "Į",
    "i've been thinking": "İ",
    "your account history": "Ĳ",
    "to make sure": "Ĵ",
    "i can": "Ķ",
    "and i": "Ĺ",
    # More high-value bigram phrases (exp 46) — Latin Extended A
    "would like": "Ļ",
    "your attention": "Ľ",
    "appreciate you": "Ŀ",
    "is that": "Ł",
    "within the": "Ń",
    "to discuss": "Ņ",
    "your identity": "Ň",
    "the upcoming": "Ŋ",
    # More phrases (exp 48) — Latin Extended A
    "however there": "Ō",
    "the approach": "Ŏ",
    "five minutes": "Ő",
    "we should": "Œ",
    "i have": "Ŕ",
    "the approach you're": "Ŗ",
    # More phrases (exp 49) — Latin Extended A
    "we need to": "Ř",
    "the new onboarding": "Ś",
    "the most important": "Ŝ",
    "the model to": "Ş",
    "the storage layer": "Š",
    "resolve the issue": "Ţ",
    "however there are": "Ť",
    "for the upcoming": "Ŧ",
    # More phrases (exp 50) — Latin Extended A
    "i wanted": "Ũ",
    "the processing": "Ū",
    "schedule a": "Ŭ",
    "i appreciate": "Ů",
    # exp 4: high-value corpus phrases
    "because the": "ā",
    "rather than": "ă",
    "thousand dollars": "ą",
    "intellectual property": "ć",
    "one hundred": "ĉ",
    "percent increase in": "ċ",
    "the same": "č",
    "during the": "ď",
    "hundred and": "đ",
    "before the": "ē",
    "percent of": "ĕ",
    "percent increase": "ė",
    "the most": "ę",
    "when the": "ě",
    "across the": "ĝ",
    "more than": "ğ",
    "under the": "ġ",
    "five hundred": "ģ",
    "rather than trying to": "ĥ",
    "you can": "ħ",
    "personal information": "ĩ",
    "i recommend": "ī",
    "the primary": "ĭ",
    "increase in": "į",
    "we need to implement": "ı",
    "if the": "ĳ",
    "two to three": "ĵ",
    "trying to": "ķ",
    "the right": "ĸ",
    "rather than trying": "ĺ",
    "two hundred": "ļ",
    "and a": "ľ",
    "need to implement": "ŀ",
    "the cost of": "ł",
    "regardless of": "ń",
    "over the": "ņ",
    "one point": "ň",
    "about what": "ŉ",
    "but the": "ŋ",
    "to your": "ō",
    "should begin": "ŏ",
    "around the": "ő",
    "i think": "œ",
    "in the first": "ŕ",
    "fifteen minutes": "ŗ",
    "the engineering": "ř",
    "two hundred and": "ś",
    "one hundred and": "ŝ",
    "the cost": "ş",
    "the default": "š",
    "is the": "ţ",
    "a single": "ť",
    "to three": "ŧ",
    "against the": "ũ",
    "i think the": "ū",
    "where the": "ŭ",
    "until the": "ů",
    "the third": "Ű",
    "four thousand": "ű",
    "that actually": "Ų",
    "the migration": "ų",
    "to prevent": "Ŵ",
    "the entire": "ŵ",
    "can be": "Ŷ",
    "related to": "ŷ",
    "dollars in": "Ÿ",
    "subject to": "Ź",
    "the contract": "ź",
    "the standard": "Ż",
    "strategy for": "ż",
    "to implement": "Ž",
    "depending on": "ž",
    "the best": "ſ",
    "is available": "Έ",
    "the previous": "Ή",
    "arising from": "Ί",
    "across three": "΋",
    "with four": "Ό",
    "since the": "΍",
    "the event": "Ύ",
    "think the": "Ώ",
    "the total": "ΐ",
    "of our": "΢",
    "in a": "Ϊ",
    "the process": "Ϋ",
    "ten minutes": "ά",
    "expected to": "έ",
    "is expected": "ή",
    "is the most": "ί",
    "at the cost": "ΰ",
    "to a": "ς",
    "cost of": "ϊ",
    "needs to": "ϋ",
    "receive an": "ό",
    "which is": "ύ",
    "like a": "ώ",
    "a complete": "Ϗ",
    "across all": "ϐ",
    "that our": "ϑ",
    "your first": "ϒ",
    "do not": "ϓ",
    "a separate": "ϔ",
    "appears to": "ϕ",
    "for a": "ϖ",
    "was a": "ϗ",
    "in under": "Ϙ",
    "two to": "ϙ",
    "leads to": "Ϛ",
    "to six": "ϛ",
    "over a": "Ϝ",
    "to one": "ϝ",
    "to two": "Ϟ",
    "you for": "ϟ",
    "to maintain": "Ϡ",
    "apply to": "ϡ",
    "into the": "Ϣ",
    "a new": "ϣ",
    "to think": "Ϥ",
    "the full": "ϥ",
    "right to": "Ϧ",
    "team has": "ϧ",
    "the last": "Ϩ",
    "for each": "ϩ",
    "not just": "Ϫ",
    "than ten": "ϫ",
    "with his": "Ϭ",
    "what you": "ϭ",
    "have the": "Ϯ",
    # ── n-gram expansion (exp 15): 293 new phrases, savings >= 8 ──
    # Sorted by byte_savings descending
    "analysis of": "£",  # savings=72, train=7, val=1
    "two to three weeks": "©",  # savings=64, train=3, val=1
    "engineering team": "Ɣ",  # savings=56, train=3, val=1
    "three weeks": "ƨ",  # savings=54, train=5, val=1
    "fifteen percent": "Ƽ",  # savings=52, train=3, val=1
    "one hundred percent": "ƽ",  # savings=51, train=2, val=1
    "real time": "ƿ",  # savings=49, train=6, val=1
    "to three weeks": "ǀ",  # savings=48, train=3, val=1
    "thousand years": "ǆ",  # savings=48, train=3, val=1
    "one percent": "ǉ",  # savings=45, train=3, val=2
    "approximately one": "Ǘ",  # savings=45, train=2, val=1
    "at the cost of slightly": "Ȉ",  # savings=42, train=1, val=1
    "approximately one point": "ȸ",  # savings=42, train=1, val=1
    "the distinction between": "ɝ",  # savings=42, train=1, val=1
    "thirty seven": "ɵ",  # savings=40, train=3, val=1
    "eighteen months": "ɺ",  # savings=39, train=2, val=1
    "hundred percent": "ɽ",  # savings=39, train=2, val=1
    "the permissions model": "ʄ",  # savings=38, train=1, val=1
    "every thirty seconds": "ʕ",  # savings=36, train=1, val=1
    "at the cost of": "ʘ",  # savings=36, train=2, val=1
    "than trying to": "ʥ",  # savings=36, train=2, val=1
    "forty seven": "ρ",  # savings=36, train=2, val=2
    "the cost of slightly": "σ",  # savings=36, train=1, val=1
    "dietary restrictions": "ϯ",  # savings=36, train=1, val=1
    "eight hours": "ϰ",  # savings=36, train=2, val=2
    "the engineering team": "ϱ",  # savings=36, train=1, val=1
    "thirty seconds": "ϲ",  # savings=36, train=1, val=2
    "twenty four": "ϳ",  # savings=36, train=3, val=1
    "to think about": "ϴ",  # savings=36, train=2, val=1
    "to twenty": "ϵ",  # savings=35, train=4, val=1
    "in the jurisdiction": "϶",  # savings=34, train=1, val=1
    "binding arbitration": "Ϸ",  # savings=34, train=1, val=1
    "thousand dollars in": "ϸ",  # savings=34, train=1, val=1
    "starting conditions": "Ϲ",  # savings=34, train=1, val=1
    "distinction between": "Ϻ",  # savings=34, train=1, val=1
    "have to think about": "ϻ",  # savings=34, train=1, val=1
    "seven percent": "ϼ",  # savings=33, train=2, val=1
    "sixty percent": "Ͻ",  # savings=33, train=2, val=1
    "five years": "Ͼ",  # savings=32, train=3, val=1
    "ninety one percent": "Ͽ",  # savings=32, train=1, val=1
    "has been requested": "Л",  # savings=32, train=1, val=1
    "physical activity": "ѹ",  # savings=30, train=1, val=1
    "forty eight hours": "ҕ",  # savings=30, train=1, val=1
    "approved the": "ҙ",  # savings=30, train=2, val=1
    "side effects": "ҝ",  # savings=30, train=2, val=1
    "treating everyone": "ԅ",  # savings=30, train=1, val=1
    "hundred and fifty": "Ԉ",  # savings=30, train=1, val=1
    "permissions model": "ԉ",  # savings=30, train=1, val=1
    "in read only mode": "Ԋ",  # savings=30, train=1, val=1
    "opportunities and": "ԋ",  # savings=30, train=1, val=1
    "before initiating": "Ԍ",  # savings=30, train=1, val=1
    "industry analysts": "ԍ",  # savings=30, train=1, val=1
    "the third quarter": "Ԏ",  # savings=30, train=1, val=1
    "the jurisdiction": "ԏ",  # savings=28, train=1, val=1
    "cost of slightly": "Ԑ",  # savings=28, train=1, val=1
    "upcoming product": "ԑ",  # savings=28, train=1, val=1
    "depending on the": "Ԓ",  # savings=28, train=1, val=1
    "milligrams daily": "ԓ",  # savings=28, train=1, val=1
    "level and": "Ԕ",  # savings=28, train=3, val=1
    "has been updated": "ԕ",  # savings=28, train=1, val=1
    "from a": "Ԗ",  # savings=28, train=4, val=3
    "last year": "ԗ",  # savings=28, train=3, val=1
    "fourteen percent": "Ԙ",  # savings=28, train=1, val=1
    "permissions from": "ԙ",  # savings=28, train=1, val=1
    "two percent": "Ԛ",  # savings=27, train=2, val=1
    "to be": "ԛ",  # savings=27, train=6, val=3
    "support the": "Ԝ",  # savings=27, train=1, val=2
    "than trying": "ԝ",  # savings=27, train=2, val=1
    "ninety days": "Ԟ",  # savings=27, train=2, val=1
    "engineering and": "ԟ",  # savings=26, train=1, val=1
    "will be used to": "Ԡ",  # savings=26, train=1, val=1
    "doesn't produce": "ԡ",  # savings=26, train=1, val=1
    "the distinction": "Ԣ",  # savings=26, train=1, val=1
    "administered in": "ԣ",  # savings=26, train=1, val=1
    "the permissions": "Ԥ",  # savings=26, train=1, val=1
    "in the meantime": "ԥ",  # savings=26, train=1, val=1
    "its own": "Ԧ",  # savings=25, train=3, val=2
    "twelve percent": "ԧ",  # savings=24, train=1, val=1
    "read only mode": "Ԩ",  # savings=24, train=1, val=1
    "ninety one": "ԩ",  # savings=24, train=2, val=1
    "one point four": "Ԫ",  # savings=24, train=1, val=1
    "mobile app": "ԫ",  # savings=24, train=1, val=2
    "been requested": "Ԭ",  # savings=24, train=1, val=1
    "the real": "ԭ",  # savings=24, train=3, val=1
    "last month": "Ԯ",  # savings=24, train=2, val=1
    "is expected to": "ԯ",  # savings=24, train=1, val=1
    "privacy policy": "־",  # savings=24, train=1, val=1
    "a twelve": "׀",  # savings=24, train=3, val=1
    "twenty minutes": "׃",  # savings=24, train=1, val=1
    "implementing a": "׆",  # savings=24, train=1, val=1
    "as the primary": "ׯ",  # savings=24, train=1, val=1
    "percent of the": "װ",  # savings=24, train=1, val=1
    "eighty percent": "ױ",  # savings=24, train=1, val=1
    "attorney fees": "ײ",  # savings=22, train=1, val=1
    "assessment of": "׳",  # savings=22, train=1, val=1
    "justifies the": "״",  # savings=22, train=1, val=1
    "three seconds": "؆",  # savings=22, train=1, val=1
    "with the most": "؇",  # savings=22, train=1, val=1
    "what you said": "؈",  # savings=22, train=1, val=1
    "appears to be": "؉",  # savings=22, train=1, val=1
    "have to think": "؊",  # savings=22, train=1, val=1
    "or related to": "؋",  # savings=22, train=1, val=1
    "the strongest": "،",  # savings=22, train=1, val=1
    "your existing": "؍",  # savings=22, train=1, val=1
    "available for": "؎",  # savings=22, train=1, val=1
    "revealed that": "؏",  # savings=22, train=1, val=1
    "a remediation": "؛",  # savings=22, train=1, val=1
    "fourteen days": "؝",  # savings=22, train=1, val=1
    "third quarter": "؞",  # savings=22, train=1, val=1
    "point two": "؟",  # savings=21, train=2, val=1
    "of ninety": "ؠ",  # savings=21, train=2, val=1
    "adapts to": "٠",  # savings=21, train=2, val=1
    "there's a": "١",  # savings=21, train=2, val=1
    "every thirty": "٢",  # savings=20, train=1, val=1
    "because they": "٣",  # savings=20, train=1, val=1
    "through your": "٤",  # savings=20, train=1, val=1
    "dollars over": "٥",  # savings=20, train=1, val=1
    "been updated": "٦",  # savings=20, train=1, val=1
    "and felt the": "٧",  # savings=20, train=1, val=1
    "the meantime": "٨",  # savings=20, train=1, val=1
    "duration and": "٩",  # savings=20, train=1, val=1
    "will be used": "٪",  # savings=20, train=1, val=1
    "to the total": "٫",  # savings=20, train=1, val=1
    "about twenty": "٬",  # savings=20, train=1, val=1
    "available on": "٭",  # savings=20, train=1, val=1
    "right answer": "ٮ",  # savings=20, train=1, val=1
    "reaching for": "ٯ",  # savings=20, train=1, val=1
    "in read only": "ٱ",  # savings=20, train=1, val=1
    "system with": "ٲ",  # savings=18, train=1, val=1
    "time and": "ٳ",  # savings=18, train=2, val=1
    "to minimize": "ٴ",  # savings=18, train=1, val=1
    "outcomes it": "ٵ",  # savings=18, train=1, val=1
    "updated the": "ٶ",  # savings=18, train=1, val=1
    "year the": "ٷ",  # savings=18, train=2, val=1
    "week and": "ٸ",  # savings=18, train=2, val=1
    "admin panel": "ٹ",  # savings=18, train=1, val=1
    "reports and": "ٺ",  # savings=18, train=1, val=1
    "third party": "ٻ",  # savings=18, train=1, val=1
    "the vaccine": "ټ",  # savings=18, train=1, val=1
    "parking lot": "ٽ",  # savings=18, train=1, val=1
    "thirty days": "پ",  # savings=18, train=1, val=1
    "the patient": "ٿ",  # savings=18, train=1, val=1
    "of slightly": "ڀ",  # savings=18, train=1, val=1
    "built in": "ځ",  # savings=18, train=1, val=2
    "caused by a": "ڂ",  # savings=18, train=1, val=1
    "seconds and": "ڃ",  # savings=18, train=1, val=1
    "but i think": "ڄ",  # savings=18, train=1, val=1
    "four to six": "څ",  # savings=18, train=1, val=1
    "and regular": "چ",  # savings=18, train=1, val=1
    "the dataset": "ڇ",  # savings=18, train=1, val=1
    "and version": "ڈ",  # savings=18, train=1, val=1
    "updates the": "ډ",  # savings=18, train=1, val=1
    "forty eight": "ڊ",  # savings=18, train=1, val=1
    "of forty": "ڋ",  # savings=18, train=1, val=2
    "the parking": "ڌ",  # savings=18, train=1, val=1
    "thirty one": "ڍ",  # savings=16, train=1, val=1
    "rates have": "ڎ",  # savings=16, train=1, val=1
    "in our": "ڏ",  # savings=16, train=3, val=1
    "may be": "ڐ",  # savings=16, train=3, val=1
    "this month": "ڑ",  # savings=16, train=1, val=1
    "found that": "ڒ",  # savings=16, train=1, val=1
    "number and": "ړ",  # savings=16, train=1, val=1
    "of our top": "ڔ",  # savings=16, train=1, val=1
    "be used to": "ڕ",  # savings=16, train=1, val=1
    "to fifteen": "ږ",  # savings=16, train=1, val=1
    "next month": "ڗ",  # savings=16, train=1, val=1
    "the reason": "ژ",  # savings=16, train=1, val=1
    "common and": "ڙ",  # savings=16, train=1, val=1
    "as the": "ښ",  # savings=16, train=2, val=2
    "or related": "ڛ",  # savings=16, train=1, val=1
    "point four": "ڜ",  # savings=16, train=1, val=1
    "is fifteen": "ڝ",  # savings=16, train=1, val=1
    "to address": "ڞ",  # savings=16, train=1, val=1
    "updated to": "ڟ",  # savings=16, train=1, val=1
    "up through": "ڠ",  # savings=16, train=1, val=1
    "percent to": "ڡ",  # savings=16, train=1, val=1
    "on its own": "ڢ",  # savings=16, train=1, val=1
    "demand for": "ڣ",  # savings=16, train=1, val=1
    "to request": "ڤ",  # savings=16, train=1, val=1
    "with acute": "ڥ",  # savings=16, train=1, val=1
    "four point": "ڦ",  # savings=16, train=1, val=1
    "of fifteen": "ڧ",  # savings=16, train=1, val=1
    "created by": "ڨ",  # savings=16, train=1, val=1
    "watched it": "ک",  # savings=16, train=1, val=1
    "most users": "ڪ",  # savings=16, train=1, val=1
    "tier which": "ګ",  # savings=16, train=1, val=1
    "of a": "ڬ",  # savings=16, train=6, val=2
    "was not": "ڭ",  # savings=15, train=2, val=1
    "and one": "ڮ",  # savings=15, train=2, val=1
    "tend to": "گ",  # savings=15, train=2, val=1
    "the two": "ڰ",  # savings=15, train=2, val=1
    "in your": "ڱ",  # savings=15, train=2, val=1
    "with no": "ڲ",  # savings=15, train=2, val=1
    "no more": "ڳ",  # savings=15, train=1, val=2
    "a small": "ڴ",  # savings=15, train=2, val=1
    "for all": "ڵ",  # savings=15, train=2, val=1
    "in this": "ڶ",  # savings=15, train=2, val=1
    "because i": "ڷ",  # savings=14, train=1, val=1
    "long term": "ڸ",  # savings=14, train=1, val=1
    "read only": "ڹ",  # savings=14, train=1, val=1
    "given the": "ں",  # savings=14, train=1, val=1
    "i can see": "ڻ",  # savings=14, train=1, val=1
    "at ninety": "ڼ",  # savings=14, train=1, val=1
    "with less": "ڽ",  # savings=14, train=1, val=1
    "i believe": "ھ",  # savings=14, train=1, val=1
    "against a": "ڿ",  # savings=14, train=1, val=1
    "only mode": "ۀ",  # savings=14, train=1, val=1
    "i want to": "ہ",  # savings=14, train=1, val=1
    "caused by": "ۂ",  # savings=14, train=1, val=1
    "costs and": "ۃ",  # savings=14, train=1, val=1
    "for three": "ۄ",  # savings=14, train=1, val=1
    "a fifteen": "ۅ",  # savings=14, train=1, val=1
    "two years": "ۆ",  # savings=14, train=1, val=1
    "a passive": "ۇ",  # savings=14, train=1, val=1
    "and fifty": "ۈ",  # savings=14, train=1, val=1
    "months of": "ۉ",  # savings=14, train=1, val=1
    "answer is": "ۊ",  # savings=14, train=1, val=1
    "might not": "ۋ",  # savings=14, train=1, val=1
    "driven by": "ی",  # savings=14, train=1, val=1
    "it's been": "ۍ",  # savings=14, train=1, val=1
    "a version": "ێ",  # savings=14, train=1, val=1
    "that your": "ۏ",  # savings=14, train=1, val=1
    "hours per": "ې",  # savings=14, train=1, val=1
    "the space": "ۑ",  # savings=14, train=1, val=1
    "that most": "ے",  # savings=14, train=1, val=1
    "the glass": "ۓ",  # savings=14, train=1, val=1
    "twelve to": "۔",  # savings=14, train=1, val=1
    "even when": "ە",  # savings=14, train=1, val=1
    "each week": "۞",  # savings=14, train=1, val=1
    "you want": "ۥ",  # savings=12, train=1, val=1
    "had been": "ۦ",  # savings=12, train=1, val=1
    "you said": "۩",  # savings=12, train=1, val=1
    "of those": "ۮ",  # savings=12, train=1, val=1
    "and is": "ۯ",  # savings=12, train=2, val=1
    "tired of": "۰",  # savings=12, train=1, val=1
    "days the": "۱",  # savings=12, train=1, val=1
    "just the": "۲",  # savings=12, train=1, val=1
    "risen to": "۳",  # savings=12, train=1, val=1
    "a full": "۴",  # savings=12, train=2, val=1
    "felt the": "۵",  # savings=12, train=1, val=1
    "so the": "۶",  # savings=12, train=2, val=1
    "an email": "۷",  # savings=12, train=1, val=1
    "plans to": "۸",  # savings=12, train=1, val=1
    "but i": "۹",  # savings=12, train=3, val=1
    "you when": "ۺ",  # savings=12, train=1, val=1
    "sure the": "ۻ",  # savings=12, train=1, val=1
    "and felt": "ۼ",  # savings=12, train=1, val=1
    "signs of": "۽",  # savings=12, train=1, val=1
    "of their": "۾",  # savings=12, train=1, val=1
    "a set of": "ۿ",  # savings=12, train=1, val=1
    "data the": "܀",  # savings=12, train=1, val=1
    "to add": "܁",  # savings=12, train=2, val=1
    "a few": "܂",  # savings=12, train=3, val=1
    "at two": "܃",  # savings=12, train=2, val=1
    "to reach": "܄",  # savings=12, train=1, val=1
    "within a": "܅",  # savings=12, train=1, val=1
    "a target": "܆",  # savings=12, train=1, val=1
    "fails to": "܇",  # savings=12, train=1, val=1
    "dose of": "܈",  # savings=10, train=1, val=1
    "isn't a": "܉",  # savings=10, train=1, val=1
    "now and": "܊",  # savings=10, train=1, val=1
    "to take": "܋",  # savings=10, train=1, val=1
    "to four": "܌",  # savings=10, train=1, val=1
    "up here": "܍",  # savings=10, train=1, val=1
    "our top": "ݍ",  # savings=10, train=1, val=1
    "four to": "ݎ",  # savings=10, train=1, val=1
    "size of": "ݏ",  # savings=10, train=1, val=1
    "and she": "ݐ",  # savings=10, train=1, val=1
    "the day": "ݑ",  # savings=10, train=1, val=1
    "by a": "ݒ",  # savings=10, train=3, val=2
    "on a": "ݓ",  # savings=10, train=4, val=1
    "see why": "ݔ",  # savings=10, train=1, val=1
    "in read": "ݕ",  # savings=10, train=1, val=1
    "cost is": "ݖ",  # savings=10, train=1, val=1
    "can see": "ݗ",  # savings=10, train=1, val=1
    "be used": "ݘ",  # savings=10, train=1, val=1
    "a clear": "ݙ",  # savings=10, train=1, val=1
    "an hour": "ݚ",  # savings=10, train=1, val=1
    "not a": "ݛ",  # savings=9, train=2, val=1
    "a ten": "ݜ",  # savings=9, train=2, val=1
    "add a": "ݝ",  # savings=9, train=2, val=1
    "set of": "ݞ",  # savings=8, train=1, val=1
    "is now": "ݟ",  # savings=8, train=1, val=1
    "by two": "ݠ",  # savings=8, train=1, val=1
    "in two": "ݡ",  # savings=8, train=1, val=1
    "i am": "ݢ",  # savings=8, train=3, val=1
    "and an": "ݣ",  # savings=8, train=1, val=1
    "on any": "ݤ",  # savings=8, train=1, val=1
    "on its": "ݥ",  # savings=8, train=1, val=1
    "i want": "ݦ",  # savings=8, train=1, val=1
    "i just": "ݧ",  # savings=8, train=1, val=1
    "uses a": "ݨ",  # savings=8, train=1, val=1
    "a four": "ݩ",  # savings=8, train=1, val=1
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
