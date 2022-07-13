from django import template
import locale

locale.setlocale(locale.LC_ALL, "pt_BR")
register = template.Library()


@register.filter()
def currency(value):
    moeda = locale.currency(value, grouping=True)
    moeda = moeda[2:]
    return moeda


@register.filter(name="potavel")
def potavel(uso, categoria):
    if categoria == "oferta":
        return "checked"
    potable = uso.lower() in [
        "torneira de lavatório",
        "chuveiro",
        "bidet/ducha higiênica",
        "torneira de cozinha",
        "filtro de água",
        "máquina de lavar louça",
        "piscina",
    ]
    if potable:
        return ""
    else:
        return "checked"
