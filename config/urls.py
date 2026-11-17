from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from solicitacoes.login_forms import EmailAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('conta/entrar/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=EmailAuthenticationForm), name='login'),
    path('conta/sair/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('solicitacoes.urls')),
]
