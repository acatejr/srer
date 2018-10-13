from django.urls import path, include
from graphene_django.views import GraphQLView

app_name = 'api'

urlpatterns = [
    path('graphql', GraphQLView.as_view(graphiql=True)),
]