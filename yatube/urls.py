from django.urls import include, path

# Добавляем к путям из приложения posts пространства имен.
urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('group/<slug:slug>/', include('posts.urls', namespace='posts')),
    path('auth/', include('django.contrib.auth.urls'))
]