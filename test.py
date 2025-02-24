from app import create_app, db
from app.services.promotion_service import PromotionService

# Crear la aplicación y el contexto de Flask
app = create_app()

with app.app_context():
    # Prueba de la función con filtros
    filters = {
        "category_id": None,   # No filtrar por categoría
        "start_date": None,   # Filtrar por fecha de inicio
        "expiration_date": None,   # No filtrar por fecha de expiración
        "keyword": "descuento",   # Filtrar por palabra clave
        "user_id": None   # Filtrar por usuario ID
    }

    # Ejecutar la consulta con los filtros definidos
    promotions = PromotionService.get_promotions_by_filter(**filters)

    # Mostrar los resultados
    print("🔍 Promociones filtradas (lista completa):")
    print(promotions)  # Muestra todo el objeto devuelto

    # Mostrar cada promoción individualmente
    if promotions:
        for promo in promotions:
            print(f"% {promo}")
    else:
        print("⚠ No se encontraron promociones con estos filtros. ⚠")
