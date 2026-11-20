"""Command-line demo for MINIMATE's week-9 baseline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from minimate.task_manager import TaskManager
from minimate.storage import SQLiteStore
from minimate.intent_baseline import KeywordIntentClassifier
from minimate.intent_hf import HFIntentClassifier, ClassifierError, DEFAULT_MODEL_DIR


def main() -> None:
    # PowerShell hosts can still expose a legacy code page on Windows.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if not sys.stdin.isatty() and hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description="MINIMATE seven-intent baseline")
    parser.add_argument("--text", help="Run one Vietnamese input then exit.")
    parser.add_argument('--classifier', choices=('hf', 'keyword'), default='hf')
    parser.add_argument('--model-dir', type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument('--db', default=str(Path(__file__).resolve().parents[1] / 'data' / 'minimate.db'))
    args = parser.parse_args()
    try:
        classifier = HFIntentClassifier(args.model_dir) if args.classifier == 'hf' else KeywordIntentClassifier()
    except ClassifierError as error:
        parser.exit(1, f'{error}\n')
    database_path = Path(args.db)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    manager = TaskManager(classifier=classifier, store=SQLiteStore(database_path))
    if args.text is not None:
        _print_response(manager.handle(args.text).to_dict())
        manager.store.close()
        return
    print("MINIMATE sẵn sàng. Gõ 'exit', 'quit' hoặc 'thoát' để dừng.")
    while True:
        try:
            text = input("Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nĐã kết thúc MINIMATE.")
            break
        if text.lower() in {"thoát", "thoat", "exit", "quit"}:
            break
        _print_response(manager.handle(text).to_dict())
    manager.store.close()


def _print_response(response: dict[str, object]) -> None:
    """Show a human-readable answer followed by the required JSON contract."""
    print(f"MINIMATE: {response['text']}")
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except ClassifierError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
