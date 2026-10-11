import json

from trailbird.cli import main
from trailbird.errors import ModelError

from .conftest import FakePredictor


def test_json_output(wav_path, confident_preds, capsys):
    rc = main(["identify", str(wav_path), "--json"], predictor_factory=lambda: FakePredictor(confident_preds))
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert len(out["predictions"]) == 3 and out["uncertain"] is False


def test_text_output_has_disclaimer(wav_path, confident_preds, capsys):
    main(["identify", str(wav_path)], predictor_factory=lambda: FakePredictor(confident_preds))
    assert "not a definitive" in capsys.readouterr().out


def test_missing_file_exit_code_2(tmp_path, capsys):
    rc = main(["identify", str(tmp_path / "nope.wav")], predictor_factory=lambda: FakePredictor())
    assert rc == 2 and "not found" in capsys.readouterr().err


def test_model_load_failure_exit_code_2(wav_path, capsys):
    def boom():
        raise ModelError("model missing")

    assert main(["identify", str(wav_path)], predictor_factory=boom) == 2
    assert "model missing" in capsys.readouterr().err


def test_fetch_model_success(capsys):
    assert main(["fetch-model"], predictor_factory=lambda: FakePredictor()) == 0
    assert "offline" in capsys.readouterr().out


def test_fetch_model_failure(capsys):
    def boom():
        raise ModelError("no network")

    assert main(["fetch-model"], predictor_factory=boom) == 2
    assert "no network" in capsys.readouterr().err
