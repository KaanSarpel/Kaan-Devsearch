from django.db import models
import uuid

from django.db.models.deletion import CASCADE
from users.models import Profile
# Create your models here.


class Project(models.Model):
    owner = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE) #Many-to-One Project can have one owner but we have multiple projects./If the user gets deleted don't delete the project./Profile Parent
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    featured_image = models.ImageField(
    null=True, blank=True, default="default.jpg") #Every model that we dont have image to is going to have this default.jpg picture.
    demo_link = models.CharField(max_length=2000, null=True, blank=True)
    source_link = models.CharField(max_length=2000, null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    vote_total = models.IntegerField(default=0, null=True, blank=True)
    vote_ratio = models.IntegerField(default=0, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True) #We want to know when this profile is created.
    id = models.UUIDField(default=uuid.uuid4, unique=True, #Also set a unique ID.
                          primary_key=True, editable=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-vote_ratio', '-vote_total', 'title'] #Vote Ratio'larına göre sırala eğer vote_ratio in başına - koyarsan descending to ascendinge çevirir. 

    @property
    def imageURL(self):
        try:
            url = self.featured_image.url
        except:
            url = ''
        return url

    @property
    def reviewers(self):
        queryset = self.review_set.all().values_list('owner__id', flat=True)
        return queryset

    @property
    def getVoteCount(self):
        reviews = self.review_set.all() #_set kullanma sebebimiz burdaki self yani Project modeli Review modelinin parent element'i / this line of code gets all the reviews related to current project.
        upVotes = reviews.filter(value='up').count()
        totalVotes = reviews.count() #.count method will let us know how many items we have on that query set.

        ratio = (upVotes / totalVotes) * 100
        self.vote_total = totalVotes
        self.vote_ratio = ratio

        self.save()


class Review(models.Model):
    VOTE_TYPE = (
        ('up', 'Up Vote'),
        ('down', 'Down Vote'),
    )
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE) #When the main project gets deleted all the reviews connected to that projects gets NULL value.CASCADE deletes all reviews related to that project.
    body = models.TextField(null=True, blank=True)
    value = models.CharField(max_length=200, choices=VOTE_TYPE)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    class Meta:
        unique_together = [['owner', 'project']] #We bind this 2 attributes together. This allows nobody to leave bunch of reviews to a project.

    def __str__(self):
        return self.value


class Tag(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    id = models.UUIDField(default=uuid.uuid4, unique=True,
                          primary_key=True, editable=False)

    def __str__(self):
        return self.name
