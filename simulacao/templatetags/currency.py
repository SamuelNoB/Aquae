from django import template
import locale

locale.setlocale(locale.LC_ALL, 'pt_BR')
register = template.Library()


@register.filter()
def currency(value):
    moeda = locale.currency(value, grouping=True)
    moeda = moeda[2:]
    return moeda