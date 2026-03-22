"""
HLC Autoresearch — Corpus Builder v2
======================================
Generates a large, diverse corpus for HLC optimization.

300 samples across 15 categories, split 70/15/15 (train/val/holdout).
- Train (210): agent optimizes against this
- Validation (45): agent sees this score (prevents overfitting)
- Holdout (45): human-only, never seen by agent

Uses Claude API to generate unique, diverse samples. Each sample is
a realistic paragraph of English text (250-500 chars).

Usage:
    pip install anthropic
    python build_corpus_v2.py              # Generate full corpus
    python build_corpus_v2.py --dry-run    # Show plan without generating
"""

import json
import random
import sys
import os
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("pip install anthropic")
    sys.exit(1)

random.seed(73)  # different seed from v1

# ═══════════════════════════════════════════════════════════
# CATEGORIES — 15 categories × 20 samples each = 300 total
# ═══════════════════════════════════════════════════════════

CATEGORIES = {
    # --- Carried over (different samples than v1) ---
    "technical": {
        "description": "Software engineering discussions: debugging, architecture, performance, systems design",
        "guidance": "Write as an engineer talking to peers. Mention specific technologies, metrics, tradeoffs. Vary between frontend, backend, infra, data, ML.",
    },
    "casual": {
        "description": "Everyday conversation between friends or acquaintances",
        "guidance": "Natural, informal tone. Topics: weekend plans, hobbies, complaints, stories, recommendations. Use contractions freely.",
    },
    "business": {
        "description": "Professional workplace communication: strategy, operations, management",
        "guidance": "Formal but not stiff. Topics: quarterly results, vendor negotiations, hiring, process changes, budgets. Include specific numbers.",
    },
    "documentation": {
        "description": "Technical documentation: API docs, system architecture, configuration guides",
        "guidance": "Clear, precise, instructional. Describe components, data flows, configuration options. Include specific parameter names and values.",
    },
    "creative": {
        "description": "Fiction, narrative prose, descriptive writing",
        "guidance": "Literary quality. Vary genre: mystery, sci-fi, literary fiction, memoir-style, historical. Focus on vivid sensory detail and character.",
    },
    "email": {
        "description": "Professional emails: updates, requests, announcements, follow-ups",
        "guidance": "Email conventions: greetings, action items, deadlines. Mix internal/external, formal/semi-formal. Include specific dates and names.",
    },
    "ai_conversation": {
        "description": "AI assistant responses: explanations, advice, technical help",
        "guidance": "Helpful, clear, structured. Topics: coding help, concept explanations, recommendations, analysis. Vary complexity.",
    },
    "support": {
        "description": "Customer support interactions: troubleshooting, account issues, billing",
        "guidance": "Patient, solution-oriented. Include ticket-like specifics: error codes, account details, steps taken. Mix agent and customer perspectives.",
    },
    # --- New categories ---
    "academic": {
        "description": "Academic and scientific writing: research summaries, methodology, analysis",
        "guidance": "Scholarly tone. Topics: psychology, biology, economics, physics, linguistics, computer science. Include methodology details and findings.",
    },
    "instructional": {
        "description": "How-to guides, tutorials, step-by-step instructions",
        "guidance": "Clear sequential instructions. Topics: cooking, DIY, software setup, fitness, photography. Include specific quantities and steps.",
    },
    "legal": {
        "description": "Legal language: contracts, terms of service, compliance, regulatory",
        "guidance": "Formal legal prose. Topics: data privacy, employment terms, liability, licensing, regulatory compliance. Use precise legal language.",
    },
    "medical": {
        "description": "Healthcare communication: clinical notes, patient education, research",
        "guidance": "Clinical precision mixed with patient-friendly language. Topics: symptoms, treatments, drug interactions, preventive care, clinical trials.",
    },
    "journalism": {
        "description": "News reporting and editorial writing",
        "guidance": "Inverted pyramid style for news, persuasive for editorial. Topics: politics, technology, environment, economy, culture. Include quotes and data.",
    },
    "marketing": {
        "description": "Marketing copy: product descriptions, campaigns, brand messaging",
        "guidance": "Persuasive, benefit-focused. Topics: SaaS products, consumer goods, event promotion, case studies. Vary between B2B and B2C.",
    },
    "conversational_ai": {
        "description": "Multi-turn dialogue: debates, interviews, panel discussions",
        "guidance": "Natural dialogue with multiple speakers. Topics: technology ethics, education policy, startup advice, book clubs. Include disagreement and nuance.",
    },
}

SAMPLES_PER_CATEGORY = 20  # 20 × 15 = 300 total


def generate_samples(client, category, description, guidance, n=20):
    """Generate n diverse text samples for a category using Claude."""
    samples = []

    # Generate in batches of 5 for diversity
    for batch in range(0, n, 5):
        batch_size = min(5, n - batch)
        batch_num = batch // 5 + 1
        total_batches = (n + 4) // 5

        prompt = f"""Generate exactly {batch_size} unique English text samples for the category: {category}

Description: {description}
Style guidance: {guidance}

RULES:
- Each sample must be a single paragraph, 250-500 characters long
- Each sample must use DIFFERENT vocabulary, topics, and sentence structures
- This is batch {batch_num} of {total_batches} — make these distinct from typical examples
- No two samples should start the same way
- Use natural, realistic English (not stilted or formulaic)
- Do NOT include any meta-commentary, labels, or numbering
- Vary sentence length within each sample (mix short and long sentences)

Output ONLY a JSON array of {batch_size} strings. No other text, no markdown, no explanation.
Example format: ["Sample one text here.", "Sample two text here."]"""

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text[: text.rfind("```")]
            text = text.strip()

        try:
            batch_samples = json.loads(text)
            for s in batch_samples:
                if isinstance(s, str) and 150 < len(s) < 800:
                    samples.append({"category": category, "text": s})
        except json.JSONDecodeError:
            print(f"  WARNING: Failed to parse batch {batch_num} for {category}, retrying...")
            continue

        print(f"  {category}: batch {batch_num}/{total_batches} → {len(samples)} samples")

    return samples[:n]


def build_corpus(corpus):
    """Split corpus into train/val/holdout with stratified sampling."""
    categories = {}
    for sample in corpus:
        cat = sample["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(sample)

    train = []
    val = []
    holdout = []

    for cat, samples in sorted(categories.items()):
        random.shuffle(samples)
        n = len(samples)
        # 70/15/15 split
        n_train = int(n * 0.7)
        n_val = int(n * 0.15)
        # rest goes to holdout

        train.extend(samples[:n_train])
        val.extend(samples[n_train : n_train + n_val])
        holdout.extend(samples[n_train + n_val :])

    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(holdout)

    return train, val, holdout


def print_stats(train, val, holdout):
    """Print corpus statistics."""
    for name, split in [("Train", train), ("Validation", val), ("Holdout", holdout)]:
        chars = sum(len(s["text"]) for s in split)
        words = sum(len(s["text"].split()) for s in split)
        cats = {}
        for s in split:
            cats[s["category"]] = cats.get(s["category"], 0) + 1
        print(f"\n{name}: {len(split)} samples, {chars:,} chars, {words:,} words")
        print(f"  Avg length: {chars // len(split)} chars/sample")
        print(f"  Categories: {dict(sorted(cats.items()))}")


def save_corpus(train, val, holdout, corpus_dir):
    """Save all splits to JSON."""
    corpus_dir.mkdir(exist_ok=True)

    with open(corpus_dir / "train.json", "w") as f:
        json.dump(train, f, indent=2)
    with open(corpus_dir / "val.json", "w") as f:
        json.dump(val, f, indent=2)
    with open(corpus_dir / "holdout.json", "w") as f:
        json.dump(holdout, f, indent=2)

    print(f"\nSaved to {corpus_dir}/")
    print(f"  train.json:   {len(train)} samples")
    print(f"  val.json:     {len(val)} samples")
    print(f"  holdout.json: {len(holdout)} samples")


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("DRY RUN — showing plan without generating\n")
        print(f"Categories: {len(CATEGORIES)}")
        print(f"Samples per category: {SAMPLES_PER_CATEGORY}")
        print(f"Total samples: {len(CATEGORIES) * SAMPLES_PER_CATEGORY}")
        print(f"\nSplit: 70% train / 15% val / 15% holdout")
        n_total = len(CATEGORIES) * SAMPLES_PER_CATEGORY
        print(f"  Train:    ~{int(n_total * 0.7)} samples")
        print(f"  Val:      ~{int(n_total * 0.15)} samples")
        print(f"  Holdout:  ~{int(n_total * 0.15)} samples")
        print(f"\nCategories:")
        for cat, info in CATEGORIES.items():
            print(f"  {cat}: {info['description']}")
        return

    client = anthropic.Anthropic()

    print(f"Generating {len(CATEGORIES) * SAMPLES_PER_CATEGORY} samples across {len(CATEGORIES)} categories...\n")

    all_samples = []
    for cat, info in CATEGORIES.items():
        samples = generate_samples(
            client, cat, info["description"], info["guidance"], SAMPLES_PER_CATEGORY
        )
        all_samples.extend(samples)
        print(f"  ✓ {cat}: {len(samples)} samples generated")

    print(f"\nTotal generated: {len(all_samples)} samples")

    train, val, holdout = build_corpus(all_samples)
    print_stats(train, val, holdout)

    corpus_dir = Path(__file__).parent / "corpus"
    save_corpus(train, val, holdout, corpus_dir)


if __name__ == "__main__":
    main()
