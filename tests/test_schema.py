from app.normalizers.schema import PromotionEvent, compute_fingerprint


def test_fingerprint_stable():
    e = PromotionEvent(provider="x", event_title="t", source_url="http://example.com")
    a = compute_fingerprint(e)
    b = compute_fingerprint(e)
    assert a == b
