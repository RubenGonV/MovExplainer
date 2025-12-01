import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci("engine/stockfish-windows-x86-64-avx2/stockfish/stockfish-windows-x86-64-avx2.exe")
board = chess.Board()  # posición inicial
info = engine.analyse(board, chess.engine.Limit(depth=10))
print(info["score"])
engine.quit()
