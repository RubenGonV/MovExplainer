# MovExplainer ♟️

> Un sistema inteligente que analiza y explica movimientos de ajedrez utilizando el motor Stockfish y procesamiento de lenguaje natural (LLM) con Ollama.

## 📋 Descripción

**MovExplainer** es una herramienta de análisis de ajedrez diseñada con **Clean Architecture** que combina la potencia de cálculo de **Stockfish** con capacidades de explicación de **LLM (Ollama)**. El sistema evalúa posiciones, valida movimientos y genera explicaciones en lenguaje natural comprensibles para diferentes niveles de audiencia (`principiante`, `intermedio`, `experto`).

>- 📊 **[Ver progreso del proyecto](PROGRESS.md)** - Rastrea características completadas, en desarrollo y planificadas.
>- 👉 **[Ver documentación generada por IA (DeepWiki)](https://deepwiki.com/RubenGonV/MovExplainer)**

## ⚙️ Características Destacadas

* **Análisis Profundo de Posiciones**: Evaluación precisa de cualquier posición de ajedrez (formato **FEN**) utilizando el motor de análisis **Stockfish**.
* **Explicaciones Narrativas Asistidas por IA**: Generación de comentarios y justificaciones detalladas sobre los movimientos, impulsadas por modelos de lenguaje locales (**Ollama/Mistral**).
* **Comparación y Evaluación de Candidatos**: Herramientas para examinar y confrontar el impacto de múltiples movimientos alternativos.
* **Validación Integral del Ajedrez**: Verificación estricta de la legalidad de los movimientos propuestos y del cumplimiento del formato **FEN**.


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

## 💻 Uso

MovExplainer ofrece tres formas de interacción: CLI, REST API y Web UI.

### 🌐 Web UI (Recomendado)

La forma más visual e intuitiva de usar MovExplainer.

1. **Iniciar el servidor**:
   ```bash
   # Activar entorno virtual
   .venv\Scripts\activate
   
   # Iniciar servidor FastAPI
   python -m uvicorn presentation.api.main:app --reload
   ```

2. **Abrir en el navegador**:
   ```
   http://localhost:8000
   ```

### 🔌 REST API

Integra MovExplainer en tus propias aplicaciones.

**Endpoint principal**: `POST /api/v1/analyze`

**Ejemplo con curl**:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    "moves": ["e7e5"],
    "audience": "intermediate"
  }'
```

**Respuesta (JSON)**:
```json
{
  "success": true,
  "explanation": "Move: e7e5\n\n1. Accomplishment: This move advances the pawn...",
  "error": null,
  "best_move": "e7e5",
  "score": -34
}
```

**Documentación interactiva**: Una vez iniciado el servidor, visita:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 🖥️ CLI (Línea de Comandos)

Para uso en scripts o automatización.

```bash
# Activar entorno virtual si no lo está
.venv\Scripts\activate

# Ejecutar análisis
python presentation/cli/commands/analyze_command.py --fen "FEN_STRING" --move "e2e4" --audience "beginner"
```

**Ejemplo**:
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
│   ├── use_cases/         # Casos de uso (ej. AnalyzePosition)
│   └── dto/               # Objetos de transferencia de datos
├── domain/             # Entidades y reglas de negocio
├── infrastructure/     # Implementaciones externas
│   ├── engines/           # Stockfish
│   ├── llm/               # Ollama
│   └── validators/        # Chess validator
├── presentation/       # Entry points
│   ├── api/               # REST API (FastAPI)
│   ├── cli/               # Comandos de consola
│   └── web/               # Interfaz web (HTML/CSS/JS)
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
