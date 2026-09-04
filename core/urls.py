from django.urls import path

from . import views

urlpatterns = [
    # Código 1 — view síncrona (bloqueante) que devolve JSON
    path("api/", views.api, name="api"),
    # Código 3 — view síncrona que faz chamadas HTTP bloqueantes
    path("sync/", views.sync_view, name="sync_view"),
    # Código 2/3 — view assíncrona fire-and-forget (da aula)
    path("async/", views.async_view, name="async_view"),
    # NOVO — view assíncrona com contador de tempo (aguarda e responde no final)
    path("async-counter/", views.async_counter_view, name="async_counter_view"),
    # NOVO (bônus) — contador assíncrono em background, resposta imediata
    path(
        "async-counter-background/",
        views.async_counter_background_view,
        name="async_counter_background_view",
    ),
]
