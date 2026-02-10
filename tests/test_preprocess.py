from pathlib import Path
import subprocess
import sys


def test_preprocess_runs_and_creates_output():
    """
    Very simple test:
    Runs preprocessing script and checks that
    the interim parquet file exists.
    """

    # run preprocess script
    result = subprocess.run(
        [sys.executable, "src/data/preprocess.py"],
        capture_output=True,
        text=True,
    )

    # script should exit successfully
    assert result.returncode == 0, result.stderr

    # check output file exists
    out_file = Path("data/interim/panel_base.parquet")
    assert out_file.exists()
