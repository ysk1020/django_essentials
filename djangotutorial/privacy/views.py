from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, this is the privacy app index.")

def privacy_policy(request):
    return HttpResponse("This is the privacy policy page.")