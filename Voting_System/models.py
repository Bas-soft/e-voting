from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Elections(models.Model):
    title=models.CharField(max_length=50)
    description=models.TextField()
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()

    objects = models.Manager()

    def __str__(self):
        return self.title

class Portfolios(models.Model):
    election=models.ForeignKey(Elections,on_delete=models.CASCADE)
    name_of_portfolio=models.CharField(max_length=100)

    objects = models.Manager()

    def __str__(self):
        return self.name_of_portfolio

class Candidate(models.Model):

    election=models.ForeignKey(Elections,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='images/',blank=False,null=False)
    position=models.ForeignKey(Portfolios,on_delete=models.CASCADE)
    Candidate_Number=models.IntegerField(default=0)
    vote=models.IntegerField(default=0)

    objects = models.Manager()

    def __str__(self):
        return self.name


class Votes(models.Model):
    election=models.ForeignKey(Elections,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    portfolio=models.ForeignKey(Portfolios,on_delete=models.CASCADE)
    candidate=models.ForeignKey(Candidate,on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"{self.user} Voted for {self.candidate.name} as {self.portfolio} in {self.election.title}"

class Voters(models.Model):
    election=models.ForeignKey(Elections,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phone=models.CharField(max_length=50)
    index_number=models.CharField(max_length=12)
    secret_token=models.CharField(max_length=15)
    sent_sms = models.BooleanField(default=False, verbose_name="Credentials sent")


    objects = models.Manager()

    def __str__(self):
        return self.index_number

class Expired_Tokens(models.Model):
    election = models.ForeignKey(Elections, on_delete=models.CASCADE)
    index_number = models.CharField(max_length=12)
    secret_token = models.CharField(max_length=12)

    objects = models.Manager()

    def __str__(self):
        return self.index_number