import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def hello_world(request):
    return JsonResponse({
        "message": "Hello world",
        "version": "v.1.0"
    })

def welcome_message(request, name: str):
    is_admin = request.GET.get("admin") == "true"

    if is_admin:
        return JsonResponse(
            {
                "role": "admin",
                "message": "Welcome to your admin app",
                "name": name.capitalize(),
            }
        )
    else:
        return JsonResponse(
            {
                "role": "user",
                "message": "Welcome to your user app",
                "name": name.capitalize(),
            }
        )


@csrf_exempt
def home(request, name: str):
    if request.method != "POST":
        return JsonResponse({"status": 405, "error": "Method not allowed!"}, status=405)

    try:
        data_received = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    age = data_received.get("age")
    country = data_received.get("country")

    if age is None or country is None:
        return JsonResponse({"error": "age and country are required"}, status=400)

    message = f"Hello {name}"

    return JsonResponse({"age": age, "country": country, "message": message})


@csrf_exempt
def profile(request, username: str):

    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data_received = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    age = data_received.get("age")
    country = data_received.get("country")
    occupation = data_received.get("occupation")

    if age is None or country is None or occupation is None:
        return JsonResponse({"error": "age, country and occupation are required"}, status=400)


    is_verbose = request.GET.get("verbose") == "true"
    verbose = True if is_verbose else False  # noqa: SIM210

    user_agent = request.headers.get("User-Agent")

    return JsonResponse({
        "username": username,
        "age": age,
        "country": country,
        "occupation": occupation,
        "is_verbose": verbose,
        "user_agent": user_agent
    })

def uniqueEndpoint(request):
    age = request.GET.get("age")
    return JsonResponse({
        "status": 200,
        "age": age
    })
