from django.urls import path
# from graphene_django.views import GraphQLView
# from .views import RaingageAPIView, PrecipEventAPIView, HomeView, PrecipEventList
# from .schema import schema

app_name = 'precip'

urlpatterns = []

# urlpatterns = [
#     path(r'graphql', GraphQLView.as_view(graphiql=True, schema=schema), name='srer_graphql'),
#     path(r'api/srer/v1.0/raingages', RaingageAPIView.as_view()),
#     path(r'api/srer/v1.0/precipevents', PrecipEventAPIView.as_view()),
#     path(r'api/srer/v1.0/precipevents/gagename/<str:gagename>/year/<int:year>', PrecipEventList.as_view()),
# ]