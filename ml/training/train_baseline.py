"""CLI: python -m ml.training.train_baseline prices.csv --output artifacts/baseline.json"""
import argparse
import json

from ml.training.baselines import train_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Train an experimental chronological ATLAS baseline")
    parser.add_argument("csv_path", help="Authorized CSV containing date,close columns")
    parser.add_argument("--output", default="artifacts/ridge-baseline.json")
    args = parser.parse_args()
    result = train_csv(args.csv_path, args.output)
    print(json.dumps({"output": args.output, "metrics": result["metrics"]}, indent=2))


if __name__ == "__main__":
    main()
