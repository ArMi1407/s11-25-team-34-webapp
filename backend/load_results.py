"""
CARGA COMPLETA: Usuarios + Marcas + Categorías + Productos
Ejecutar: python backend/load_complete.py
"""
import os, sys, pandas as pd

# 1. Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

# 2. Importar modelos
from django.contrib.auth.models import User
from products.models import Product, Category
from accounts.models import UserProfile, BrandProfile
from django.utils.text import slugify

# 3. Ruta del CSV
CSV_PATH = "ecoshop-data/data/products_with_impact.csv"

# 4. Verificar archivo
if not os.path.exists(CSV_PATH):
    print(f"❌ ERROR: Archivo no encontrado: {CSV_PATH}")
    exit()

# 5. Leer CSV
df = pd.read_csv(CSV_PATH)
print(f"📊 CSV cargado: {len(df)} productos")

# 6. Mapeo de badges
BADGE_MAP = {
    '🌱 Bajo impacto': '🌱 low Impact',
    '🌿 Medio impacto': '🌿 medium Impact', 
    '🌳 Alto impacto': '🌳 high Impact'
}

# 7. Función para obtener/crear marca
def obtener_o_crear_marca(nombre_marca):
    """Crea usuario, perfil y marca si no existe"""
    try:
        return BrandProfile.objects.get(brand_name=nombre_marca)
    except BrandProfile.DoesNotExist:
        print(f"   🆕 Creando marca: {nombre_marca}")
        
        # Crear usuario
        username = f"brand_{nombre_marca.lower().replace(' ', '_')}"
        email = f"{nombre_marca.lower()}@ecoshop.com"
        
        usuario, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_active': True
            }
        )
        if created:
            usuario.set_password("password123")  # Contraseña temporal
            usuario.save()
        
        # Crear perfil de usuario
        user_profile, _ = UserProfile.objects.get_or_create(
            user=usuario,
            defaults={
                'is_brand_manager': True,
                'eco_points': 1000
            }
        )
        
        # Crear perfil de marca
        marca = BrandProfile.objects.create(
            user_profile=user_profile,
            brand_name=nombre_marca,
            sustainability_story=f"Comprometidos con la sostenibilidad desde 2024. {nombre_marca} ofrece productos ecológicos con bajas emisiones de carbono."
        )
        
        return marca

# 8. Cargar productos
creados = 0
errores = 0

for _, fila in df.iterrows():
    try:
        producto_nombre = fila['product']
        
        # Evitar duplicados
        if Product.objects.filter(name=producto_nombre).exists():
            print(f"⏭️  Saltando: {producto_nombre} (ya existe)")
            continue
        
        # Obtener/Crear categoría
        categoria, _ = Category.objects.get_or_create(
            name=fila['category'],
            defaults={'slug': slugify(fila['category'])}
        )
        
        # Obtener/Crear marca
        marca = obtener_o_crear_marca(fila['brand'])
        
        # Crear producto
        Product.objects.create(
            name=producto_nombre,
            slug=slugify(f"{producto_nombre}-{fila['id']}"),
            description=f"{producto_nombre}. Ingrediente principal: {fila['ingredient_main']}. {fila['base_type'].replace('_', ' ').title()}. Packaging: {fila['packaging_material'].replace('_', ' ').title()}. Origen: {fila['origin_country']}. Peso: {fila['weight']}g.",
            brand=marca,
            category=categoria,
            climatiq_category=fila['category_climatiq'],
            price=float(fila['money']),
            stock=100,
            is_active=True,
            ingredient_main=fila['ingredient_main'],
            base_type=fila['base_type'],
            packaging_material=fila['packaging_material'],
            origin_country=fila['origin_country'],
            weight=int(fila['weight']),
            recyclable_packaging=bool(fila['recyclable_packaging']),
            transportation_type=fila['transportation_type'],
            carbon_footprint=float(fila['huella_total']),
            eco_badge=BADGE_MAP.get(fila['eco_badge'], '🌿 medium Impact')
        )
        
        creados += 1
        if creados % 3 == 0:
            print(f"   ✅ {creados} productos creados...")
            
    except Exception as e:
        errores += 1
        print(f"❌ Error en {fila.get('product', '?')}: {str(e)[:100]}")

# 9. Resultados
print("\n" + "="*50)
print("📊 RESULTADOS FINALES")
print("="*50)
print(f"✅ Productos creados: {creados}")
print(f"❌ Errores: {errores}")
print(f"🏷️  Marcas en BD: {BrandProfile.objects.count()}")
print(f"🏷️  Categorías en BD: {Category.objects.count()}")
print(f"📦 Total productos en BD: {Product.objects.count()}")
print("="*50)
print("🔑 Credenciales de marcas creadas:")
print("   Usuario: brand_[nombre_marca]")
print("   Contraseña: password123")
print("   Email: [marca]@ecoshop.com")