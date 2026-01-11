from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import threading

from game.core.GameFunctions import GameFunctions
from game.core.ImageProcessor import ImageProcessor
from game.scripts.send_throw import simulate_throws, stop_simulation

games_received = []

@csrf_exempt
def init_game(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Játék adatok érkeztek:", data)

            games_received.append(data)

            stop_simulation.clear()
            thread = threading.Thread(target=simulate_throws, args=(data,))
            thread.start()

            return JsonResponse({'status': 'ok'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def stop_game(request):
    if request.method == 'POST':
        stop_simulation.set()
        return JsonResponse({'status': 'stopped'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def turn_on_cameras(request):
    if request.method == 'POST':
            GameFunctions.turnOnCameras()
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)