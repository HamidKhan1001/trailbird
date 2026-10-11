from trailbird.predictor import aggregate, split_species
from trailbird.results import DISCLAIMER, Prediction, format_markdown, is_uncertain, top_k


def P(name, c):
    return Prediction(name, f"Sci {name}", c)


def test_top_k_sorted_and_limited():
    out = top_k([P("a", 0.1), P("b", 0.9), P("c", 0.5), P("d", 0.3)], 3)
    assert [p.common_name for p in out] == ["b", "c", "d"]


def test_confident_result_not_uncertain():
    assert not is_uncertain([P("a", 0.9), P("b", 0.2)])


def test_low_confidence_is_uncertain():
    assert is_uncertain([P("a", 0.3), P("b", 0.1)])


def test_close_top_two_is_uncertain():
    assert is_uncertain([P("a", 0.8), P("b", 0.75)])


def test_empty_is_uncertain_and_formats():
    assert is_uncertain([])
    assert "No bird detected" in format_markdown([])


def test_markdown_flags_uncertain_and_has_disclaimer():
    md = format_markdown([P("a", 0.3), P("b", 0.1)])
    assert "UNCERTAIN" in md and DISCLAIMER in md


def test_markdown_shows_three_rows_and_note():
    preds = [P("a", 0.9), P("b", 0.4), P("c", 0.2)]
    md = format_markdown(preds, {"Sci a": "sings at dawn"})
    assert md.count("| 1 |") == 1 and "| 3 |" in md and "sings at dawn" in md


def test_split_species():
    assert split_species("Turdus merula_Common Blackbird") == ("Common Blackbird", "Turdus merula")


def test_aggregate_takes_max_per_species_and_clamps():
    out = aggregate([("A b_X", 0.2), ("A b_X", 0.7), ("C d_Y", 1.5)], k=3)
    assert out[0].common_name == "Y" and out[0].confidence == 1.0
    assert out[1].confidence == 0.7
