from django.db import models


# Main entity
class Repository(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=300, null=True)
    public_url = models.URLField()
    issues = models.IntegerField()
    updated_at = models.DateTimeField()


# Github programming-language
class RepositoryLanguage(models.Model):
    repository = models.ForeignKey(Repository, related_name='languages', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    size = models.IntegerField()
    color = models.CharField(max_length=7)


# Contributor to repositories who is not a part of dotkom
class ExternalContributor(models.Model):
    username = models.CharField(max_length=30)
    repositories = models.ManyToManyField(Repository)


# Commit in repository
class Commit(models.Model):
    username = models.ForeignKey(ExternalContributor, null=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    description = models.CharField(max_length=150)
    repository = models.ForeignKey(Repository, related_name='repositories', on_delete=models.CASCADE)
