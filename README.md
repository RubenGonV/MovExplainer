# MovExplainer ♟️

> Un sistema inteligente que analiza y explica movimientos de ajedrez utilizando el motor Stockfish y procesamiento de lenguaje natural (LLM) con Ollama.

## 📋 Descripción

**MovExplainer** es una herramienta de análisis de ajedrez diseñada con **Clean Architecture** que combina la potencia de cálculo de **Stockfish** con capacidades de explicación de **LLM (Ollama)**. El sistema evalúa posiciones, valida movimientos y genera explicaciones en lenguaje natural comprensibles para diferentes niveles de audiencia (principiante, intermedio, experto).

### Características principales

- 🏗️ **Clean Architecture**: Código modular y desacoplado (Domain, Application, Infrastructure, Presentation).
- 🎯 **Análisis de posiciones**: Evalúa posiciones FEN utilizando Stockfish.
- 🤖 **Explicaciones con IA**: Genera explicaciones narrativas de los movimientos usando modelos locales (Ollama/Mistral).
- 🔍 **Comparación de movimientos**: Analiza y compara múltiples candidatos.
- ✅ **Validación robusta**: Verifica legalidad de movimientos y formatos FEN.
- 🖥️ **CLI Potente**: Interfaz de línea de comandos fácil de usar con salida JSON.
- 🧪 **Testing Integrado**: Suite completa de tests unitarios y de integración.

## 🚀 Instalación

### Requisitos previos

- Python 3.10 o superior
- [Ollama](https://ollama.ai/) instalado y ejecutándose (con el modelo `mistral` descargado: `ollama pull mistral`)
- Windows (el binario de Stockfish incluido es para Windows x86-64 AVX2)

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd MovExplainer
   ```

2. **Crear uns entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Dependencias

- `python-chess`: Manipulación de tablero y reglas.
- `ollama`: Cliente para interactuar con el LLM local.
- `pydantic`: Validación de datos y DTOs.
- `pytest`: Framework de testing.

## 💻 Uso

### CLI (Línea de Comandos)

La forma principal de interactuar con MovExplainer es a través de su CLI.

```bash
# Activar entorno virtual si no lo está
.venv\Scripts\activate

# Ejecutar análisis
python presentation/cli/commands/analyze_command.py --fen "FEN_STRING" --move "e2e4" --audience "beginner"
```

### Ejemplo

**Comanado:**
```bash
python presentation/cli/commands/analyze_command.py --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1" --move "e7e5" --audience "intermediate"
```

**Salida (JSON):**
```json
{
  "success": true,
  "explanation": "Move: e7e5\n\n1. Accomplishment: This move advances the pawn...",
  "error": null,
  "best_move": "e7e5",
  "score": -34
}
```

### Argumentos

- `--fen`: (Requerido) La cadena FEN de la posición.
- `--move`: (Opcional, múltiple) Movimiento candidato en formato UCI (ej. `e2e4`). Se puede repetir para analizar varios: `--move e2e4 --move d2d4`.
- `--audience`: (Opcional) Nivel de la audiencia: `beginner`, `intermediate`, `expert`. Default: `beginner`.

## 📁 Estructura del Proyecto

El proyecto sigue los principios de Clean Architecture:

```
MovExplainer/
├── application/        # Casos de uso y DTOs
│   ├── use_cases/      # Lógica de negocio (ej. AnalyzePosition)
│   └── dto/            # Objetos de transferencia de datos
├── domain/             # Entidades y reglas de negocio
├── infrastructure/     # Implementaciones externas
│   ├── engines/        # Stockfish
│   ├── llm/            # Ollama
│   └── validators/     # Chess validator
├── presentation/       # Entry points
│   └── cli/            # Comandos de consola
├── tests/              # Tests automatizados
├── container.py        # Inyección de dependencias
└── requirements.txt
```

## 🔧 Configuración

- **Stockfish**: El binario está incluido en `infrastructure/engines/`. El contenedor de inyección de dependencias lo localiza automáticamente.
- **Ollama**: Se conecta por defecto a `localhost:11434`. Puedes configurar el modelo con la variable de entorno `OLLAMA_MODEL` (default: `mistral`).

## 🧪 Testing

Para ejecutar la suite de pruebas:

```bash
pytest
```

## 👤 Autor

Rubén González Velasco

---

**MovExplainer** - Potenciando el aprendizaje de ajedrez con IA.