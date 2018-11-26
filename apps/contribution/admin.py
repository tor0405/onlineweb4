from django.contrib import admin

from apps.contribution.models import (ActivityEntry, Contribution, ExternalContributor, Repository,
                                      RepositoryLanguage)


class LanguagesInLine(admin.TabularInline):
    model = RepositoryLanguage
    extra = 0


class ActivityEntriesInLine(admin.TabularInline):
    model = ActivityEntry
    extra = 0


class RepositoryAdmin(admin.ModelAdmin):
    model = Repository
    ordering = ['-updated_at']
    list_display = ['id', 'name', 'updated_at']
    inlines = [
        LanguagesInLine,
        ActivityEntriesInLine
    ]


class ContributionsInLine(admin.TabularInline):
    model = Contribution
    extra = 0


class ExternalContributorAdmin(admin.ModelAdmin):
    model = ExternalContributor
    list_display = ['username']
    inlines = [
        ContributionsInLine
    ]


class ContributionAdmin(admin.ModelAdmin):
    model = Contribution
    list_display = ['contributor', 'repository', 'commits']


class ActivityEntryAdmin(admin.ModelAdmin):
    model = ActivityEntry
    list_display = ['date', 'score']


admin.site.register(ActivityEntry, ActivityEntryAdmin)
admin.site.register(Contribution, ContributionAdmin)
admin.site.register(ExternalContributor, ExternalContributorAdmin)
admin.site.register(Repository, RepositoryAdmin)
