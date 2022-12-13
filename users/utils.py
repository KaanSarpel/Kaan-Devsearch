from django.db.models import Q
from .models import Profile, Skill

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginateProfiles(request, profiles, results):
    page = request.GET.get('page')
    paginator = Paginator(profiles, results)

    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        profiles = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)

    leftIndex = (int(page) - 4)

    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page) + 5)

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex)

    return custom_range, profiles


def searchProfiles(request):
    search_query = ''  #If we don't have data from frontend we want to make sure It is empty string so It doesn't ruin our filter. This is the 'name' attribute of input field of Search(html).

    if request.GET.get('search_query'): #If there is GET request extract that value that's sent in.
        search_query = request.GET.get('search_query')

    skills = Skill.objects.filter(name__icontains=search_query) #Because skill is a child element we had to do do and extra line of code in order to search skills in our search bar.

    profiles = Profile.objects.distinct().filter(  #Distinct olmadığında ilk başta sorun yoktu,ancak skills araştırdığımda bir profilin birden fazla skilli olduğu zaman aynı profili 2-3 defa listeliyordu distinct koyarak bunun önüne geçtik.
        Q(name__icontains=search_query) | #search_query empty string olduğu için hala tüm profiller listelenmeye devam edicek. Aradaki | işareti de 'or' demek.
        Q(short_intro__icontains=search_query) | 
        Q(skill__in=skills) #Does the profile have a skill that is listed in this query set.If It does list that profile. 
    ) 

    return profiles, search_query
