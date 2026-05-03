from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('employees/', include('apps.employees.urls')),
    path('projects/', include('apps.projects.urls')),
    path('finance/', include('apps.finance.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('fleet/', include('apps.fleet.urls')),
    path('audit/', include('apps.audit.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
