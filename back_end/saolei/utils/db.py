from typing import Type
from django.db.models import Count, Model, TextChoices


def get_choice_counts_filtered(model: Type[Model], field_name: str, choices_class: Type[TextChoices], **filter_kwargs):
    choice_values: list[str] = [value for value, _ in choices_class.choices]
    counts = model.objects.filter(**filter_kwargs).values(field_name).annotate(count=Count('pk'))
    count_dict: dict[str, int] = {item[field_name]: item['count'] for item in counts}
    return {value: count_dict.get(value, 0) for value in choice_values}
