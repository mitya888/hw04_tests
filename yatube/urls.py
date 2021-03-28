from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    # дополнительно к стандартному фреймворку авторизаций
    # добавлено представление для регистрации
    path("admin/", admin.site.urls),
    path("", include('posts.urls')),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('about/', include('about.urls', namespace='about')),
]
