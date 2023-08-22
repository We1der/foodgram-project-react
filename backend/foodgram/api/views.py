from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscribe, Tag)
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAdminUser, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import RecipeFilter
from .pagination import FoodgramPaginator
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, RecipeShortSerializer,
                          SetPasswordSerializer, SubscriptionsSerializer,
                          TagSerializer, UserSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FoodgramPaginator
    permission_classes = (IsAdminUser, IsAuthenticatedOrReadOnly)

    @action(
        methods=('GET',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = self.get_serializer_class()
        serializer = serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('POST',),
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            'Пароль успешно изменен',
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={
                'user': request.user,
                'recipes_limit': request.GET.get('recipes_limit'),
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if not Subscribe.objects.filter(
                    author=author,
                    user=request.user,
            ).exists():
                serializer = SubscriptionsSerializer(
                    author,
                    context={
                        'user': request.user,
                        'recipes_limit': request.GET.get('recipes_limit'),
                        'author': author,
                    }
                )
                sub = Subscribe.objects.create(
                    author=author,
                    user=request.user,
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {'detail': 'Подписка уже оформлена'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            sub = get_object_or_404(
                Subscribe,
                author=author,
                user=request.user,
            )
            sub.delete()
            return Response(
                {'detail': 'Отписка выполнена'},
                status=status.HTTP_204_NO_CONTENT,
            )


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = FoodgramPaginator
    permission_classes = (IsAuthorOrAdminOrReadOnly, )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=('post', 'delete', ),
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not ShoppingCart.objects.filter(
                    recipe=recipe,
                    user=request.user,
            ).exists():
                ShoppingCart.objects.create(recipe=recipe, user=request.user)
                response_data = RecipeShortSerializer(
                    recipe,
                    context={'request': request},
                )
                return Response(
                    response_data.data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {'errors': 'Рецепт уже есть в списке.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT,
            )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__ShoppingCart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(sum_amount=Sum('amount'))
        shopping_cart_for_download = []

        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['sum_amount']
            measurement_unit = ingredient['ingredient__measurement_unit']
            shopping_cart_for_download.append(
                f'{name} - {amount}{measurement_unit}\n'
            )
        response = HttpResponse(
            shopping_cart_for_download,
            'Content-Type: text/plain',
        )
        response['Content-Disposition'] = 'attachment; filename="products.txt"'
        return response

    @action(
        detail=True,
        methods=('post', 'delete', ),
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if not Favorite.objects.filter(
                    recipe=recipe,
                    user=request.user,
            ).exists():
                Favorite.objects.create(recipe=recipe, user=request.user)
                response_data = RecipeShortSerializer(
                    recipe,
                    context={'request': request},
                )
                return Response(
                    response_data.data,
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {'errors': 'Рецепт уже есть в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            Favorite.objects.filter(
                user=request.user,
                recipe=recipe,
            ).delete()
            return Response(
                {'detail': 'Рецепт успешно удален из избранного'},
                status=status.HTTP_204_NO_CONTENT,
            )


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = None
    permission_classes = (AllowAny,)
