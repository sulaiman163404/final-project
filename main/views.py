from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, viewsets, status

from .models import Category, Post, PostImage
from .serializers import CategorySerializer, PostSerializer, PostImageSerializer
from .permissions import IsPostAuthor


class MyPaginationClass(PageNumberPagination):
    page_size = 2

    def get_paginated_response(self, data):
        for i in range(self.page_size):
            text = data[i]['text']
            data[i]['text'] = text[:10] + '...'
        return super().get_paginated_response(data)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = MyPaginationClass

    def get_serializer_context(self):
        return {'request': self.request}

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsPostAuthor, ]
        else:
            permissions = []
        return [permission() for permission in permissions]

    def get_queryset(self):
        queryset = super().get_queryset()
        day_count = int(self.request.query_params.get('days', 0))

        if day_count > 0:
            start_date = timezone.now() - timedelta(days=day_count)
            queryset = queryset.filter(created_at__gte=start_date)
        return queryset

    @action(detail=False, methods=['get'])
    def own(self, request, pk=None):
        queryset = self.get_queryset()
        queryset = queryset.filter(author=request.user)
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])   #router builds path posts/search/
    def search(self, request, pk=None):
        q = request.query_params.get('q')             #request.query_params = request.GET
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) |
                                   Q(text__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostImageView(generics.ListCreateAPIView):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer

    def get_serializer_context(self):
        return {'request': self.request}

