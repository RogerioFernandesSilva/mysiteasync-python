import asyncio
import time

import httpx
from django.http import HttpResponse, JsonResponse


# ---------------------------------------------------------------------------
# Código 1 (da aula) — view SÍNCRONA que "trava" a thread por 1 segundo.
# ---------------------------------------------------------------------------
def api(request):
    time.sleep(1)
    payload = {"message": "Hello, World!"}

    if "task_id" in request.GET:
        payload["task_id"] = request.GET["task_id"]
    return JsonResponse(payload)


# ---------------------------------------------------------------------------
# Código 2/3 (da aula) — corrigidos: faltavam os imports (asyncio, httpx,
# time) e a indentação de `http_call_async` estava errada (o `async with`
# tinha saído do `for`).
# ---------------------------------------------------------------------------
async def http_call_async():
    for num in range(1, 6):
        await asyncio.sleep(1)
        print(num)

    async with httpx.AsyncClient() as client:
        r = await client.get("https://httpbin.org/")
        print(r)


def http_call_sync():
    for num in range(1, 6):
        time.sleep(1)
        print(num)

    r = httpx.get("https://httpbin.org/")
    print(r)


async def async_view(request):
    """Dispara a tarefa em segundo plano e responde na hora (non-blocking)."""
    loop = asyncio.get_event_loop()
    loop.create_task(http_call_async())
    return HttpResponse("Non-blocking HTTP request")


def sync_view(request):
    """Bloqueia a thread inteira até `http_call_sync` terminar."""
    http_call_sync()
    return HttpResponse("Blocking HTTP request")


# ---------------------------------------------------------------------------
# NOVA VIEW — contador de tempo assíncrono
#
# Ideia: em vez de só disparar uma tarefa e esquecer dela (fire-and-forget,
# como em `async_view`), aqui a própria view espera (await) o contador,
# mas usando asyncio.sleep — que NÃO bloqueia o event loop. Ou seja,
# enquanto essa requisição está "contando", o servidor continua livre
# para atender outras requisições em paralelo (coisa que o Código 1,
# com time.sleep, jamais conseguiria fazer).
# ---------------------------------------------------------------------------
async def async_counter_view(request):
    """
    Conta de 1 até `seconds` (padrão 5), aguardando 1s a cada tick com
    asyncio.sleep (não bloqueante), e retorna o resultado em JSON junto
    com o tempo total decorrido.

    Exemplos de uso:
        /async-counter/                 -> conta até 5
        /async-counter/?seconds=10      -> conta até 10
        /async-counter/?task_id=abc123  -> ecoa o task_id na resposta
    """
    try:
        seconds = int(request.GET.get("seconds", 5))
    except ValueError:
        seconds = 5
    seconds = max(1, min(seconds, 30))  # limite de segurança

    start = time.monotonic()
    counter = 0

    for tick in range(1, seconds + 1):
        await asyncio.sleep(1)
        counter = tick
        print(f"[async_counter_view] tick {counter}/{seconds}")

    elapsed = round(time.monotonic() - start, 2)

    payload = {
        "message": "Contador assíncrono finalizado!",
        "counter": counter,
        "elapsed_seconds": elapsed,
    }
    if "task_id" in request.GET:
        payload["task_id"] = request.GET["task_id"]

    return JsonResponse(payload)


# ---------------------------------------------------------------------------
# BÔNUS — versão "fire-and-forget" do contador, no mesmo estilo do
# `async_view` da aula: responde IMEDIATAMENTE e o contador continua
# rodando em background (aparece só no console/log do servidor).
# ---------------------------------------------------------------------------
async def _background_counter(seconds: int):
    for tick in range(1, seconds + 1):
        await asyncio.sleep(1)
        print(f"[background_counter] tick {tick}/{seconds}")
    print("[background_counter] finalizado!")


async def async_counter_background_view(request):
    try:
        seconds = int(request.GET.get("seconds", 5))
    except ValueError:
        seconds = 5
    seconds = max(1, min(seconds, 30))

    loop = asyncio.get_event_loop()
    loop.create_task(_background_counter(seconds))
    return HttpResponse(
        f"Contador iniciado em background por {seconds}s. "
        f"A resposta não esperou o contador terminar (veja o console)."
    )


