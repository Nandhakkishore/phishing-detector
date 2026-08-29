import pandas as pd

if __name__ == "__main__":
    splits = ["train", "val", "test"]

    for split in splits:
        url_df = pd.read_csv(f"dataset/processed/{split}_url_features.csv")
        content_df = pd.read_csv(f"dataset/processed/{split}_content_features.csv")

        # Sanity check: same row count and same labels in the same order
        assert len(url_df) == len(content_df), f"Row count mismatch in {split}"
        assert (url_df["label"].values == content_df["label"].values).all(), \
            f"Label mismatch in {split} — rows are not aligned!"

        # Drop the duplicate label column from one side before merging
        content_features_only = content_df.drop(columns=["label"])

        hybrid_df = pd.concat([url_df, content_features_only], axis=1)

        output_path = f"dataset/processed/{split}_hybrid_features.csv"
        hybrid_df.to_csv(output_path, index=False)
        print(f"{split}: hybrid shape {hybrid_df.shape} -> saved to {output_path}")

    print("\nDone. Hybrid feature files saved to dataset/processed/")