from pathlib import Path
import subprocess
import json
import csv


class PreparedRunnerError(RuntimeError):
    pass


def run_command(args: list[str], cwd: Path):
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
    if result.returncode != 0:
        raise PreparedRunnerError(result.stderr or result.stdout)
    return result.stdout


def _read_truth(path: Path) -> dict[str, float]:
    with path.open(newline='', encoding='utf-8') as f:
        return {row['id']: float(row['pK']) for row in csv.DictReader(r for r in f if r.strip() and not r.startswith('#'))}


def _read_pred(path: Path) -> dict[str, float]:
    with path.open(newline='', encoding='utf-8') as f:
        return {row['id']: float(row['y_pred_pK']) for row in csv.DictReader(r for r in f if r.strip() and not r.startswith('#'))}


def export_parity_points(truth_path: Path, predictions_csv: Path, points_path: Path) -> list[dict]:
    truth = _read_truth(truth_path)
    pred = _read_pred(predictions_csv)
    points = [
        {'id': item_id, 'truth': truth_value, 'prediction': pred[item_id]}
        for item_id, truth_value in truth.items()
        if item_id in pred
    ]
    points_path.write_text(json.dumps({'points': points}, indent=2), encoding='utf-8')
    return points


def run_prepared_evaluation(repo_root: Path, predictions_csv: Path, report_path: Path, points_path: Path | None = None):
    truth_path = repo_root / 'round1' / 'ground_truth.csv'
    if not truth_path.exists():
        raise PreparedRunnerError('round1/ground_truth.csv was not found')

    run_command([
        'python',
        'scripts/sanitize_predictions.py',
        '--pred',
        str(predictions_csv),
    ], cwd=repo_root)

    run_command([
        'python',
        'scripts/eval.py',
        '--truth',
        str(truth_path),
        '--pred',
        str(predictions_csv),
        '--out',
        str(report_path),
    ], cwd=repo_root)

    if points_path is not None:
        export_parity_points(truth_path, predictions_csv, points_path)

    return json.loads(report_path.read_text(encoding='utf-8'))
