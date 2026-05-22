from pathlib import Path
import subprocess
import json


class PreparedRunnerError(RuntimeError):
    pass


def run_command(args: list[str], cwd: Path):
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        raise PreparedRunnerError(result.stderr or result.stdout)
    return result.stdout


def run_prepared_evaluation(repo_root: Path, predictions_csv: Path, report_path: Path):
    truth_path = repo_root / "round1" / "ground_truth.csv"
    if not truth_path.exists():
        raise PreparedRunnerError("round1/ground_truth.csv was not found")

    run_command([
        "python",
        "scripts/sanitize_predictions.py",
        "--pred",
        str(predictions_csv),
    ], cwd=repo_root)

    run_command([
        "python",
        "scripts/eval.py",
        "--truth",
        str(truth_path),
        "--pred",
        str(predictions_csv),
        "--out",
        str(report_path),
    ], cwd=repo_root)

    return json.loads(report_path.read_text(encoding="utf-8"))
