"""Local presentation demo for the Mini-language compiler.
Run with ``python app.py`` and open http://127.0.0.1:5000.
"""

from pathlib import Path

from flask import Flask, jsonify, render_template, request

from src.ast.printer import format_ast
from src.codegen.tac_generator import TacGenerator
from src.main import format_symbol_table, format_tokens
from src.parser.parse import parse_source_to_ast
from src.semantic.semantic_analyzer import SemanticAnalyzer


app = Flask(__name__)


@app.get("/")
def index():
    """Render the standalone compiler demonstration page."""
    example_path = Path(__file__).parent / "tests" / "valid" / "valid_program.mini"
    return render_template("index.html", example_code=example_path.read_text(encoding="utf-8"))


@app.post("/compile")
def compile_source():
    """Run the established compiler pipeline and return its display outputs."""
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("code"), str):
        return jsonify(_error_response("Request body must be JSON with a string 'code' field.")), 400

    source = payload["code"]
    try:
        program = parse_source_to_ast(source)
    except SyntaxError as error:
        return jsonify(_error_response(f"Syntax error: {error}"))
    except Exception as error:  # Defensive: retain a useful local-demo response.
        return jsonify(_error_response(f"Compilation error: {error}"))

    analyzer = SemanticAnalyzer()
    semantic_errors = analyzer.analyze(program)
    if semantic_errors:
        messages = [
            f"Semantic error [{error.rule}] line {error.line}: {error.message}"
            for error in semantic_errors
        ]
        return jsonify(_error_response("\n".join(messages)))

    return jsonify(
        {
            "tokens": format_tokens(source),
            "ast": format_ast(program),
            "symtable": format_symbol_table(analyzer),
            "tac": "\n".join(TacGenerator().generate(program)),
            "errors": "",
        }
    )


def _error_response(message: str) -> dict[str, str]:
    """Match compiler-stage gating by clearing normal outputs after a failure."""
    return {"tokens": "", "ast": "", "symtable": "", "tac": "", "errors": message}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
