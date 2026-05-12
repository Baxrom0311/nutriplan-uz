import requests
from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from meals.models import Meal, MealImageAnalysis, WaterLog, WeightLog


DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

SYSTEM_PROMPT = """Sen NutriPlan UZ — O'zbekiston uchun sog'lom ovqatlanish bo'yicha AI maslahatchi.

Sening vazifalaring:
- Foydalanuvchining ovqatlanish ma'lumotlariga asoslangan shaxsiy maslahatlar berish
- Kaloriya, oqsil, uglevod va yog' bo'yicha tavsiyalar
- O'zbek taomlari haqida bilim (osh, so'msa, lag'mon, shashlik, non va h.k.)
- Vazn yo'qotish, saqlash yoki olish uchun amaliy maslahatlar
- Suv ichish rejimi bo'yicha eslatmalar

Qoidalar:
- Har doim o'zbek tilida javob ber
- Qisqa va aniq javob ber
- Foydalanuvchining maqsadiga mos maslahat ber
- Ilmiy asoslangan ma'lumotlar ber
- Doktor emas ekanligingni eslatib tur, jiddiy holatlarda shifokorga murojaat qilishni maslahat ber
- Jins, bo'y, vazn, yosh, maqsad, bugungi ovqatlar, suv va vazn tarixi kontekstda berilgan bo'lsa, ularni qayta so'rama
- Avval kontekstdagi real raqamlarga tayangan holda tahlil qil
- Faqat ma'lumot bazada yo'q bo'lsa, aynan yetishmayotgan bitta-ikkita ma'lumotni so'ra
"""


def get_user_context(user):
    """Foydalanuvchining ovqatlanish ma'lumotlarini yig'ish"""
    profile = getattr(user, 'profile', None)
    today = timezone.now().date()

    # Bugungi ovqatlar
    meals = Meal.objects.filter(user=user, date=today).prefetch_related('items__food_item')
    consumed_cals = float(sum(m.total_calories for m in meals))
    consumed_protein = float(sum(m.total_protein for m in meals))
    consumed_carbs = float(sum(m.total_carbs for m in meals))
    consumed_fat = float(sum(m.total_fat for m in meals))

    meal_details = []
    for meal in meals:
        items = [f"{item.food_item.name} ({item.weight_g}g)" for item in meal.items.all()]
        if items:
            meal_details.append(f"{meal.get_meal_type_display()}: {', '.join(items)}")

    # Bugungi suv
    water = sum(w.amount_ml for w in WaterLog.objects.filter(user=user, date=today))

    # Oxirgi vazn
    last_weight = WeightLog.objects.filter(user=user).order_by('-date').first()
    recent_weights = list(WeightLog.objects.filter(user=user).order_by('-date')[:7])
    recent_weights.reverse()

    photo_analyses = MealImageAnalysis.objects.filter(
        user=user,
        date=today,
        status='processed',
    ).select_related('meal_item').order_by('created_at')

    photo_details = [
        (
            f"{item.get_meal_type_display()}: {item.detected_food_name} "
            f"({item.estimated_weight_g}g, {item.estimated_calories} kkal)"
        )
        for item in photo_analyses
    ]

    weight_history = [
        f"{item.date}: {item.weight_kg} kg"
        for item in recent_weights
    ]
    daily_calorie_goal = profile.daily_calorie_goal if profile and profile.daily_calorie_goal else 2000
    protein_goal = float(profile.protein_goal_g) if profile and profile.protein_goal_g else 120
    carbs_goal = float(profile.carbs_goal_g) if profile and profile.carbs_goal_g else 250
    fat_goal = float(profile.fat_goal_g) if profile and profile.fat_goal_g else 65

    context = f"""
Foydalanuvchi ma'lumotlari:
- Jins: {profile.get_gender_display() if profile and profile.gender else 'Noaniq'}
- Bo'y: {profile.height_cm if profile and profile.height_cm else 'Noaniq'} cm
- Vazn: {profile.weight_kg if profile and profile.weight_kg else 'Noaniq'} kg
- Faollik: {profile.get_activity_level_display() if profile and profile.activity_level else 'Noaniq'}
- Maqsad: {profile.get_goal_display() if profile and profile.goal else 'Noaniq'}
- Kunlik kaloriya maqsadi: {daily_calorie_goal} kkal
- BMR: {profile.bmr if profile and profile.bmr else 'Hisoblanmagan'}
- TDEE: {profile.tdee if profile and profile.tdee else 'Hisoblanmagan'}

Bugungi ovqatlanish ({today}):
- Kaloriya: {consumed_cals:.0f} / {daily_calorie_goal} kkal
- Oqsil: {consumed_protein:.0f} / {protein_goal:.0f} g
- Uglevod: {consumed_carbs:.0f} / {carbs_goal:.0f} g
- Yog': {consumed_fat:.0f} / {fat_goal:.0f} g
- Suv: {water} / 2000 ml

Bugungi ovqatlar:
{chr(10).join(meal_details) if meal_details else 'Hali ovqat kiritilmagan'}

Rasm orqali aniqlangan bugungi ovqatlar:
{chr(10).join(photo_details) if photo_details else 'Rasm orqali ovqat hali kiritilmagan'}

Oxirgi vazn: {f'{last_weight.weight_kg} kg ({last_weight.date})' if last_weight else 'Kiritilmagan'}

So'nggi vazn tarixi:
{chr(10).join(weight_history) if weight_history else 'Vazn tarixi kiritilmagan'}
"""
    return context


class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get('message', '').strip()
        history = request.data.get('history', [])

        if not message:
            return Response({'error': 'Xabar bo\'sh bo\'lmasligi kerak'}, status=400)

        api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        if not api_key:
            return Response({'error': 'AI xizmati sozlanmagan'}, status=503)

        # Foydalanuvchi kontekstini yig'ish
        user_context = get_user_context(request.user)

        # Xabarlar ro'yxatini tayyorlash
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT + "\n\n" + user_context}
        ]

        # Tarixni qo'shish (oxirgi 10 ta xabar)
        for item in history[-10:]:
            if item.get('role') in ('user', 'assistant'):
                messages.append({
                    "role": item['role'],
                    "content": item['content']
                })

        messages.append({"role": "user", "content": message})

        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            reply = data['choices'][0]['message']['content']
            return Response({'reply': reply})

        except requests.exceptions.Timeout:
            return Response({'error': 'AI xizmati javob bermadi, qayta urinib ko\'ring'}, status=504)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'AI xizmati xatosi: {str(e)}'}, status=502)


class AIInsightsView(APIView):
    """Foydalanuvchi ma'lumotlariga asoslangan AI xulosalari"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        
        if not profile:
            return Response({'error': 'Profil topilmadi'}, status=404)
        
        # Oxirgi 7 kunlik ma'lumotlar
        from datetime import timedelta
        week_ago = timezone.now().date() - timedelta(days=7)
        meals = Meal.objects.filter(user=user, date__gte=week_ago)
        weight_logs = WeightLog.objects.filter(user=user, date__gte=week_ago).order_by('-date')
        
        # Statistika
        total_days = 7
        days_logged = meals.values('date').distinct().count()
        
        avg_calories = 0
        avg_protein = 0
        avg_carbs = 0
        avg_fat = 0
        
        if meals.exists():
            for meal in meals:
                avg_calories += float(meal.total_calories or 0)
                avg_protein += float(meal.total_protein or 0)
                avg_carbs += float(meal.total_carbs or 0)
                avg_fat += float(meal.total_fat or 0)
            
            avg_calories /= total_days
            avg_protein /= total_days
            avg_carbs /= total_days
            avg_fat /= total_days
        
        # Vazn o'zgarishi
        weight_change = 0
        if weight_logs.count() >= 2:
            latest_weight = float(weight_logs.first().weight_kg)
            oldest_weight = float(weight_logs.last().weight_kg)
            weight_change = latest_weight - oldest_weight
        
        # Context
        context = {
            "profile": {
                "gender": profile.get_gender_display() if profile.gender else "Noaniq",
                "height": profile.height_cm or 0,
                "current_weight": profile.weight_kg or 0,
                "goal": profile.get_goal_display() if profile.goal else "Noaniq",
                "activity_level": profile.get_activity_level_display() if profile.activity_level else "Noaniq",
                "bmr": profile.bmr or 0,
                "tdee": profile.tdee or 0,
            },
            "targets": {
                "calories": profile.daily_calorie_goal or 2000,
                "protein": float(profile.protein_goal_g or 120),
                "carbs": float(profile.carbs_goal_g or 250),
                "fat": float(profile.fat_goal_g or 65),
            },
            "last_7_days": {
                "days_logged": days_logged,
                "total_days": total_days,
                "avg_calories": round(avg_calories, 1),
                "avg_protein": round(avg_protein, 1),
                "avg_carbs": round(avg_carbs, 1),
                "avg_fat": round(avg_fat, 1),
                "weight_change_kg": round(weight_change, 2),
            }
        }
        
        # AI dan xulosalar olish
        insights = self._get_ai_insights(context)
        
        return Response({
            "context": context,
            "insights": insights
        })
    
    def _get_ai_insights(self, context):
        """DeepSeek AI dan xulosalar olish"""
        api_key = getattr(settings, 'DEEPSEEK_API_KEY', '')
        if not api_key:
            return {
                "summary": "AI xulosa olish uchun API key sozlanmagan",
                "recommendations": [],
                "warnings": [],
                "motivation": ""
            }
        
        prompt = f"""
Siz professional dietolog va fitness murabbisiz. Foydalanuvchi ma'lumotlarini tahlil qilib, qisqa va aniq xulosalar bering (o'zbek tilida).

**Foydalanuvchi profili:**
- Jins: {context['profile']['gender']}
- Bo'y: {context['profile']['height']} cm
- Vazn: {context['profile']['current_weight']} kg
- Maqsad: {context['profile']['goal']}
- Faollik: {context['profile']['activity_level']}
- BMR: {context['profile']['bmr']} kcal
- TDEE: {context['profile']['tdee']} kcal

**Maqsadlar:**
- Kaloriya: {context['targets']['calories']} kcal
- Protein: {context['targets']['protein']} g
- Uglevodlar: {context['targets']['carbs']} g
- Yog': {context['targets']['fat']} g

**Oxirgi 7 kun:**
- Jurnal yuritilgan: {context['last_7_days']['days_logged']}/{context['last_7_days']['total_days']} kun
- O'rtacha kaloriya: {context['last_7_days']['avg_calories']} kcal
- O'rtacha protein: {context['last_7_days']['avg_protein']} g
- O'rtacha uglevodlar: {context['last_7_days']['avg_carbs']} g
- O'rtacha yog': {context['last_7_days']['avg_fat']} g
- Vazn o'zgarishi: {context['last_7_days']['weight_change_kg']} kg

Faqat JSON formatda javob bering:
{{
  "summary": "Umumiy holat (2-3 jumla, o'zbek tilida)",
  "recommendations": ["Tavsiya 1", "Tavsiya 2", "Tavsiya 3"],
  "warnings": ["Ogohlantirish (agar kerak bo'lsa)"],
  "motivation": "Motivatsion xabar (1 jumla)"
}}
"""
        
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': 'Siz professional dietolog. Faqat JSON formatda javob bering.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    'temperature': 0.7,
                    'max_tokens': 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # JSON parse
                import json
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                insights = json.loads(content)
                return insights
            else:
                return {
                    "summary": "AI xulosa olishda xatolik",
                    "recommendations": ["Keyinroq qayta urinib ko'ring"],
                    "warnings": [],
                    "motivation": ""
                }
        except Exception as e:
            return {
                "summary": "Ma'lumotlaringiz asosida xulosa chiqarib bo'lmadi",
                "recommendations": ["Profil va ovqat ma'lumotlarini to'liq kiriting"],
                "warnings": [],
                "motivation": "Davom eting!"
            }
