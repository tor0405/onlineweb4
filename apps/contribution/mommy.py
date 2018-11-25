import json

import requests
from django.conf import settings
from django.utils import timezone
from pytz import timezone as tz

from apps.contribution.models import Contribution, ExternalContributor, Repository, RepositoryLanguage
from apps.mommy import schedule
from apps.mommy.registry import Task


class UpdateRepositories(Task):

    @staticmethod
    def run():
        # Load new data
        fresh = UpdateRepositories.git_repositories()
        dotkom_members = UpdateRepositories.dotkom_members()

        localtz = tz('Europe/Oslo')
        for repo in fresh:
            fresh_repo = Repository(
                id=repo['id'],
                name=repo['name'],
                description=repo['description'],
                updated_at=localtz.localize(timezone.datetime.strptime(repo['updated_at'], "%Y-%m-%dT%H:%M:%SZ")),
                public_url=repo['public_url'],
                issues=repo['issues']
            )

            # If repository exists, only update data
            if Repository.objects.filter(id=fresh_repo.id).exists():
                stored_repo = Repository.objects.get(id=fresh_repo.id)
                repo_languages = repo['languages']
                UpdateRepositories.update_repository(stored_repo, fresh_repo, repo_languages, dotkom_members)

            # else: repository does not exist
            else:
                repo_languages = repo['languages']
                UpdateRepositories.new_repository(fresh_repo, repo_languages, dotkom_members)

        # Delete repositories that does not satisfy the updated_at limit
        old_repositories = Repository.objects.all()
        for repo in old_repositories:
            if repo.updated_at < timezone.now() - timezone.timedelta(days=730):
                repo.delete()

    @staticmethod
    def update_repository(stored_repo, fresh_repo, repo_languages, dotkom_members):
        stored_repo.name = fresh_repo.name
        stored_repo.description = fresh_repo.description
        stored_repo.updated_at = fresh_repo.updated_at
        stored_repo.public_url = fresh_repo.public_url
        stored_repo.issues = fresh_repo.issues
        stored_repo.save()

        # Update languages if they exist, and add if not
        for language in repo_languages:
            if RepositoryLanguage.objects.filter(type=language['name'], repository=stored_repo).exists():
                stored_language = RepositoryLanguage.objects.get(type=language['name'], repository=stored_repo)
                stored_language.size = language['size']
                stored_language.color = language['color']
                stored_language.save()
            else:
                new_language = RepositoryLanguage(
                    type=language['name'],
                    size=language['size'],
                    color=language['color'],
                    repository=stored_repo
                )
                new_language.save()

        # update repository contributors
        contributors = UpdateRepositories.get_contributors(stored_repo.name)
        for username in contributors:
            if username not in dotkom_members:
                if ExternalContributor.objects.filter(username=username).exists():
                    contributor = ExternalContributor.objects.get(username=username)

                    if Contribution.objects.filter(contributor=contributor, repository=stored_repo).exists():
                        contribution = Contribution.objects.get(contributor=contributor, repository=stored_repo)
                        contribution.commits = contributors[username]
                        contribution.save()
                    else:
                        new_contribution = Contribution(
                            contributor=contributor,
                            repository=stored_repo,
                            commits=contributors[username]
                        )
                        new_contribution.save()
                else:
                    new_contributor = ExternalContributor(username=username)
                    new_contributor.save()

                    new_contribution = Contribution(
                        contributor=new_contributor,
                        repository=stored_repo,
                        commits=contributors[username]
                    )
                    new_contribution.save()

    @staticmethod
    def new_repository(new_repo, new_languages, dotkom_members):
        # Filter out repositories with inactivity past 2 years (365 days * 2)
        if new_repo.updated_at > timezone.now() - timezone.timedelta(days=730):
            new_repo = Repository(
                id=new_repo.id,
                name=new_repo.name,
                description=new_repo.description,
                updated_at=new_repo.updated_at,
                public_url=new_repo.public_url,
                issues=new_repo.issues
            )
            new_repo.save()

            # Add repository languages
            for language in new_languages:
                new_language = RepositoryLanguage(
                    type=language['name'],
                    size=language['size'],
                    color=language['color'],
                    repository=new_repo
                )
                new_language.save()

            # new repository contributors
            contributors = UpdateRepositories.get_contributors(new_repo.name)
            for username in contributors:
                if username not in dotkom_members:
                    if ExternalContributor.objects.filter(username=username).exists():
                        contributor = ExternalContributor.objects.get(username=username)
                    else:
                        contributor = ExternalContributor(username=username)
                        contributor.save()

                    contribution = Contribution(
                        contributor=contributor,
                        repository=new_repo,
                        commits=contributors[username]
                    )
                    contribution.save()

    @staticmethod
    def git_repositories():
        query = """
        {
          organization(login: "dotkom") {
            repositories (first: 100) {
              nodes {
                id
                name
                description
                updatedAt
                url
                issues (states: [OPEN]){
                  totalCount
                }
                isPrivate
                languages (first:10) {
                  totalSize
                  edges {
                    size
                    node {
                      name
                      color
                    }
                  }
                }
              }
            }
          }
        }
        """

        response = UpdateRepositories.post_graphql(query)
        dict_repos = response.get('data', {}).get('organization', {}).get('repositories', {}).get('nodes')

        repository_list = []
        for r in dict_repos:

            # If repository is private, skip
            if r.get('isPrivate'):
                continue

            total_size = r.get('languages', {}).get('totalSize')
            languages = []
            for l in r.get('languages', {}).get('edges'):
                language = {
                    'name': l.get('node', {}).get('name'),
                    'color': l.get('node', {}).get('color'),
                    'size': l.get('size')
                }
                languages.append(language)

            repo = {
                'id': r.get('id'),
                'name': r.get('name'),
                'description': r.get('description'),
                'updated_at': r.get('updatedAt'),
                'public_url': r.get('url'),
                'issues': r.get('issues', {}).get('totalCount'),
                'total_size': total_size,
                'languages': languages
            }
            repository_list.append(repo)

        return repository_list

    @staticmethod
    def dotkom_members():
        query = """
                {
                  organization(login: "dotkom") { 
                    members (first: 100) {
                      nodes {
                        login
                      }
                    }
                  }
                }
                """
        response = UpdateRepositories.post_graphql(query)
        members = response.get('data', {}).get('organization', {}).get('members', {}).get('nodes')

        member_list = []
        for member in members:
            member_list.append(member.get('login'))
        return member_list

    # RestV3 for contributors, as GraphQL does not support this yet
    # Returns dictionary { user: contributions }
    @staticmethod
    def get_contributors(repo_name):
        url = "https://api.github.com/repos/dotkom/{0}/contributors?per_page=100".format(repo_name)
        r = requests.get(url)
        data = json.loads(r.text)

        contributors = {}
        for user in data:
            username = str(user['login'])
            commits = int(user['contributions'])
            contributors[username] = commits
        return contributors

    # GraphQL post method
    @staticmethod
    def post_graphql(query):
        token = settings.GITHUB_GRAPHQL_TOKEN
        url = "https://api.github.com/graphql"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'bearer ' + str(token)
        }

        r = requests.post(url, json={'query': query}, headers=headers)
        return json.loads(r.text)

schedule.register(UpdateRepositories, day_of_week="mon-sun", hour=6, minute=0)

