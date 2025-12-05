import pytest
from domain.entities.move import Move
from domain.entities.position import Position
from domain.value_objects.fen import FEN

@pytest.mark.unit
def test_move_creation():
    move = Move(uci="e2e4", san="e4")
    assert move.uci == "e2e4"
    assert move.san == "e4"
    assert str(move) == "e4"

@pytest.mark.unit
def test_move_creation_uci_only():
    move = Move(uci="e2e4")
    assert move.uci == "e2e4"
    assert move.san is None
    assert str(move) == "e2e4"

@pytest.mark.unit
def test_move_validation():
    with pytest.raises(ValueError):
        Move(uci="") # Empty
    
    with pytest.raises(ValueError):
        Move(uci="e2") # Too short

@pytest.mark.unit
def test_position_is_white_turn():
    fen_white = FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    pos_white = Position(fen=fen_white)
    assert pos_white.is_white_turn() is True

    fen_black = FEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1")
    pos_black = Position(fen=fen_black)
    assert pos_black.is_white_turn() is False
