"""EcoShop Impact Calculator
Calcula huellas de carbono para productos sostenibles
"""

import os
import requests
import pandas as pd
from dotenv import load_dotenv
from time import sleep
from typing import Optional, Dict

# Cargar variables de entorno
load_dotenv()


class ImpactCalculator:
    """Calculadora de impacto ambiental para productos EcoShop"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa la calculadora

        Args:
            api_key: API key de Climatiq (opcional, se lee de .env si no se pasa)
        """
        self.api_key = api_key or os.getenv("CLIMATIQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "CLIMATIQ_API_KEY no encontrada. "
                "Configura tu archivo .env o pasa api_key como parámetro"
            )

    def calcular_huella_materiales(self, producto: Dict) -> float:
        """
        Calcula huella por packaging e ingredientes

        Args:
            producto: Dict con datos del producto

        Returns:
            float: Score de impacto (0.0 - 1.0+)
        """
        # Impacto por material de packaging
        packaging_impact = {
            "plastic_bottle": 0.3,
            "plastic_tube": 0.3,
            "glass_container": 0.2,
            "paper_wrap": 0.1,
        }

        score_packaging = packaging_impact.get(producto.get("packaging_material"), 0.3)

        # Penalización si no es reciclable
        if not producto.get("recyclable_packaging", True):
            score_packaging += 0.2

        # Impacto por procesamiento de ingrediente
        low_process = [
            "Aloe Vera",
            "Chamomile",
            "Thermal Water",
            "Cucumber",
            "Olive Oil",
            "Coconut Oil",
        ]
        medium_process = [
            "Green Tea",
            "Rice Extract",
            "Oat Extract",
            "Lemon",
            "Lavender Oil",
            "Avocado Butter",
            "Avocado Oil",
            "Shea Butter",
            "Bamboo Extract",
        ]
        high_process = ["Niacinamide", "Vitamin C", "Centella Asiatica"]

        ingredient = producto.get("ingredient_main", "")
        if ingredient in low_process:
            score_ingredients = 0.10
        elif ingredient in medium_process:
            score_ingredients = 0.20
        elif ingredient in high_process:
            score_ingredients = 0.30
        else:
            score_ingredients = 0.20  # default

        return round(score_packaging + score_ingredients, 3)

    def calcular_huella_transporte(self, producto: Dict) -> float:
        """
        Calcula huella por transporte

        Args:
            producto: Dict con datos del producto

        Returns:
            float: kg CO2e estimado
        """
        # Factor de emisión por tipo (kg CO2e por km por kg de producto)
        transport_factor = {"air": 0.0007, "sea": 0.0003, "land": 0.0004}

        # Distancia promedio desde país de origen (km)
        country_distance = {
            "ARG": 200,
            "BRA": 2000,
            "KOR": 18000,
            "CHN": 19000,
            "VNM": 17000,
            "MEX": 8000,
        }

        distance = country_distance.get(producto.get("origin_country"), 5000)
        t_type = producto.get("transportation_type", "sea")

        # Convertir peso a kg
        weight_kg = producto.get("weight", 100) / 1000

        impact = distance * transport_factor.get(t_type, 0.0004) * weight_kg

        return round(impact, 3)

    def calcular_huella_manufactura(
        self, producto: Dict, usar_api: bool = True
    ) -> Optional[float]:
        """
        Calcula CO2e de manufactura usando Climatiq API o fórmula aproximada

        Args:
            producto: Dict con datos del producto
            usar_api: Si True, intenta usar Climatiq API. Si False o falla, usa fórmula aproximada

        Returns:
            float: kg CO2e
        """
        # Si no se quiere usar API o no hay key, usar fórmula aproximada
        if not usar_api or not self.api_key:
            return self._calcular_huella_manufactura_aproximada(producto)

        # Mapear categorías a activity_ids válidos de Climatiq
        category_mapping = {
            "consumer_goods-type_emulsion": "consumer_goods-type_cosmetics_and_toiletries",
            "consumer_goods-type_facial_wash": "consumer_goods-type_cosmetics_and_toiletries",
            "consumer_goods-type_soaps_and_cleaning_compounds": "consumer_goods-type_soaps_and_cleaning_compounds",
        }

        original_category = producto.get("category_climatiq", "")
        activity_id = category_mapping.get(
            original_category, "consumer_goods-type_cosmetics_and_toiletries"
        )

        payload = {
            "emission_factor": {"activity_id": activity_id, "data_version": "^0"},
            "parameters": {},
        }
        print(f"DEBUG - Payload para producto {producto.get('id')}:")
        print(payload)

        # Priorizar parámetros según disponibilidad
        if pd.notna(producto.get("money")):
            payload["parameters"]["money"] = producto["money"]
            payload["parameters"]["money_unit"] = producto.get("money_unit", "USD")
        elif pd.notna(producto.get("weight")):
            payload["parameters"]["weight"] = producto["weight"]
            payload["parameters"]["weight_unit"] = producto.get("weight_unit", "g")
        elif pd.notna(producto.get("volume")):
            payload["parameters"]["volume"] = producto["volume"]
            payload["parameters"]["volume_unit"] = producto.get("volume_unit", "ml")

        try:
            response = requests.post(
                "https://api.climatiq.io/data/v1/estimate",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                return round(data["co2e"], 3)
            else:
                print(
                    f"⚠️  API error {response.status_code} para producto {producto.get('id', 'N/A')} - usando fórmula aproximada"
                )
                return self._calcular_huella_manufactura_aproximada(producto)

        except requests.exceptions.Timeout:
            print(
                f"⚠️  Timeout para producto {producto.get('id', 'N/A')} - usando fórmula aproximada"
            )
            return self._calcular_huella_manufactura_aproximada(producto)
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Error de conexión: {e} - usando fórmula aproximada")
            return self._calcular_huella_manufactura_aproximada(producto)
        except KeyError:
            print(f"⚠️  Respuesta inesperada de API - usando fórmula aproximada")
            return self._calcular_huella_manufactura_aproximada(producto)

    def _calcular_huella_manufactura_aproximada(self, producto: Dict) -> float:
        """
        Calcula huella de manufactura con fórmula aproximada
        Basado en tipo de base y peso del producto

        Args:
            producto: Dict con datos del producto

        Returns:
            float: kg CO2e estimado
        """
        # Factores de emisión aproximados por tipo de base (kg CO2e por kg de producto)
        base_factors = {
            "water_based": 0.5,  # Menor impacto
            "plant_based": 0.8,  # Medio impacto
            "oil_based": 1.2,  # Mayor impacto
        }

        base_type = producto.get("base_type", "water_based")
        factor = base_factors.get(base_type, 0.8)

        # Convertir peso a kg
        weight_kg = producto.get("weight", 100) / 1000

        # Calcular emisión base
        emision_base = weight_kg * factor

        # Ajuste por tipo de packaging (más plástico = más emisiones)
        packaging_adjustment = {
            "plastic_bottle": 1.2,
            "plastic_tube": 1.15,
            "glass_container": 1.1,
            "paper_wrap": 1.0,
        }

        packaging = producto.get("packaging_material", "plastic_bottle")
        ajuste = packaging_adjustment.get(packaging, 1.1)

        emision_total = emision_base * ajuste

        return round(emision_total, 3)

    def calcular_producto_individual(self, producto: Dict) -> Dict:
        """
        Calcula todas las huellas para un solo producto

        Args:
            producto: Dict con datos del producto

        Returns:
            Dict: producto original + huellas calculadas
        """
        resultado = producto.copy()

        resultado["huella_materiales"] = self.calcular_huella_materiales(producto)
        resultado["huella_transporte"] = self.calcular_huella_transporte(producto)
        resultado["huella_manufactura"] = self.calcular_huella_manufactura(producto)

        # Calcular total
        resultado["huella_total"] = (
            resultado["huella_materiales"]
            + resultado["huella_transporte"]
            + (
                resultado["huella_manufactura"]
                if resultado["huella_manufactura"] is not None
                else 0
            )
        )

        # Asignar badge
        resultado["eco_badge"] = self.asignar_eco_badge(resultado["huella_total"])

        return resultado

    def calcular_batch(
        self, df_productos: pd.DataFrame, delay: float = 0.2
    ) -> pd.DataFrame:
        """
        Calcula huellas para un DataFrame completo

        Args:
            df_productos: DataFrame con productos
            delay: Segundos entre requests a API (para evitar rate limiting)

        Returns:
            DataFrame con columnas de huella agregadas
        """
        df = df_productos.copy()

        print("🌱 Calculando huellas de materiales...")
        df["huella_materiales"] = df.apply(
            lambda row: self.calcular_huella_materiales(row.to_dict()), axis=1
        )

        print("🚚 Calculando huellas de transporte...")
        df["huella_transporte"] = df.apply(
            lambda row: self.calcular_huella_transporte(row.to_dict()), axis=1
        )

        print("🏭 Calculando huellas de manufactura (esto puede tardar)...")
        manufactura_list = []
        total = len(df)

        for idx, row in df.iterrows():
            huella = self.calcular_huella_manufactura(row.to_dict())
            manufactura_list.append(huella)

            if (idx + 1) % 5 == 0:
                print(f"   Progreso: {idx + 1}/{total} productos")

            sleep(delay)

        df["huella_manufactura"] = manufactura_list

        print("🧮 Calculando totales...")
        df["huella_total"] = df.apply(
            lambda row: (
                row["huella_materiales"]
                + row["huella_transporte"]
                + (
                    row["huella_manufactura"]
                    if pd.notna(row["huella_manufactura"])
                    else 0
                )
            ),
            axis=1,
        )

        print("🏷️  Asignando eco-badges...")
        df["eco_badge"] = df["huella_total"].apply(self.asignar_eco_badge)

        print("✅ ¡Cálculo completado!")
        return df

    @staticmethod
    def asignar_eco_badge(huella_total: float) -> str:
        """
        Asigna badge según huella total

        Args:
            huella_total: Huella total en kg CO2e

        Returns:
            str: Badge con emoji y nivel
        """
        if huella_total < 0.5:
            return "🌱 Bajo impacto"
        elif huella_total < 1.5:
            return "🌿 Medio impacto"
        else:
            return "🌳 Alto impacto"


# === FUNCIÓN AUXILIAR PARA EL BACKEND ===
def calcular_impacto_producto(
    producto_data: Dict, api_key: Optional[str] = None
) -> Dict:
    """
    Función simplificada para que el backend calcule impacto de un producto

    Args:
        producto_data: Dict con datos del producto
        api_key: API key de Climatiq (opcional)

    Returns:
        Dict con producto + huellas calculadas

    Ejemplo de uso desde el backend:
        from data_module.impact_calculator import calcular_impacto_producto

        producto = {
            "id": 1,
            "product": "SilkBalance Emulsion",
            "packaging_material": "plastic_bottle",
            "weight": 150,
            ...
        }

        resultado = calcular_impacto_producto(producto)
        print(resultado['huella_total'])
    """
    calculator = ImpactCalculator(api_key=api_key)
    return calculator.calcular_producto_individual(producto_data)


# === SCRIPT PRINCIPAL (para testing) ===
if __name__ == "__main__":
    import sys

    # Verificar que existe el archivo de productos
    csv_path = "data/products.csv"
    if not os.path.exists(csv_path):
        print(f"❌ No se encontró {csv_path}")
        print("Asegúrate de tener el CSV en la carpeta 'data/'")
        sys.exit(1)

    # Cargar productos
    print(f"📂 Cargando productos desde {csv_path}...")
    df_products = pd.read_csv(csv_path)
    print(f"   {len(df_products)} productos cargados")

    # Inicializar calculadora
    try:
        calculator = ImpactCalculator()
        print("✅ Calculadora inicializada correctamente")
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Calcular huellas
    df_with_impact = calculator.calcular_batch(df_products)

    # Mostrar resultados
    print("\n" + "=" * 70)
    print("RESUMEN DE IMPACTO AMBIENTAL")
    print("=" * 70)
    print(
        df_with_impact[
            [
                "product",
                "huella_materiales",
                "huella_transporte",
                "huella_manufactura",
                "huella_total",
                "eco_badge",
            ]
        ].to_string()
    )

    # Guardar resultados
    output_path = "data/products_with_impact.csv"
    df_with_impact.to_csv(output_path, index=False)
    print(f"\n💾 Resultados guardados en '{output_path}'")

    # Estadísticas
    print("\n📊 ESTADÍSTICAS:")
    print(f"   Huella promedio: {df_with_impact['huella_total'].mean():.3f} kg CO2e")
    print(f"   Huella mínima: {df_with_impact['huella_total'].min():.3f} kg CO2e")
    print(f"   Huella máxima: {df_with_impact['huella_total'].max():.3f} kg CO2e")
    print("\n🏷️  DISTRIBUCIÓN DE BADGES:")
    print(df_with_impact["eco_badge"].value_counts())
