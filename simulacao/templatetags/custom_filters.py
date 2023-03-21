from django import template
import locale

#locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
register = template.Library()


@register.filter()
def currency(value):
    moeda = locale.currency(value, grouping=True)
    moeda = moeda[2:]
    return moeda


@register.filter(name="potavel")
def potavel(uso, categoria):
    if categoria == "oferta":
        potable = uso.lower() in [
        "chuveiro",
        "máquina de lavar louça",
        "tanque",
        "torneira de banheiro",
        ]

        if potable:
            return "checked"
        else:
            return ""

    potable = uso.lower() in [
        "torneira de lavatório",
        "chuveiro",
        "bidet/ducha higiênica",
        "torneira de cozinha",
        "filtro de água",
        "máquina de lavar louça",
        "piscina",
        "torneira de banheiro",
    ]
    if potable:
        return ""
    else:
        return "checked"
    
    
