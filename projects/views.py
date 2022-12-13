from django.core import paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Tag
from .forms import ProjectForm, ReviewForm
from django.template.defaultfilters import pluralize
from .utils import searchProjects, paginateProjects


def projects(request):
    projects, search_query = searchProjects(request)
    custom_range, projects = paginateProjects(request, projects, 6) #Projects ilk başta tüm query bu function'ı call ettiğimizde resetliyoruz onu , 6 ise utils.py da yarattığımız function bir results değeri istiyor onu bu şekilde sisteme giriyoruz.

    context = {'projects': projects,
               'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'projects/projects.html', context)


def project(request, pk):
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST) #We process the form.
        review = form.save(commit=False)  #In simple words, here we update the form object and let them know that don't save the values in the database right now, we just get the instance of the form and then after manually adding the missing inputs then we save.
        review.project = projectObj
        review.owner = request.user.profile
        review.save()

        projectObj.getVoteCount

        messages.success(request, 'Your review was successfully submitted!')
        return redirect('project', pk=projectObj.id) #This is how we can redirect to dynamic value like this.

    return render(request, 'projects/single-project.html', {'project': projectObj, 'form': form})




@login_required(login_url="login") #Send the user to login page If they are not logged in.
def createProject(request):
    profile = request.user.profile #request.user picks the logged in User.Because we have #One to One relationship. We could pick the current logged in user's profile with this line of code.
    form = ProjectForm() #Form oluştur demek bu.

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(',',  " ").split() #newtags is name of the textarea in createproject form thats how we can query.
        form = ProjectForm(request.POST, request.FILES) #request.POST get the POST request data , request.FILES get the FILES request data.
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile # Bu satırları projeyi create ettikten sonra hangi user'a ait olduğunu belirlemek için yazdık.
            project.save() #Resave

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag) #We are either gonna create a tag or if one exists we are simply just gonna query that tag. To use get_or_create we do need to add created which is a True or False value.
                project.tags.add(tag)
            messages.success(request, 'Your ta{} has been added successfully.'.format(pluralize(newtags,'g,gs')))
            return redirect('account')

    context = {'form': form}
    return render(request, "projects/project_form.html", context)


@login_required(login_url="login")
def updateProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk) # _set will give us all the projects of that user. 
    tags = project.tags.all()
    form = ProjectForm(instance=project) #İlk projeyi seçiyoruz / Sonra onu bir form'a koyuyoruz.

    if request.method == 'POST': #Eğer bu form'a post request gelirse
        newtags = request.POST.get('newtags').replace(',',  " ").split()

        form = ProjectForm(request.POST, request.FILES, instance=project) #Yeni bir form oluştur.
        if form.is_valid(): #Eğer veri geçerli ise.
            project = form.save() #Kaydet.
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            messages.success(request, 'Your ta{} has been added successfully.'.format(pluralize(newtags,'g,gs')))    

            return redirect('account')

    context = {'form': form, 'project': project,'tags':tags}
    return render(request, "projects/project_form.html", context)


@login_required(login_url="login")
def deleteProject(request, pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('account')
    context = {'object': project}
    return render(request, 'delete_template.html', context)


@login_required(login_url='login')
def updateReview(request,pk):
  profile = request.user.profile #Got the logged in User.
  review = profile.review_set.get(id=pk) #This will make sure only the owner of the skill can edit.
  form = ReviewForm(instance=review) #Instance will tell us which review we are editing and will pre-fill that information.

  if request.method == 'POST': #Process that data.
    form = ReviewForm(request.POST, instance=review) #Pass in the POST data.
    if form.is_valid(): #If It's valid,
      form.save() #Resave.
      messages.success(request,'Review was updated successfully!')
      return redirect('account')  #If the method is POST / Create a new instance of that form / Is the data is valid / Save the data / Then redirect the user to URL name = 'projects'/CRUD'daki C bu.

  context = {'form':form}
  return render(request,'projects/review_form.html',context)

@login_required(login_url='login')
def deleteReview(request,pk):
  profile = request.user.profile #Got the logged in User.
  review = profile.review_set.get(id=pk) #This will make sure only the owner of the skill can edit.

  if request.method == 'POST':
    review.delete()
    messages.success(request,'Review was deleted successfully!')
    return redirect('account') 
  
  context = {'object':review.body} #Pass into the context disctionary as object.
  return render(request,'delete_template.html',context) #Sonra object kelimesini delete_template.html de kullanabilmek için context şeklinde buraya yerleştiriyoruz.




@login_required(login_url='login')
def deleteTag(request,pk):
  profile = request.user.profile
  tag = Tag.objects.get(id=pk)

  if request.method == 'POST':
    tag.delete()
    return redirect('projects') 

  context = {'object':tag} 
  return render(request,'delete_template.html',context)

