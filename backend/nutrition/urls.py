from django.urls import path

from .views import AIChatView, AIInsightsView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('insights/', AIInsightsView.as_view(), name='ai-insights'),
]
