from rest_framework import status
from rest_framework.response import Response


class AddOrDelMixin:
    serializer_class = None
    model_class = None

    def add_or_delete_object(self, model, obj, request, serializer, args):
        if request.method == 'DELETE':
            model.objects.filter(**args).delete()
            return Response(
                {'detail': 'Удалено'},
                status=status.HTTP_204_NO_CONTENT,
            )

        if not model.objects.filter(**args).exists():
            model.objects.create(**args)
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
