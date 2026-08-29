import pandas as pd

# Content-derived columns from the PhiUSIIL dataset —
# these represent webpage structure/content signals, not the URL string itself.
CONTENT_COLUMNS = [
    "LineOfCode", "LargestLineLength", "HasTitle",
    "DomainTitleMatchScore", "URLTitleMatchScore", "HasFavicon",
    "Robots", "IsResponsive", "NoOfURLRedirect", "NoOfSelfRedirect",
    "HasDescription", "NoOfPopup", "NoOfiFrame",
    "HasExternalFormSubmit", "HasSocialNet", "HasSubmitButton",
    "HasHiddenFields", "HasPasswordField", "Bank", "Pay", "Crypto",
    "HasCopyrightInfo", "NoOfImage", "NoOfCSS", "NoOfJS",
    "NoOfSelfRef", "NoOfEmptyRef", "NoOfExternalRef",
]


def extract_content_features(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in CONTENT_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected content columns: {missing}")

    content_df = df[CONTENT_COLUMNS].copy()
    content_df["label"] = df["label"].values
    return content_df


if __name__ == "__main__":
    splits = ["train", "val", "test"]
    for split in splits:
        input_path = f"dataset/splits/{split}.csv"
        output_path = f"dataset/processed/{split}_content_features.csv"
        print(f"Processing {split}...")

        df = pd.read_csv(input_path)
        content_df = extract_content_features(df)
        content_df.to_csv(output_path, index=False)

        print(f"  -> saved {content_df.shape} to {output_path}")

    print("\nDone. All content feature files saved to dataset/processed/")