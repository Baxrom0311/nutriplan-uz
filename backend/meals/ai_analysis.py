import base64
import json
import mimetypes
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from django.conf import settings


class FoodVisionServiceNotConfigured(Exception):
    pass


class FoodVisionAnalysisError(Exception):
    pass


@dataclass(frozen=True)
class FoodVisionResult:
    food_name: str
    estimated_weight_g: Decimal
    calories: Decimal
    protein: Decimal
    carbs: Decimal
    fat: Decimal
    confidence: Decimal
    notes_uz: str
    raw: dict[str, Any]


def _decimal(value: Any, default: str = '0') -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        parsed = Decimal(default)
    return max(parsed, Decimal('0'))


def _image_to_data_url(image_file) -> str:
    name = getattr(image_file, 'name', 'meal-photo.jpg')
    mime_type = mimetypes.guess_type(name)[0] or 'image/jpeg'

    if hasattr(image_file, 'open'):
        image_file.open('rb')

    content = image_file.read()

    if hasattr(image_file, 'seek'):
        image_file.seek(0)

    encoded = base64.b64encode(content).decode('ascii')
    return f'data:{mime_type};base64,{encoded}'


def _extract_json(content: str) -> dict[str, Any]:
    normalized = content.strip()
    if normalized.startswith('```'):
        normalized = re.sub(r'^```(?:json)?\s*', '', normalized)
        normalized = re.sub(r'\s*```$', '', normalized)

    try:
        return json.loads(normalized)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', normalized, flags=re.DOTALL)
        if not match:
            raise FoodVisionAnalysisError('AI javobidan JSON natija ajratib olinmadi.')
        return json.loads(match.group(0))


def _analyze_with_gemini(image_file, prompt: str, api_key: str, model: str) -> str:
    """Gemini API orqali rasm tahlili"""
    if hasattr(image_file, 'open'):
        image_file.open('rb')
    content = image_file.read()
    if hasattr(image_file, 'seek'):
        image_file.seek(0)
    
    encoded = base64.b64encode(content).decode('ascii')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    response = requests.post(
        url,
        headers={'Content-Type': 'application/json'},
        json={
            'contents': [{
                'parts': [
                    {'text': prompt},
                    {'inline_data': {'mime_type': 'image/jpeg', 'data': encoded}}
                ]
            }],
            'generationConfig': {
                'temperature': 0.2,
                'maxOutputTokens': 1024,
            }
        },
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text']


def _analyze_with_openai(image_file, prompt: str, api_key: str, model: str, api_url: str) -> str:
    """OpenAI-compatible API orqali rasm tahlili"""
    data_url = _image_to_data_url(image_file)
    
    response = requests.post(
        api_url,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        },
        json={
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Sen oziq-ovqat rasmlarini tahlil qiluvchi nutrition AI modulisan. Javobni faqat JSON formatida qaytar, markdown ishlatma.',
                },
                {
                    'role': 'user',
                    'content': [
                        {'type': 'text', 'text': prompt},
                        {'type': 'image_url', 'image_url': {'url': data_url}},
                    ],
                },
            ],
            'temperature': 0.2,
            'max_tokens': 1024,
        },
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    return data['choices'][0]['message']['content']


def analyze_meal_photo(image_file, user_context: str) -> FoodVisionResult:
    api_key = getattr(settings, 'FOOD_VISION_API_KEY', '')
    if not api_key:
        raise FoodVisionServiceNotConfigured('Rasmni tahlil qilish uchun FOOD_VISION_API_KEY sozlanmagan.')

    model = getattr(settings, 'FOOD_VISION_MODEL', 'gemini-2.0-flash-exp')
    provider = getattr(settings, 'FOOD_VISION_PROVIDER', 'gemini')
    
    prompt = f"""Sen professional nutrition AI. Rasmda ko'rinayotgan ovqatni aniq tahlil qil.

Foydalanuvchi konteksti:
{user_context}

O'zbek milliy taomlari (osh, lag'mon, manti, shashlik, somsa, non) va xalqaro taomlarni yaxshi bil.
Porsiya hajmini diqqat bilan baholab, kaloriya va makronutrientlarni aniq hisoblang.

Faqat JSON formatida javob ber (markdown yoki qo'shimcha matn yo'q):
{{
  "food_name": "aniq ovqat nomi (o'zbek tilida)",
  "estimated_weight_g": 350,
  "calories": 735,
  "protein": 28,
  "carbs": 87,
  "fat": 31,
  "confidence": 0.85,
  "notes_uz": "qisqa tavsif va tarkib haqida izoh"
}}

Agar rasmda ovqat aniq ko'rinmasa, eng ehtiyotkor taxminni ber va confidence ni pastroq qo'y.
Barcha raqamlar musbat bo'lishi kerak."""

    try:
        if provider == 'gemini':
            content = _analyze_with_gemini(image_file, prompt, api_key, model)
        else:
            api_url = getattr(settings, 'FOOD_VISION_API_URL', 'https://api.openai.com/v1/chat/completions')
            content = _analyze_with_openai(image_file, prompt, api_key, model, api_url)
        
        parsed = _extract_json(content)
        
    except requests.exceptions.Timeout as exc:
        raise FoodVisionAnalysisError('Rasmni tahlil qilish xizmati javob bermadi.') from exc
    except requests.exceptions.RequestException as exc:
        raise FoodVisionAnalysisError(f'Rasmni tahlil qilish xizmati xatosi: {exc}') from exc

    food_name = str(parsed.get('food_name') or 'Aniqlangan ovqat').strip()[:200]
    weight = _decimal(parsed.get('estimated_weight_g'), '100') or Decimal('100')

    return FoodVisionResult(
        food_name=food_name,
        estimated_weight_g=weight,
        calories=_decimal(parsed.get('calories')),
        protein=_decimal(parsed.get('protein')),
        carbs=_decimal(parsed.get('carbs')),
        fat=_decimal(parsed.get('fat')),
        confidence=min(_decimal(parsed.get('confidence'), '0'), Decimal('1')),
        notes_uz=str(parsed.get('notes_uz') or '').strip(),
        raw=parsed,
    )
