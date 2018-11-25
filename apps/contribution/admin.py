from django.contrib import admin

from apps.contribution.models import Commit, Contribution, ExternalContributor, Repository, RepositoryLanguage


class LanguagesInLine(admin.TabularInline):
    model = RepositoryLanguage
    extra = 0


class RepositoryAdmin(admin.ModelAdmin):
    model = Repository
    ordering = ['-updated_at']
    list_display = ['id', 'name', 'updated_at']
    inlines = [
        LanguagesInLine,
    ]


class CommitAdmin(admin.ModelAdmin):
    model = Commit


class ExternalContributorAdmin(admin.ModelAdmin):
    model = ExternalContributor
    list_display = ['username']


class ContributionAdmin(admin.ModelAdmin):
    model = Contribution
    list_display = ['contributor', 'repository', 'commits']


admin.site.register(Commit, CommitAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(ExternalContributor, ExternalContributorAdmin)
admin.site.register(Repository, RepositoryAdmin)
