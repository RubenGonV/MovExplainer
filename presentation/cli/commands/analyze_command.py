"""
Analyze Command CLI.

This script parses arguments, sets up the application container,
and executes the AnalyzePosition use case.
"""

import argparse
import sys

# Ensure project root is in path for imports to work if run directly
import os

from container import Container
from application.dto.analysis_request import AnalysisRequest
from presentation.cli.formatters.json_formatter import JsonFormatter

sys.path.append(os.getcwd())


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze a chess position.")
    parser.add_argument(
        "--fen",
        type=str,
        required=True,
        help="FEN string of the position to analyze.",
    )
    parser.add_argument(
        "--move",
        action="append",
        dest="moves",
        default=[],
        help="Candidate moves to analyze (UCI format, e.g. e2e4). Can be specified multiple times.",
    )
    parser.add_argument(
        "--audience",
        type=str,
        default="beginner",
        help="Target audience for the explanation (default: beginner).",
    )
    return parser.parse_args()


def main():
    """Main entry point for the analyze command."""
    args = parse_args()

    # Initialize Container
    container = Container()

    try:
        # Resolve Use Case
        use_case = container.get_analyze_position_use_case()

        # specific moves or analyze best?
        # The use case seems to take a list of moves to consider.
        # If no moves are provided, we might want to let the engine find best moves?
        # The current use case implementation:
        # "2. Validate Moves ... if not valid_moves: return Error"
        # So we MUST provide moves currently.
        # (A future improvement could be to generate candidate moves if none provided)

        if not args.moves:
            # Just for safety, we could error out or pass empty list which will error in use case
            pass

        # Create Request
        request = AnalysisRequest(
            fen=args.fen, moves=args.moves, target_audience=args.audience
        )

        # Execute
        response = use_case.execute(request)

        # Format and Print
        json_output = JsonFormatter.format(response)
        print(json_output)

    except (OSError, ValueError, RuntimeError) as e:
        # Fallback error handling usually shouldn't happen if use case handles exceptions,
        # but for safety:
        error_response = {"success": False, "error": f"Critical CLI error: {str(e)}"}
        print(JsonFormatter.format(error_response))

    finally:
        container.close()


if __name__ == "__main__":
    main()
