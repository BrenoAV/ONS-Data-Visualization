#!/bin/bash

echo "Downloading dataset from Dados Abertos ONS (https://dados.ons.org.br/)"

urlsLoadBalance=("https://ons-dl-prod-opendata.s3.amazonaws.com/dataset/carga_energia_di/CARGA_ENERGIA_2022.csv")
pathData="data"

mkdir -p $pathData
echo "Dir $pathData created!"

# Interacting on all dataset
for urlLoadBalance in ${urlsLoadBalance[@]}; do
    echo "Downloading $urlLoadBalance..."
    cd $pathData && curl -O $urlLoadBalance 
done
