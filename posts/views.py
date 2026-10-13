from django.shortcuts import render
from .models import Category, Tag
from .serilizers import CategorySerializer
from rest_framework import viewsets
from rest_framework import permissions, filters

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]