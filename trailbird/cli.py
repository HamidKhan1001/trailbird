"""Command line: `trailbird identify clip.wav [--json]`."""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from .errors import TrailbirdError
from .notes import load_notes
from .predictor import BirdNETPredictor
from .results import format_markdown
from .service import Identifier


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trailbird", description="Offline bird-call identifier.")
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch-model", help="Download the model once (the only step that needs internet).")
    ident = sub.add_parser("identify", help="Identify the bird in an audio file.")
    ident.add_argument("audio", help="Path to a wav/flac/ogg/mp3 file.")
    ident.add_argument("--json", action="store_true", help="Machine-readable output.")
    ident.add_argument("-k", type=int, default=3, help="Number of species to return (default 3).")
    ident.add_argument(
        "--allow-network",
        action="store_true",
        help="Do not block outbound connections during inference (default: blocked).",
    )
    return p


def main(argv: Sequence[str] | None = None, predictor_factory=BirdNETPredictor) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "fetch-model":
        try:
            predictor_factory().load()
        except TrailbirdError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print("Model ready. From now on TrailBird runs fully offline.")
        return 0
    try:
        identifier = Identifier(
            predictor_factory(),
            load_notes(),
            k=args.k,
            enforce_offline=not args.allow_network,
        )
        result = identifier.identify(args.audio)
    except TrailbirdError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        notes = {result.predictions[0].scientific_name: result.note} if result.predictions else {}
        print(format_markdown(result.predictions, {k: v for k, v in notes.items() if v}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
