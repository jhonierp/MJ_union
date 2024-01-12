from django.contrib import admin
from django.urls import path
from proyecto import views 

urlpatterns = [
    path('', views.fun_hom, name='home'),
    path('ahorros', views.fun_ahor,name='ahorros'),
    path('creditos', views.fun_credi,name='creditos'),
    path('registro_user', views.fun_re_us,name='registro_user'),
    path('registro_admin', views.fun_re_adm,name='registro_admin'),
    path('tabla_main', views.fun_tab_main,name='tabla_main'),
    path('registro_edit/<int:id>', views.fun_reg_edit),
    path('tabla_edit', views.fun_tab_edit,name='tabla_edit'),
    path('tabla_edit_admin', views.fun_tab_edit_admin,name='tabla_edit_admin'),
    path('actualizar_campo/', views.actualizar_campo, name='actualizar_campo'),
]
