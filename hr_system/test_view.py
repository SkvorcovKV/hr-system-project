from django.http import HttpResponse

def simple_test(request):
    return HttpResponse("<h1>Django работает!</h1><p>Если это видите, сервер работает.</p>")