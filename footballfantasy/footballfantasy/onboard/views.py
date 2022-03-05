from django.shortcuts import render


# Create your views here.
def onboard(request):
    return render(request, 'onboard/onboard.html')
