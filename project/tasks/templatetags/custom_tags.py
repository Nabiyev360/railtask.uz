from django import template

register = template.Library()

@register.filter
def add_length(list1, list2):
    return len(list1) + len(list2)

@register.filter
def proportion(num1, num2):
    return round((num1 / num2) * 100, 1) if num2 > 0 else 0