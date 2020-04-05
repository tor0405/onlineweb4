import graphene

from apps.events.graphql.schema import EventQuery


class Query(EventQuery, graphene.ObjectType):
    pass



schema = graphene.Schema(query=Query )
