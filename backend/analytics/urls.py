from django.urls import path
from .views import (
    DashboardStatsView,
    WeeklyMacrosView,
    WeeklyWaterView,
    WeightHistoryView
)

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='analytics-dashboard'),
    path('weekly-macros/', WeeklyMacrosView.as_view(), name='analytics-weekly-macros'),
    path('weekly-water/', WeeklyWaterView.as_view(), name='analytics-weekly-water'),
    path('weight-history/', WeightHistoryView.as_view(), name='analytics-weight-history'),
]
