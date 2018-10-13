from precip.models import Raingage
from graphene import ObjectType, Node, Schema
from graphene_django.fields import DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

class RaingageNode(DjangoObjectType):

    class Meta:
        model = Raingage
        interfaces = (Node,)
        filter_fields = ['name', 'code']

class Query(ObjectType):
    raingage = Node.Field(RaingageNode)
    raingages = DjangoFilterConnectionField(RaingageNode)

schema = Schema(query=Query)