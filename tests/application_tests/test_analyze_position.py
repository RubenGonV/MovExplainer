import unittest
from unittest.mock import Mock
from domain.entities.evaluation import Evaluation
from application.dto.analysis_request import AnalysisRequest
from application.use_cases.analyze_position import AnalyzePosition


class TestAnalyzePosition(unittest.TestCase):
    def setUp(self):
        self.mock_engine = Mock()
        self.mock_llm = Mock()
        self.mock_validator = Mock()
        self.use_case = AnalyzePosition(
            engine_service=self.mock_engine,
            llm_service=self.mock_llm,
            validator=self.mock_validator,
        )

    def test_execute_success(self):
        # Setup
        fen = "start_fen"
        moves = ["e2e4"]
        request = AnalysisRequest(fen=fen, moves=moves)

        # Mocks
        self.mock_validator.validate_fen.return_value = True
        self.mock_validator.sanitize_move.return_value = "e2e4"
        self.mock_validator.validate_move.return_value = True

        from domain.value_objects.score import Score

        # Mocking Evaluation requires matching the signature: score, depth, pv
        # Assuming Score(cp, mate)

        eval_current = Evaluation(score=Score(cp=10, mate=None), depth=10, pv=[])
        eval_move = Evaluation(score=Score(cp=20, mate=None), depth=10, pv=[])

        self.mock_engine.evaluate.return_value = eval_current
        self.mock_engine.analyze_moves.return_value = {"e2e4": eval_move}
        self.mock_llm.explain.return_value = "Good move!"

        # Execute
        response = self.use_case.execute(request)

        # Assert
        self.assertTrue(response.success)
        self.assertEqual(response.explanation, "Good move!")
        self.assertEqual(response.best_move, "e2e4")
        self.assertEqual(response.score, 20)

        self.mock_validator.validate_fen.assert_called_with(fen)
        self.mock_engine.evaluate.assert_called_with(fen)
        self.mock_engine.analyze_moves.assert_called_with(fen, ["e2e4"])
        self.mock_llm.explain.assert_called()

    def test_invalid_fen(self):
        self.mock_validator.validate_fen.return_value = False
        request = AnalysisRequest(fen="bad", moves=[])

        response = self.use_case.execute(request)

        self.assertFalse(response.success)
        self.assertEqual(response.error, "Invalid FEN string")

    def test_no_valid_moves(self):
        self.mock_validator.validate_fen.return_value = True
        self.mock_validator.sanitize_move.return_value = "bad_move"
        self.mock_validator.validate_move.return_value = False  # Move is invalid

        request = AnalysisRequest(fen="start", moves=["bad_move"])

        response = self.use_case.execute(request)

        self.assertFalse(response.success)
        self.assertEqual(response.error, "No valid moves provided")


if __name__ == "__main__":
    unittest.main()
