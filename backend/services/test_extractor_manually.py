from live_content_extractor import extract_live_content_features

result = extract_live_content_features("https://www.python.org")
for k, v in result.items():
    print(f"{k}: {v}")