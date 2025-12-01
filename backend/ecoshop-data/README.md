# EcoShop - Módulo de Datos

Calculadora de impacto ambiental para productos sostenibles.

## Instalación
# Clonar repositorio
git clone [URL_DEL_REPO]
cd ecoshop-data

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
cp .env.example .env
# Editar .env y agregar tu API key de Climatiq
```

## API Key (Opcional)

Este módulo puede funcionar CON o SIN API de Climatiq:

- **CON API:** Usa datos reales de Climatiq (más preciso)
- **SIN API:** Usa fórmulas aproximadas (suficiente para prototipo)

Para obtener API key gratuita: https://www.climatiq.io/

## Uso desde el backend
```python
from data_module.impact_calculator import calcular_impacto_producto

producto = {
    "id": 1,
    "product": "SilkBalance Emulsion",
    "packaging_material": "plastic_bottle",
    "weight": 150,
    "base_type": "water_based",
    "origin_country": "ARG",
    "transportation_type": "sea",
    "recyclable_packaging": True,
    "ingredient_main": "Green Tea"
}

resultado = calcular_impacto_producto(producto)

print(resultado['huella_total'])  # 0.599
print(resultado['eco_badge'])     #  Bajo impacto
```

## Estructura
```
ecoshop-data/
├── data/                    # Datos
│   └── products.csv
├── data_module/             # Código principal
│   ├── __init__.py
│   └── impact_calculator.py
├── notebooks/               # Análisis exploratorio
├── .env.example             # Template de variables
└── requirements.txt         # Dependencias
```

## Testing
```bash
python data_module/impact_calculator.py
```

Esto procesa `data/products.csv` y genera `data/products_with_impact.csv`.
