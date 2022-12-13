from django.dispatch.dispatcher import receiver
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import conf
from django.db.models import Q
from .models import Profile, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from .utils import searchProfiles, paginateProfiles


def loginUser(request):
    page = 'login' #Page = yazmasının sebebi template'da if loop kullanıcak if page == 'login' loginUser else registerUser

    if request.user.is_authenticated: #Bu çok kullanışlı! Eğer user Login ise direct profiles page'e redirect ediyorum.Decorater kullanmadan.
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username) #Check If a user with this username exists.
        except:
            messages.error(request, 'Username does not exist') #Documentation Django Messages

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user) #Login function creates a session for that user in the database.(User'i login ediyor.)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account') #If next is inside request.get method send the user to here , else send them to their account.

        else:
            messages.error(request, 'Username OR password is incorrect') #Her bir messages'a göre styling oluşturduk.

    return render(request, 'users/login_register.html')


def logoutUser(request):
    logout(request)
    messages.info(request, 'User was logged out!')
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): #form.save() ==> Sadece bunuda yazıp bitirebilirdik ama aşağıdaki modifikasyon eğer user'lar arası case sensitive bir durum varsa bunu ortadan kaldırıyor.Örnek:Kaan KaAn diye 2 user oluşmasını engelliyor.
            user = form.save(commit=False) #We hold this information before processing It.
            user.username = user.username.lower() #We lower the letters of input data.
            user.save() #Then officially add user to database and save.

            messages.success(request, 'User account was created!') #Success message.

            login(request, user)
            return redirect('edit-account')

        else:
            messages.success(
                request, 'An error has occurred during registration')

    context = {'page': page, 'form': form}
    return render(request, 'users/login_register.html', context)


def profiles(request):
    profiles, search_query = searchProfiles(request) #Trigger this function and It will give us profiles and search_query because thats what that function returns.

    custom_range, profiles = paginateProfiles(request, profiles, 5)
    context = {'profiles': profiles, 'search_query': search_query,
               'custom_range': custom_range}
    return render(request, 'users/profiles.html', context)


def userProfile(request, pk): #Typically you would pass in PK to get profile.
    profile = Profile.objects.get(id=pk) #A-Tag içine pass ettiğim değerlerden bir tanesi ID onuda burda PK ile eşitledim.Gerekli projeye erişebilmek adına.

    topSkills = profile.skill_set.exclude(description__exact="") #Tanımı olmayanları çıkart tanımlıları tut.
    otherSkills = profile.skill_set.filter(description="") #Tanımlıları çıkart tanımsızları tut.

    context = {'profile': profile, 'topSkills': topSkills,
               "otherSkills": otherSkills}
    return render(request, 'users/user-profile.html', context)


@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile  #request.user gets us logged in user / and when we add .profile to get the logged in users profile. (one-to-one relationship).

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {'profile': profile, 'skills': skills, 'projects': projects}
    return render(request, 'users/account.html', context)


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile) #instance=profile yazınca profildeki güncel verilerle formdaki boşlukları dolduruyo en başta.

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile) #If there is a POST request process , / also process Image files / we want to know what profile we are updating.(We want to update logged in user.)
        if form.is_valid():
            form.save()

            return redirect('account')

    context = {'form': form}
    return render(request, 'users/profile_form.html', context)


@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm() #Made the form.

    if request.method == 'POST': #Process that data
        form = SkillForm(request.POST) #Pass in the POST data
        if form.is_valid(): #If Its valid
            skill = form.save(commit=False) #This line of code gives us the instance , so we can update the owner and save.
            skill.owner = profile # Owneri güncelle
            skill.save() #Resave
            
            messages.success(request, 'Skill was added successfully!')
            return redirect('account')

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def updateSkill(request, pk): #Created skill view.
    profile = request.user.profile #Got the logged in User.
    skill = profile.skill_set.get(id=pk) #This will make sure only the owner of the skill can edit.
    form = SkillForm(instance=skill) #Instance will tell us which skill we are editing adnd will prefill that information.

    if request.method == 'POST': #Process that data
        form = SkillForm(request.POST, instance=skill) #Pass in the POST data
        if form.is_valid(): #If Its valid
            form.save() #Resave
            messages.success(request, 'Skill was updated successfully!')
            return redirect('account') #If the method is POST / Create a new instance of that form / If the data is valid / Save the data / Then redirect the user to URL name = 'projects'/CRUD'daki C bu.

    context = {'form': form}
    return render(request, 'users/skill_form.html', context)


@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile #request.user picks the logged in User.Because we have #One to One relationship. We could pick the current logged in user's profile with this line of code.
    skill = profile.skill_set.get(id=pk) #Query object.
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill was deleted successfully!')
        return redirect('account')

    context = {'object': skill}
    return render(request, 'delete_template.html', context)


@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all() #Normalde profile.messages_set.all() gerekirdi ancak isim verdiğimiz için Models'de gerek yok.
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests': messageRequests, 'unreadCount': unreadCount}
    return render(request, 'users/inbox.html', context)


@login_required(login_url='login')
def viewMessage(request, pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read == False: #Eğer mesaj daha önceden okunmamış ise / mesajı oku / kaydet.
        message.is_read = True
        message.save()
    context = {'message': message}
    return render(request, 'users/message.html', context)


def createMessage(request, pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient

            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request, 'Your message was successfully sent!')
            return redirect('user-profile', pk=recipient.id)

    context = {'recipient': recipient, 'form': form}
    return render(request, 'users/message_form.html', context)
