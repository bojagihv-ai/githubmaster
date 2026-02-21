from app.normalizers.schema import PromotionEvent, compute_fingerprint, compute_identity_key


def test_fingerprint_stable():
    e = PromotionEvent(provider="x", event_title="t", source_url="http://example.com")
    a = compute_fingerprint(e)
    b = compute_fingerprint(e)
    assert a == b


def test_identity_key_stable_for_same_identity():
    a = PromotionEvent(provider="x", event_title="Promo", event_type="other", source_url="http://example.com")
    b = PromotionEvent(provider="x", event_title="Promo", event_type="other", source_url="http://example.com")
    assert compute_identity_key(a) == compute_identity_key(b)
