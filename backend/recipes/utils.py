from django.http.response import HttpResponse


def get_ingredients_list(ingredients_list):
    """Формирование списка покупок."""

    ingredients_dict = {}
    list_to_buy = []
    if not ingredients_list:
        return (['Добавьте в корзину хотя бы один рецепт!', ])
    for ingredient in ingredients_list:
        amount = ingredient.amount
        name = ingredient.ingredient.name
        measurement_unit = ingredient.ingredient.measurement_unit
        if name in ingredients_dict:
            ingredients_dict[name]['amount'] += amount
        else:
            ingredients_dict[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount,
            }
    for ingredient, params in ingredients_dict.items():
        pam = params["amount"]
        pmu = params["measurement_unit"]
        list_to_buy.append(
            f'{ingredient}-{pam} {pmu}.\n',
        )
    return list_to_buy


def download_response(download_list, filename):
    """Формирование файла для скачивания списка покупок."""

    response = HttpResponse(download_list, 'Content-Type: text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
