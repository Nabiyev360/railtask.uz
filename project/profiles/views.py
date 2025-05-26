from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def my_profile_view(request):
    return render(request, 'profiles/my-profile.html')
