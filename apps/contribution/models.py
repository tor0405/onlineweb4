from django.db import models


# Main entity
class Repository(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=300, null=True)
    public_url = models.URLField()
    issues = models.IntegerField()
    updated_at = models.DateTimeField()

    def weekly_activity(self):
        return ActivityEntry.objects.filter(repository=self)


# Github programming-language
class RepositoryLanguage(models.Model):
    repository = models.ForeignKey(Repository, related_name='languages', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    size = models.IntegerField()
    color = models.CharField(max_length=7)


# Contributor to repositories who is not a part of dotkom
class ExternalContributor(models.Model):
    username = models.CharField(max_length=30)
    repositories = models.ManyToManyField(Repository, through='Contribution')


# Relation between ExternalContributor and Repository
class Contribution(models.Model):
    contributor = models.ForeignKey(ExternalContributor, on_delete=models.CASCADE)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    commits = models.IntegerField()


# Activity of repository
class ActivityEntry(models.Model):
    repository = models.ForeignKey(Repository, related_name='repositories', on_delete=models.CASCADE)
    date = models.DateField()
    score = models.IntegerField()
