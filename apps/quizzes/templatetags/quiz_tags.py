"""
Custom template tags and filters for quizzes
"""

from django import template

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get item from dictionary
    Usage: {{ dict|get_item:key }}
    """
    if dictionary and key:
        return dictionary.get(key)
    return None
