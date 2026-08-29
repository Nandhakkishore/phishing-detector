import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

TIMEOUT_SECONDS = 6.0
HEADERS = {"User-Agent": "Mozilla/5.0 (PhishingDetectorResearchBot/1.0)"}

BANK_WORDS = ["bank", "account", "iban", "swift"]
PAY_WORDS = ["paypal", "payment", "checkout", "billing"]
CRYPTO_WORDS = ["crypto", "bitcoin", "wallet", "blockchain", "ethereum"]


def fetch_page(url: str):
    with httpx.Client(follow_redirects=True, timeout=TIMEOUT_SECONDS, headers=HEADERS) as client:
        response = client.get(url)
        return response.text, response.status_code


def extract_live_content_features(url: str) -> dict:
    parsed_target = urlparse(url)
    domain = parsed_target.hostname or ""

    try:
        html, status_code = fetch_page(url)
    except Exception as e:
        return {
            "fetch_success": 0,
            "fetch_error": str(e),
            **_default_content_features(),
        }

    soup = BeautifulSoup(html, "html.parser")

    lines = html.splitlines()
    line_of_code = len(lines)
    largest_line_length = max((len(l) for l in lines), default=0)

    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    has_title = int(bool(title_text))

    domain_title_match = _text_domain_similarity(title_text, domain)
    url_title_match = _text_domain_similarity(title_text, url)

    has_favicon = int(bool(soup.find("link", rel=lambda x: x and "icon" in x.lower())))
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    has_robots = int(bool(robots_meta))

    viewport_meta = soup.find("meta", attrs={"name": "viewport"})
    is_responsive = int(bool(viewport_meta))

    forms = soup.find_all("form")
    has_external_form_submit = int(any(
        f.get("action", "").startswith("http") and domain not in f.get("action", "")
        for f in forms
    ))
    has_submit_button = int(any(
        f.find("button", type="submit") or f.find("input", type="submit")
        for f in forms
    ))
    has_hidden_fields = int(any(f.find("input", type="hidden") for f in forms))
    has_password_field = int(bool(soup.find("input", type="password")))

    social_links = ["facebook.com", "twitter.com", "instagram.com", "linkedin.com"]
    has_social_net = int(any(s in html.lower() for s in social_links))

    desc_meta = soup.find("meta", attrs={"name": "description"})
    has_description = int(bool(desc_meta))

    has_copyright = int("©" in html or "copyright" in html.lower())

    num_popup = len(soup.find_all("script", string=lambda s: s and "window.open" in s))
    num_iframe = len(soup.find_all("iframe"))
    num_image = len(soup.find_all("img"))
    num_css = len(soup.find_all("link", rel="stylesheet"))
    num_js = len(soup.find_all("script"))

    all_links = [a.get("href", "") for a in soup.find_all("a")]
    num_self_ref = sum(1 for l in all_links if l.startswith("#") or domain in l)
    num_empty_ref = sum(1 for l in all_links if l in ("", "#", "javascript:void(0)"))
    num_external_ref = sum(1 for l in all_links if l.startswith("http") and domain not in l)

    html_lower = html.lower()
    has_bank = int(any(w in html_lower for w in BANK_WORDS))
    has_pay = int(any(w in html_lower for w in PAY_WORDS))
    has_crypto = int(any(w in html_lower for w in CRYPTO_WORDS))

    return {
        "fetch_success": 1,
        "LineOfCode": line_of_code,
        "LargestLineLength": largest_line_length,
        "HasTitle": has_title,
        "DomainTitleMatchScore": domain_title_match,
        "URLTitleMatchScore": url_title_match,
        "HasFavicon": has_favicon,
        "Robots": has_robots,
        "IsResponsive": is_responsive,
        "NoOfURLRedirect": 0,
        "NoOfSelfRedirect": 0,
        "HasDescription": has_description,
        "NoOfPopup": num_popup,
        "NoOfiFrame": num_iframe,
        "HasExternalFormSubmit": has_external_form_submit,
        "HasSocialNet": has_social_net,
        "HasSubmitButton": has_submit_button,
        "HasHiddenFields": has_hidden_fields,
        "HasPasswordField": has_password_field,
        "Bank": has_bank,
        "Pay": has_pay,
        "Crypto": has_crypto,
        "HasCopyrightInfo": has_copyright,
        "NoOfImage": num_image,
        "NoOfCSS": num_css,
        "NoOfJS": num_js,
        "NoOfSelfRef": num_self_ref,
        "NoOfEmptyRef": num_empty_ref,
        "NoOfExternalRef": num_external_ref,
    }


def _text_domain_similarity(text: str, reference: str) -> float:
    if not text or not reference:
        return 0.0
    text_tokens = set(text.lower().split())
    ref_tokens = set(reference.lower().replace(".", " ").replace("/", " ").split())
    if not text_tokens or not ref_tokens:
        return 0.0
    overlap = text_tokens & ref_tokens
    return round(len(overlap) / max(len(text_tokens), 1), 4)


def _default_content_features() -> dict:
    return {
        "LineOfCode": 0, "LargestLineLength": 0, "HasTitle": 0,
        "DomainTitleMatchScore": 0.0, "URLTitleMatchScore": 0.0,
        "HasFavicon": 0, "Robots": 0, "IsResponsive": 0,
        "NoOfURLRedirect": 0, "NoOfSelfRedirect": 0, "HasDescription": 0,
        "NoOfPopup": 0, "NoOfiFrame": 0, "HasExternalFormSubmit": 0,
        "HasSocialNet": 0, "HasSubmitButton": 0, "HasHiddenFields": 0,
        "HasPasswordField": 0, "Bank": 0, "Pay": 0, "Crypto": 0,
        "HasCopyrightInfo": 0, "NoOfImage": 0, "NoOfCSS": 0, "NoOfJS": 0,
        "NoOfSelfRef": 0, "NoOfEmptyRef": 0, "NoOfExternalRef": 0,
    }