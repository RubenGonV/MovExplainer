"""
Analyzes a chess position and provides a move explanation and analysis.

This endpoint receives a FEN, an optional list of moves, and a target audience.
It uses the registered use case via Dependency Injection (DI) to process the request,
generate an explanation, and return analysis details like the best move and score.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from presentation.api.schemas import AnalysisRequestModel, AnalysisResponseModel
from container import Container
from application.dto.analysis_request import AnalysisRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MovExplainer API", description="Chess Move Explainer API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path(__file__).parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    return FileResponse(str(static_path / "index.html"))


def get_container():
    """Returns the dependency injection container instance."""
    return Container()


@app.post("/explain", response_model=AnalysisResponseModel)
async def explain_position(
    request: AnalysisRequestModel, container: Container = Depends(get_container)
):
    """Analyzes a chess position and provides a move explanation and analysis."""

    logger.info("Received explanation request for FEN: %s", request.fen)

    try:
        # Map Pydantic model to Domain DTO
        dto = AnalysisRequest(
            fen=request.fen,
            moves=request.moves,
            target_audience=request.target_audience,
        )

        # Get Use Case from Container
        use_case = container.get_analyze_position_use_case()

        # Execute Use Case
        result = use_case.execute(dto)

        # Map Domain Result to Pydantic Response
        response = AnalysisResponseModel(
            success=result.success,
            explanation=result.explanation,
            error=result.error,
            best_move=result.best_move,
            score=result.score,
        )

        if not result.success:
            logger.warning("Analysis failed: %s", result.error)
            # We return the response with success=False,
            # but if it was a system error we might define status codes.
            # For now, following the generic response structure.

        return response

    except (ValueError, RuntimeError, ConnectionError) as e:
        logger.error("Error processing request: %s", str(e), exc_info=True)
        # Return error response with appropriate error message
        return AnalysisResponseModel(success=False, error=f"Analysis error: {str(e)}")
