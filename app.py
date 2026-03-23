"""
Contradicta — Detecting what doesn't add up.
AI-powered contradiction and misleading claim detector for healthcare text.
"""

import streamlit as st
import re
from itertools import combinations

# ─── Page Config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="Contradicta",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Mono', monospace;
    background-color: #0a0a0f;
    color: #e2e2e8;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2rem 4rem 2rem; max-width: 820px; }

/* ── Hero Header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
    position: relative;
}
.hero::before {
    content: "";
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,60,60,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.8rem;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #ff3c3c 0%, #ff8c42 50%, #e2e2e8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1;
}
.hero-tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: #666677;
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 0.6rem;
}
.hero-bar {
    width: 60px; height: 3px;
    background: linear-gradient(90deg, #ff3c3c, #ff8c42);
    margin: 1.4rem auto 0 auto;
    border-radius: 2px;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #ff3c3c;
    margin-bottom: 0.5rem;
    margin-top: 1.8rem;
}

/* ── Streamlit widget overrides ── */
.stTextArea textarea {
    background: #111118 !important;
    border: 1px solid #2a2a38 !important;
    border-radius: 8px !important;
    color: #e2e2e8 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: #ff3c3c !important;
    box-shadow: 0 0 0 2px rgba(255,60,60,0.15) !important;
}
.stFileUploader {
    background: #111118 !important;
    border: 1px dashed #2a2a38 !important;
    border-radius: 8px !important;
    padding: 0.5rem !important;
}
.stButton > button {
    background: linear-gradient(135deg, #ff3c3c, #cc2020) !important;
    color: white !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.65rem 2.5rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ff5555, #e02828) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(255,60,60,0.3) !important;
}

/* ── Result Cards ── */
.result-box {
    background: #111118;
    border: 1px solid #2a2a38;
    border-radius: 10px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0;
}
.claim-item {
    display: flex;
    gap: 0.8rem;
    align-items: flex-start;
    padding: 0.55rem 0;
    border-bottom: 1px solid #1e1e2a;
    font-size: 0.82rem;
    line-height: 1.6;
}
.claim-item:last-child { border-bottom: none; }
.claim-num {
    background: #1e1e2a;
    color: #666677;
    font-size: 0.65rem;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
    margin-top: 2px;
    letter-spacing: 1px;
}

/* ── Contradiction Cards ── */
.contradiction-card {
    background: rgba(255, 60, 60, 0.05);
    border: 1px solid rgba(255, 60, 60, 0.3);
    border-left: 3px solid #ff3c3c;
    border-radius: 8px;
    padding: 1.1rem 1.3rem;
    margin: 0.8rem 0;
}
.c-vs {
    font-size: 0.6rem;
    letter-spacing: 3px;
    color: #ff3c3c;
    text-transform: uppercase;
    text-align: center;
    margin: 0.5rem 0;
}
.c-sentence {
    font-size: 0.8rem;
    color: #c8c8d4;
    line-height: 1.6;
    background: #0d0d14;
    padding: 0.5rem 0.8rem;
    border-radius: 5px;
    margin: 0.3rem 0;
}
.c-explanation {
    font-size: 0.72rem;
    color: #888898;
    margin-top: 0.7rem;
    padding-top: 0.6rem;
    border-top: 1px solid rgba(255,60,60,0.15);
}
.confidence-badge {
    display: inline-block;
    background: rgba(255,60,60,0.12);
    color: #ff7070;
    font-size: 0.6rem;
    letter-spacing: 1px;
    padding: 2px 7px;
    border-radius: 3px;
    margin-left: 0.5rem;
    text-transform: uppercase;
}

/* ── No-contradiction state ── */
.clean-state {
    background: rgba(40, 200, 100, 0.05);
    border: 1px solid rgba(40, 200, 100, 0.25);
    border-left: 3px solid #28c864;
    border-radius: 8px;
    padding: 1rem 1.3rem;
    font-size: 0.82rem;
    color: #60d890;
}

/* ── Credibility Score ── */
.score-wrapper {
    text-align: center;
    padding: 2rem 1rem;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
}
.score-label {
    font-size: 0.65rem;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #666677;
    margin-top: 0.4rem;
}
.score-bar-bg {
    background: #1e1e2a;
    border-radius: 99px;
    height: 6px;
    margin: 1.2rem auto;
    max-width: 280px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.8s ease;
}
.score-verdict {
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.5rem;
}

/* ── Divider ── */
.subtle-divider {
    border: none;
    border-top: 1px solid #1e1e2a;
    margin: 2rem 0;
}

/* ── Loading override ── */
.stSpinner > div {
    border-top-color: #ff3c3c !important;
}

/* ── Info box ── */
.info-pill {
    display: inline-block;
    background: #1a1a24;
    border: 1px solid #2a2a38;
    border-radius: 6px;
    font-size: 0.7rem;
    color: #888898;
    padding: 0.4rem 0.8rem;
    margin: 0.3rem 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ─── Lazy Imports (so Streamlit loads fast before heavy models) ───────────────

@st.cache_resource(show_spinner=False)
def load_nli_model():
    """
    Load the NLI pipeline once and cache it.
    facebook/bart-large-mnli is a zero-shot / NLI model that classifies
    (premise, hypothesis) pairs as entailment / neutral / contradiction.
    """
    from transformers import pipeline
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=-1,          # CPU — change to 0 for GPU
    )


def extract_text_from_image(image_file) -> str:
    """
    Step OCR: use pytesseract to pull text out of an uploaded image.
    Returns an empty string if pytesseract or Pillow is missing.
    """
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_file)
        return pytesseract.image_to_string(img)
    except ImportError:
        st.warning("⚠️ pytesseract / Pillow not installed. OCR unavailable.", icon="⚠️")
        return ""
    except Exception as e:
        st.warning(f"⚠️ OCR failed: {e}")
        return ""


# ─── NLP Helpers ──────────────────────────────────────────────────────────────

def split_into_claims(text: str) -> list[str]:
    """
    Step 1 — Sentence splitting.
    Uses a simple regex to split on sentence boundaries.
    Filters out very short or empty fragments.
    """
    # Split on . ? ! followed by whitespace or end-of-string
    raw = re.split(r'(?<=[.?!])\s+', text.strip())
    claims = [s.strip() for s in raw if len(s.strip()) > 20]
    return claims


def classify_pair(nli, premise: str, hypothesis: str) -> dict:
    """
    Step 2 — NLI classification for a single sentence pair.

    We frame the task as zero-shot classification:
      - The premise is the first sentence.
      - The hypothesis is the second sentence.
    Labels: ["entailment", "neutral", "contradiction"]

    Returns the top label and its score.
    """
    result = nli(
        premise,
        candidate_labels=["entailment", "neutral", "contradiction"],
        hypothesis_template="{}",      # hypothesis is the second sentence
        multi_label=False,
    )
    # Reframe: use hypothesis as the actual hypothesis text
    result2 = nli(
        f"{premise} [SEP] {hypothesis}",
        candidate_labels=["These statements are consistent",
                          "These statements are contradictory",
                          "These statements are unrelated"],
        multi_label=False,
    )
    label_map = {
        "These statements are consistent": "entailment",
        "These statements are contradictory": "contradiction",
        "These statements are unrelated": "neutral",
    }
    top_label = label_map[result2["labels"][0]]
    top_score = result2["scores"][0]
    return {"label": top_label, "score": top_score}


def analyze_claims(claims: list[str], nli) -> list[dict]:
    """
    Step 3 — Compare every unique pair of claims.
    Returns a list of contradiction findings.
    """
    findings = []
    pairs = list(combinations(range(len(claims)), 2))

    progress = st.progress(0, text="Analyzing claim pairs…")
    for i, (a, b) in enumerate(pairs):
        result = classify_pair(nli, claims[a], claims[b])
        if result["label"] == "contradiction":
            findings.append({
                "idx_a": a,
                "idx_b": b,
                "sentence_a": claims[a],
                "sentence_b": claims[b],
                "score": result["score"],
            })
        progress.progress((i + 1) / len(pairs),
                          text=f"Checking pair {i+1} of {len(pairs)}…")
    progress.empty()
    return findings


def compute_credibility(claims: list[str], contradictions: list[dict]) -> int:
    """
    Simple credibility heuristic:
      - Start at 100.
      - Each contradiction deducts points proportional to confidence.
      - More total claims = smaller per-contradiction penalty (more context).
    """
    if not claims:
        return 100
    base_penalty = max(5, 40 // max(len(claims) - 1, 1))
    score = 100
    for c in contradictions:
        deduction = int(base_penalty * c["score"])
        score -= deduction
    return max(0, min(100, score))


# ─── UI Helpers ───────────────────────────────────────────────────────────────

def score_color(score: int) -> str:
    if score >= 75:
        return "#28c864"
    elif score >= 45:
        return "#ff8c42"
    else:
        return "#ff3c3c"


def score_verdict(score: int) -> str:
    if score >= 75:
        return "Likely Consistent"
    elif score >= 45:
        return "Moderate Inconsistency"
    else:
        return "High Inconsistency Risk"


# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    # Hero
    st.markdown("""
    <div class="hero">
        <div class="hero-title">CONTRADICTA</div>
        <div class="hero-tagline">Helping you make sense of conflicting health information</div>
        <div class="hero-bar"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input Section ────────────────────────────────────────────────────────
    st.markdown('<div class="section-label">01 — Input</div>', unsafe_allow_html=True)

    text_input = st.text_area(
        label="Paste healthcare text here",
        placeholder=(
            "Paste a healthcare article, patient summary, or a medical advice you want to check.\n\n"
            "Example: Vitamin C cures the common cold. No supplement has been proven "
            "to cure the common cold. Daily vitamin C reduces cold duration by 8%."
        ),
        height=180,
        label_visibility="collapsed",
    )

    st.caption("*THIS TOOL HIGHLIGHTS PATTERNS AND INCONSISTENCIES, BUT DOES NOT PROVIDE MEDICAL ADVICE.*")

    st.markdown('<div class="section-label">02 — Upload Image</div>',
                unsafe_allow_html=True)
    uploaded_image = st.file_uploader(
        label="Upload image",
        type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top:1.2rem'></div>", unsafe_allow_html=True)
    run = st.button("⚡ ANALYZE")

    # ── Analysis ─────────────────────────────────────────────────────────────
    if run:
        # Merge text sources
        combined_text = text_input.strip()

        if uploaded_image:
            with st.spinner("Extracting text from image…"):
                ocr_text = extract_text_from_image(uploaded_image)
            if ocr_text.strip():
                combined_text = combined_text + "\n" + ocr_text
                st.markdown(
                    f'<div class="result-box"><span class="info-pill">OCR extracted '
                    f'{len(ocr_text.split())} words from image</span></div>',
                    unsafe_allow_html=True,
                )

        if not combined_text:
            st.error("Please enter text or upload an image first.")
            return

        # Step 1: Sentence splitting
        claims = split_into_claims(combined_text)
        if len(claims) < 2:
            st.warning("Need at least 2 sentences to detect contradictions. "
                       "Please add more text.")
            return

        # Step 2 & 3: Load model + classify
        with st.spinner("Loading NLI model (first run may take ~30 s)…"):
            nli = load_nli_model()

        contradictions = analyze_claims(claims, nli)
        score = compute_credibility(claims, contradictions)

        st.markdown('<hr class="subtle-divider">', unsafe_allow_html=True)

        # ── Output: Claims List ───────────────────────────────────────────────
        st.markdown('<div class="section-label">03 — Extracted Claims</div>',
                    unsafe_allow_html=True)
        claims_html = '<div class="result-box">'
        for i, claim in enumerate(claims):
            claims_html += (
                f'<div class="claim-item">'
                f'<span class="claim-num">#{i+1:02d}</span>'
                f'<span>{claim}</span>'
                f'</div>'
            )
        claims_html += "</div>"
        st.markdown(claims_html, unsafe_allow_html=True)

        # ── Output: Contradictions ────────────────────────────────────────────
        st.markdown('<div class="section-label">04 — Contradiction Analysis</div>',
                    unsafe_allow_html=True)

        if not contradictions:
            st.markdown(
                '<div class="clean-state">No major issues detected in the claims.</div>',
                unsafe_allow_html=True,
            )
        else:
            for c in contradictions:
                conf_pct = int(c["score"] * 100)
                st.markdown(f"""
                <div class="contradiction-card">
                    <div style="display:flex; align-items:center; margin-bottom:0.3rem;">
                        <span style="font-size:0.65rem; letter-spacing:2px; color:#ff3c3c; text-transform:uppercase;">
                            Contradiction
                        </span>
                        <span class="confidence-badge">{conf_pct}% confidence</span>
                        <span style="margin-left:auto; font-size:0.65rem; color:#444455;">
                            Claims #{c['idx_a']+1} vs #{c['idx_b']+1}
                        </span>
                    </div>
                    <div class="c-sentence">{c['sentence_a']}</div>
                    <div class="c-vs">— contradicts —</div>
                    <div class="c-sentence">{c['sentence_b']}</div>
                    <div class="c-explanation">
                        These two statements appear inconsistent with each other.
                        Review them carefully before sharing or acting on this information.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Output: Credibility Score ─────────────────────────────────────────
        st.markdown('<div class="section-label">05 — Consistency Score</div>',
                    unsafe_allow_html=True)

        color = score_color(score)
        verdict = score_verdict(score)
        bar_pct = score

        st.markdown(f"""
        <div class="result-box">
            <div class="score-wrapper">
                <div class="score-number" style="color:{color}">{score}</div>
                <div class="score-label">Credibility Score / 100</div>
                <div class="score-bar-bg">
                    <div class="score-bar-fill"
                         style="width:{bar_pct}%; background:{color}">
                    </div>
                </div>
                <div class="score-verdict" style="color:{color}">{verdict}</div>
            </div>
            <div style="border-top:1px solid #1e1e2a; padding-top:1rem; margin-top:0.5rem;
                        font-size:0.72rem; color:#666677; line-height:1.8; text-align:center;">
                <span class="info-pill">{len(claims)} claims analysed</span>
                <span class="info-pill">{len(contradictions)} contradiction(s) found</span>
                <span class="info-pill">Model: facebook/bart-large-mnli</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:0.65rem; color:#444455; text-align:center;
                    margin-top:1.5rem; letter-spacing:1px;">
            CONTRADICTA · AI analysis only · Not a substitute for professional medical advice
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
