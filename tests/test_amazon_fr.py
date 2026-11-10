"""amazon.fr markup: French labels, epoch-ms order dates and review-type tabs."""

import pytest

from vine_search import amazon

FR = "https://www.amazon.fr"


@pytest.fixture(autouse=True)
def french_storefront(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(amazon, "AMAZON_HOSTS", frozenset({"amazon.fr", "www.amazon.fr"}))
    monkeypatch.setattr(amazon, "ORIGIN", FR)


def test_review_tabs_found_by_review_type() -> None:
    html = (
        '<a href="/vine/vine-reviews?review-type=pending_review">En attente</a>'
        '<a href="/vine/vine-reviews?review-type=completed">Avis envoyés</a>'
    )
    tabs = amazon.review_sections(html, f"{FR}/vine/vine-reviews")
    assert tabs == {
        "awaiting_review": f"{FR}/vine/vine-reviews?review-type=pending_review",
        "reviewed": f"{FR}/vine/vine-reviews?review-type=completed",
    }


def test_french_review_row() -> None:
    html = """<div id="vvp-items-grid-container"><p>Affichage de 1-1 sur 1 résultats</p>
    <table class="vvp-reviews-table"><tbody><tr class="vvp-reviews-table--row">
    <td class="vvp-reviews-table--text-col"><a href="/dp/B0ABCDEFGH">
      <span class="a-truncate-full">Lampe de bureau</span></a></td>
    <td class="vvp-reviews-table--text-col" data-order-timestamp="1762732800000">10/11/2025</td>
    <td class="vvp-reviews-table--text-col">Pas encore examiné</td>
    </tr></tbody></table></div>"""
    page = amazon.parse_reviews(html, f"{FR}/vine/vine-reviews?review-type=completed", "reviewed")
    assert page.state == "ok", page.message
    (row,) = page.reviews
    assert row["asin"] == "B0ABCDEFGH"
    assert row["order_date"] == "2025-11-10"
    assert row["observed_status"] == "Pas encore examiné"
    assert row["product_url"] == f"{FR}/dp/B0ABCDEFGH"
    assert page.advertised_count == 1


def test_french_etv_and_unavailable() -> None:
    product = {"asin": "B0ABCDEFGH", "title": "Lampe"}
    html = '<a href="/dp/B0ABCDEFGH">Lampe</a><p>Valeur fiscale estimée : 1&#8239;234,56 €</p>'
    details = amazon.parse_product_details(html, product, product_id=1)
    assert details["etv"] == "1 234,56 €"
    gone = amazon.parse_product_details("<p>Actuellement indisponible.</p>", product, product_id=1)
    assert gone["state"] == "unavailable"
