import subprocess
import sys


def test_cli_prints_tokens_and_completed_scope_history():
    result = subprocess.run(
        [
            sys.executable, "-m", "src.main", "tests/valid/valid_program.mini",
            "--tokens", "--symtable",
        ],
        capture_output=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 0
    assert "Tokens:\n  INT: 'int' (line 5)" in result.stdout
    assert "Symbol table:\n  Active scope 0:" in result.stdout
    assert "inner: type=int, scope=1, declared_line=21" in result.stdout
