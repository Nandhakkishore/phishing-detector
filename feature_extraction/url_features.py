import re
import math
from urllib.parse import urlparse
import pandas as pd

# Known shortener domains (common ones)
SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "shorte.st", "cutt.ly", "rebrand.ly", "tiny.cc"
}

# Suspicious keywords often seen in phishing URLs
SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "update", "account", "signin",
    "banking", "confirm", "webscr", "password", "billing", "suspend"
]

IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


def shannon_entropy(s: str) -> float:
    """Measures randomness of characters in a string — phishing URLs
    often use random-looking subdomains/paths with higher entropy."""
    if not s:
        return 0.0
    prob = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def extract_url_features(url: str) -> dict:
    url = str(url).strip()
    features = {}

    # --- Basic parsing ---
    parsed = urlparse(url if "://" in url else "http://" + url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    query = parsed.query or ""

    # --- Length-based features ---
    features["url_length"] = len(url)
    features["hostname_length"] = len(hostname)
    features["path_length"] = len(path)

    # --- Character counts ---
    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_digits"] = sum(c.isdigit() for c in url)
    features["num_special_chars"] = len(re.findall(r"[@%~=&+#!*,]", url))
    features["num_underscores"] = url.count("_")
    features["num_slashes"] = url.count("/")
    features["num_question_marks"] = url.count("?")
    features["num_equals"] = url.count("=")
    features["num_at_symbols"] = url.count("@")

    # --- Structural features ---
    features["has_ip"] = int(bool(IP_PATTERN.match(hostname)))
    features["has_https"] = int(parsed.scheme == "https")
    features["num_subdomains"] = max(hostname.count(".") - 1, 0) if hostname else 0
    features["has_port"] = int(parsed.port is not None)

    # --- Shortener detection ---
    features["is_shortened"] = int(hostname.lower() in SHORTENERS)

    # --- Suspicious keyword count ---
    url_lower = url.lower()
    features["suspicious_word_count"] = sum(
        1 for w in SUSPICIOUS_WORDS if w in url_lower
    )

    # --- Redirect indicator (rough heuristic: extra "http" occurrences,
    # or "//" appearing again after the initial protocol) ---
    features["num_redirect_indicators"] = url_lower.count("http", url_lower.find("://") + 3)

    # --- Entropy ---
    features["hostname_entropy"] = shannon_entropy(hostname)

    # --- Ratios (guard against divide-by-zero) ---
    features["digit_ratio"] = features["num_digits"] / len(url) if len(url) else 0
    features["special_char_ratio"] = features["num_special_chars"] / len(url) if len(url) else 0

    return features


def build_feature_dataframe(input_csv: str, url_col: str = "URL", label_col: str = "label") -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    feature_rows = df[url_col].apply(extract_url_features)
    feature_df = pd.DataFrame(list(feature_rows))
    feature_df[label_col] = df[label_col].values
    return feature_df


if __name__ == "__main__":
    splits = ["train", "val", "test"]
    for split in splits:
        input_path = f"dataset/splits/{split}.csv"
        output_path = f"dataset/processed/{split}_url_features.csv"
        print(f"Processing {split}...")
        feat_df = build_feature_dataframe(input_path)
        feat_df.to_csv(output_path, index=False)
        print(f"  -> saved {feat_df.shape} to {output_path}")

    print("\nDone. All URL feature files saved to dataset/processed/")