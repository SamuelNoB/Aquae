from django.shortcuts import render
# Create your views here.


def home(request):
    return render(request, 'index.html')

def how_to(request):
    return render(request, 'how_to_use.html')

def about(request):
    return render(request, 'about_us.html')