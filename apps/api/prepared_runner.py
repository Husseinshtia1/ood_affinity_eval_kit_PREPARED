from pathlib import Path
import subprocess
import json

class PreparedRunnerError(RuntimeError):
    pass


def run_command(args:list[str], cwd:Path):
    result=subprocess.run(args,cwd=str(cwd),capture_output=True,text=True)
    if result.returncode!=0:
        raise PreparedRunnerError(result.stderr)
    return result.stdout


def run_prepared_evaluation(repo_root:Path,predictions_csv:Path,report_path:Path):

    run_command([
        'python',
        'scripts/sanitize_predictions.py',
        '--input',str(predictions_csv)
    ],cwd=repo_root)

    run_command([
        'python',
        'scripts/eval.py',
        '--predictions',str(predictions_csv),
        '--out',str(report_path)
    ],cwd=repo_root)

    return json.loads(report_path.read_text())