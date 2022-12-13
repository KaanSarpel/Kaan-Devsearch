from .models import Project, Tag
from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginateProjects(request, projects, results):

    page = request.GET.get('page') #Sadece 1 yazsam page'e bana 1. sayfayı gösterir oyüzden dynamic bir value yaptık.
    paginator = Paginator(projects, results) #At Paginator first you select query set and then you have to decide how many inputs per pages that you are going to display. /projects önceki functiondan içeri pass edildi.

    try:
        projects = paginator.page(page) #paginator.page means what page do we want to get this queryset from , which right now we set to current passed in page. This line of code ile ilgili voice note var dinle mutlaka.
    except PageNotAnInteger:
        page = 1
        projects = paginator.page(page) #If page is not passed then the page is 1.Yani direk projects url'ine giderse.
    except EmptyPage:
        page = paginator.num_pages
        projects = paginator.page(page) #If the user provided page number that doesn't exist to url / select the total number of pages available / go ahead and give us that last page.

    leftIndex = (int(page) - 4)

    if leftIndex < 1:
        leftIndex = 1

    rightIndex = (int(page) + 5) #If we are on Page 3 rightIndex button will be at index position 3+5 = 8 (Because this is index position we will see page 7) 

    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages + 1

    custom_range = range(leftIndex, rightIndex) #Custom range aynı zamanda toplam sayfa sayısını sisteme tanıtıyor.

    return custom_range, projects


def searchProjects(request):

    search_query = '' #Herhangibir get request yoksa eğer , search_query '' yaptık bütün projeleri listeleyebilmek adına. / Template'da name ve value düzenlemeyi unutma.

    if request.GET.get('search_query'): #If there is GET request extract that value that's sent in.
        search_query = request.GET.get('search_query')

    tags = Tag.objects.filter(name__icontains=search_query)

    projects = Project.objects.distinct().filter(
        Q(title__icontains=search_query) |
        Q(description__icontains=search_query) | 
        Q(owner__name__icontains=search_query) | #Burda owner foreign key, Profile modelinden inherit ediyor,o yüzden o modeldeki hangi attribute üzerinde arama yapmak istediğimizi yazdık owner => name .
        Q(tags__in=tags)
    )
    return projects, search_query
