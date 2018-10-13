from django.urls import path
from .views import HomeView
# from .views import RaingageAPIView, PrecipEventAPIView, HomeView, PrecipEventList
# from .schema import schema
# from graphene_django.views import GraphQLView

app_name = 'precip'

urlpatterns = [
    path(r'', HomeView.as_view()),
    # path('graphql', GraphQLView.as_view(graphiql=True)),
]
