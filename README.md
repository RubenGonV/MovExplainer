# MovExplainer ♟️

> Un sistema inteligente que analiza y explica movimientos de ajedrez utilizando el motor Stockfish y procesamiento de lenguaje natural.

## 📋 Descripción

**MovExplainer** es una herramienta de análisis de ajedrez que combina la potencia del motor de ajedrez Stockfish con capacidades de procesamiento de lenguaje natural. El proyecto permite evaluar posiciones de ajedrez, comparar movimientos candidatos y obtener análisis detallados de cada jugada.

### Características principales

- 🎯 **Análisis de posiciones**: Evalúa posiciones de ajedrez desde notación FEN
- 🔍 **Comparación de movimientos**: Analiza múltiples movimientos candidatos simultáneamente
- 📊 **Evaluación detallada**: Proporciona evaluaciones en centipeones y detección de mate
- 🧠 **Líneas principales**: Muestra las mejores continuaciones (PV) para cada movimiento
- ✅ **Validación de movimientos**: Verifica la legalidad de los movimientos propuestos
- 🧪 **Suite de pruebas**: Incluye tests automatizados con pytest

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- Windows (el motor Stockfish incluido es para Windows x86-64 AVX2)

### Pasos de instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd MovExplainer
   ```

2. **Crear un entorno virtual** (recomendado)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Dependencias

El proyecto utiliza las siguientes bibliotecas principales:

- `chess==1.11.2` - Biblioteca para manipulación de tableros y movimientos de ajedrez
- `fastapi==0.122.0` - Framework web para crear APIs (preparado para futuras expansiones)
- `pydantic==2.10.6` - Validación de datos
- `pytest` - Framework de testing

## 💻 Uso

### Uso básico

Ejecuta el script de análisis directamente:

```bash
python analysis.py
```

Este comando ejecutará el ejemplo incluido que analiza una posición específica.

### Uso programático

Puedes importar y usar la función `evaluate_position` en tus propios scripts:

```python
from analysis import evaluate_position

# Definir posición FEN
fen = "r1bqkbnr/pppppppp/n7/8/8/N7/PPPPPPPP/R1BQKBNR w KQkq - 0 1"

# Movimientos candidatos en notación UCI
candidate_moves = ["b1c3", "a3b5"]

# Evaluar posición
results = evaluate_position(fen, candidate_moves, depth=12)

# Procesar resultados
for move, data in results.items():
    if data["mate"] is not None:
        print(f"Movimiento {move}: Mate en {data['mate']}")
    else:
        print(f"Movimiento {move}: {data['cp']} centipeones")
    print(f"Línea principal: {' → '.join(data['pv_moves'])}")
```

### Parámetros de `evaluate_position`

- **`fen`** (str): Posición del tablero en notación FEN
- **`candidate_moves`** (list): Lista de movimientos en notación UCI (ej: "e2e4")
- **`depth`** (int, opcional): Profundidad de análisis del motor (default: 12)

### Formato de respuesta

La función retorna un diccionario con la siguiente estructura:

```python
{
    "e2e4": {
        "cp": 25,              # Evaluación en centipeones (None si es mate)
        "mate": None,          # Número de movimientos hasta mate (None si no hay mate)
        "pv_moves": ["e4", "e5", "Nf3", "Nc6", "Bc4"]  # Línea principal en notación SAN
    }
}
```

## 🧪 Testing

El proyecto incluye una suite de pruebas automatizadas usando pytest.

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar un test específico

```bash
pytest tests/test_mate.py
```

### Tests disponibles

- **`test_mate.py`**: Verifica la detección correcta de posiciones de mate
- **`test_ollama.py`**: Tests relacionados con integración de LLM (en desarrollo)

## 📁 Estructura del proyecto

```
MovExplainer/
├── analysis.py           # Módulo principal de análisis de posiciones
├── mvp.py               # Script de prueba mínimo viable
├── requirements.txt     # Dependencias del proyecto
├── README.md           # Este archivo
├── engine/             # Motor de ajedrez Stockfish
│   └── stockfish-windows-x86-64-avx2/
├── tests/              # Suite de pruebas
│   ├── test_mate.py
│   └── test_ollama.py
├── backend/            # Backend API (en desarrollo)
├── frontend/           # Frontend web (en desarrollo)
└── .venv/             # Entorno virtual (no incluido en git)
```

## 🔧 Configuración del motor

El proyecto utiliza **Stockfish** como motor de análisis. La ruta al ejecutable se configura automáticamente en `analysis.py`:

```python
ENGINE_PATH = os.path.join(BASE_DIR, "engine", "stockfish-windows-x86-64-avx2", 
                          "stockfish", "stockfish-windows-x86-64-avx2.exe")
```

Si deseas usar una versión diferente de Stockfish o estás en otro sistema operativo, modifica esta ruta según corresponda.

## 🛠️ Desarrollo

### Próximas características

- [ ] API REST con FastAPI para acceso remoto
- [ ] Interfaz web interactiva
- [ ] Integración con LLM para explicaciones en lenguaje natural
- [ ] Soporte para múltiples motores de ajedrez
- [ ] Análisis de partidas completas (PGN)
- [ ] Visualización gráfica de evaluaciones

### Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Notas técnicas

### Notación FEN

FEN (Forsyth-Edwards Notation) es un estándar para describir posiciones de ajedrez. Ejemplo:

```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

### Notación UCI

UCI (Universal Chess Interface) es el formato estándar para movimientos. Ejemplos:
- `e2e4` - Peón de e2 a e4
- `e7e8q` - Peón de e7 a e8 promocionando a dama

### Notación SAN

SAN (Standard Algebraic Notation) es la notación legible para humanos. Ejemplos:
- `e4` - Peón a e4
- `Nf3` - Caballo a f3
- `O-O` - Enroque corto

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia que especifiques.

## 👤 Autor

Rubén González Velasco

---

**¿Preguntas o sugerencias?** No dudes en abrir un issue o contactar al autor.