from django.contrib import admin
from django.urls import path,include
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView,SpectacularSwaggerView
from apps.core import views as v
r=DefaultRouter()
for prefix,cls in [('projects',v.ProjectViewSet),('prospects',v.ProspectViewSet),('campaigns',v.CampaignViewSet),('conversations',v.ConversationViewSet),('leads',v.LeadViewSet),('knowledge',v.KnowledgeViewSet),('ai-config',v.AIConfigViewSet),('playbooks',v.PlaybookViewSet)]:r.register(prefix,cls)
urlpatterns=[path('admin/',admin.site.urls),path('login/',v.AdminLogin.as_view(),name='login'),path('logout/',LogoutView.as_view(),name='logout'),path('',v.dashboard,name='dashboard'),path('app/<slug:section>/',v.dashboard,name='section'),path('api/v1/',include(r.urls)),path('api/v1/ai/test/',v.test_ai),path('api/v1/analytics/overview/',v.overview),path('api/v1/analytics/prospects.csv',v.export_prospects),path('api/schema/',SpectacularAPIView.as_view(),name='schema'),path('api/docs/',SpectacularSwaggerView.as_view(url_name='schema'),name='swagger-ui')]

from apps.core.workspace import inbox
urlpatterns += [path('inbox/',inbox,name='inbox'), path('inbox/<int:pk>/',inbox,name='inbox-detail')]
from apps.core.workspace import import_prospects
urlpatterns += [path('prospects/import/',import_prospects,name='prospect-import'),path('api/v1/analytics/prospects.xlsx',v.export_excel)]
from apps.core.integrations.instagram.webhooks import webhook
urlpatterns += [path('integrations/instagram/webhook/',webhook)]
