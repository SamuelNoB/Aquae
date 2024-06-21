#!/bin/bash

for n in {539..751}; do
    echo "Executando script para o arquivo Pluviometria_fixture-$n.json"
    python manage.py loaddata simulacao/base_de_dados/fixtures/Pluviometria_fixture-$n.json
    echo "Finalizado Pluviometria_fixture-0$n.json"
done
