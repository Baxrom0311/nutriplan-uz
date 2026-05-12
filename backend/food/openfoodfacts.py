import requests
from django.conf import settings
from .models import FoodItem, FoodCategory

class OpenFoodFactsClient:
    BASE_URL = "https://world.openfoodfacts.org/api/v2"
    
    def search_product(self, query: str) -> list:
        url = f"https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 20
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("products", [])
        except requests.RequestException:
            pass
        return []

    def get_by_barcode(self, barcode: str) -> dict | None:
        url = f"{self.BASE_URL}/product/{barcode}.json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    return data.get("product")
        except requests.RequestException:
            pass
        return None

    def parse_product(self, product_data: dict) -> dict:
        nutriments = product_data.get('nutriments', {})
        
        # O'zbek tiliga tarjima qilingan ism yoki default
        name = product_data.get('product_name', 'Unknown Product')
        brand = product_data.get('brands', '')
        
        # 100g dagi ozuqaviy qiymatlar
        calories = nutriments.get('energy-kcal_100g', 0)
        protein = nutriments.get('proteins_100g', 0)
        fat = nutriments.get('fat_100g', 0)
        carbs = nutriments.get('carbohydrates_100g', 0)
        fiber = nutriments.get('fiber_100g', 0)
        sugar = nutriments.get('sugars_100g', 0)
        sodium = nutriments.get('sodium_100g', 0)
        
        return {
            'name': name,
            'barcode': product_data.get('code'),
            'brand': brand,
            'calories_per_100g': calories,
            'protein_per_100g': protein,
            'fat_per_100g': fat,
            'carbs_per_100g': carbs,
            'fiber_per_100g': fiber,
            'sugar_per_100g': sugar,
            'sodium_per_100g': sodium,
            'image_url': product_data.get('image_url'),
            'source': 'openfoodfacts'
        }

    def import_to_db(self, barcode: str, user=None) -> FoodItem | None:
        # Check if already exists
        existing = FoodItem.objects.filter(barcode=barcode).first()
        if existing:
            return existing
            
        product_data = self.get_by_barcode(barcode)
        if not product_data:
            return None
            
        parsed_data = self.parse_product(product_data)
        
        if parsed_data.get('calories_per_100g') == 0 and parsed_data.get('protein_per_100g') == 0:
            return None # Skip empty nutritional info
            
        # Get or create 'Imported' category
        category, _ = FoodCategory.objects.get_or_create(
            name='Imported via API',
            defaults={'name_uz': 'API orqali import qilingan'}
        )
        
        item = FoodItem(
            category=category,
            name=parsed_data['name'],
            barcode=parsed_data['barcode'],
            brand=parsed_data['brand'],
            calories_per_100g=parsed_data['calories_per_100g'],
            protein_per_100g=parsed_data['protein_per_100g'],
            fat_per_100g=parsed_data['fat_per_100g'],
            carbs_per_100g=parsed_data['carbs_per_100g'],
            fiber_per_100g=parsed_data['fiber_per_100g'],
            sugar_per_100g=parsed_data['sugar_per_100g'],
            sodium_per_100g=parsed_data['sodium_per_100g'],
            image_url=parsed_data['image_url'],
            source=parsed_data['source'],
            is_verified=False,
            created_by=user
        )
        item.save()
        return item
