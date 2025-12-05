import chess
import chess.engine
import sys

import os

# Construir ruta absoluta al engine basada en la ubicación de este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENGINE_REL_PATH = os.path.join("infrastructure", "engines", "stockfish-windows-x86-64-avx2", "stockfish", "stockfish-windows-x86-64-avx2.exe")
ENGINE_PATH = os.path.join(BASE_DIR, ENGINE_REL_PATH)


def evaluate_position(fen, candidate_moves, depth=12):
    # 1. Intentar cargar tablero
    try:
        board = chess.Board(fen)
    except ValueError:
        raise ValueError("❌ El FEN es inválido")


    # 2. Verificar existencia del engine
    if not os.path.isfile(ENGINE_PATH):
        raise FileNotFoundError(
            f"❌ No se encontró el motor de ajedrez en: {ENGINE_PATH}\n"
            "   Asegúrate de que el archivo existe y la ruta es correcta."
        )

    # 3. Arrancar engine
    try:
        engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
    except Exception as e:
        print(f"❌ Error al iniciar el motor: {e}")
        return None

    results = {}

    for move in candidate_moves:
        try:
            uci_move = chess.Move.from_uci(move)
        except ValueError:
            print(f"⚠️ Movimiento '{move}' inválido, saltando.")
            continue

        if uci_move not in board.legal_moves:
            print(f"⚠️ Movimiento ilegal: {move}, ignorado.")
            continue

        new_board = board.copy()
        new_board.push(uci_move)

        info = engine.analyse(new_board, chess.engine.Limit(depth=depth))

        score = info["score"].pov(board.turn)  # orientado al jugador actual
        pv = info.get("pv", [])[:5]  # usa get para no fallar

        # Generar SAN para la línea principal (PV) simulando los movimientos
        pv_san = []
        temp_board = new_board.copy()
        for next_move in pv:
            pv_san.append(temp_board.san(next_move))
            temp_board.push(next_move)

        results[move] = {
            "cp": score.score(mate_score=100000) if score.is_mate() is False else None,
            "mate": score.mate(),
            "pv_moves": pv_san,
        }

    engine.quit()
    return results


if __name__ == "__main__":
    # Ejemplo de prueba rápida
    fen = "r1bqkbnr/pppppppp/n7/8/8/N7/PPPPPPPP/R1BQKBNR w KQkq - 0 1"
    candidate_moves = ["b1c3", "a3b5"]

    print("🧠 Evaluando movimientos...\n")
    
    results = evaluate_position(fen, candidate_moves)

    for move, data in results.items():
        if data["mate"] is not None:
            eval_str = f"Mate en {data['mate']}"
        else:
            eval_str = f"{data['cp']} centipawns"

        print(f"\n➡️ Movimiento {move}")
        print(f"   Evaluación: {eval_str}")
        print(f"   Línea principal: {' → '.join(data['pv_moves'])}")
