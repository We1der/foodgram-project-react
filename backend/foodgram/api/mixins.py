from rest_framework import status
from rest_framework.response import Response


class AddOrDelMixin:
    serializer_class = None
    model_class = None

    def add_or_delete_object(self, model, obj, request, serializer, **kwargs):
        if request.method == 'DELETE':
            model.objects.filter(**kwargs).delete()
            return Response(
                {'detail': 'Удалено'},
                status=status.HTTP_204_NO_CONTENT,
            )

        if not model.objects.filter(**kwargs).exists():
            model.objects.create(**kwargs)
            response_data = serializer(
                obj,
                context={'request': request},
            )
            return Response(
                response_data.data,
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {'errors': 'Экземпляр класса уже существует'},
                status=status.HTTP_400_BAD_REQUEST,
            )
