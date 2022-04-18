"""Portal URL Configuration
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from agent.views import VMBornAPIView, HVBornAPIView, HVAliveAPIView, VMAliveAPIView
from cmdb.views import HVViewSet, VMViewSet

router = DefaultRouter()
router.register('hv', HVViewSet)
router.register('vm', VMViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hv/born/', HVBornAPIView.as_view()),
    path('vm/born/', VMBornAPIView.as_view()),
    path('vm/alive/', HVAliveAPIView.as_view()),
    path('vm/alive/', VMAliveAPIView.as_view()),
]

urlpatterns += router.urls
