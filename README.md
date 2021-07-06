# Check SSL - Python

![langage](https://img.shields.io/badge/Langage-Python-green.svg) 
![version](https://img.shields.io/badge/version-Beta-purple.svg)
[![Twitter](https://img.shields.io/twitter/follow/pg3io.svg?style=social)](https://twitter.com/intent/follow?screen_name=pg3io)

Vérifie l'expiration d'un certificat SSL pour des urls donnés
Comme pour crawlurl, ce service peut envoyer les données vers influxDB
## Input

Lister vos urls dans un fichier "yml"

## Output

### Sans InfluxDB

dans le terminal :
```
{'url': <URL>, 'expiration': <ssl_expiration_timestamp>, 'dns': [<DNS>]}
```

### Avec InfluxDB
sur la base de données :
```
measurement: ssl_check
tag: host=${domaine}
expiration: ${date d'expiration}
delta: ${nombre de jours avant expiration}
```

## Execution

### Sans InfluxDB
```
export LIST=./sources/list.yml
python3 check_ssl.py
```

### Avec InfluxDB
```
export LIST=./sources/list.yml
export INFLUXDB-HOST=http://localhost:8086
export INFLUXDB-BUCKET=bucket
export INFLUXDB-TOKEN=token
export INFLUXDB-ORG=org
```

## Docker
```
docker-compose build --no-cache && docker-compose up -d
```

# License

![Apache 2.0 Licence](https://img.shields.io/hexpm/l/plug.svg)

This project is licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license - see the [LICENSE](LICENSE) file for details.

# Author Information
This role was created in 21/12/2018 by [PG3](https://pg3.io)\
Maintained in 05/07/2021 by [PG3](https://pg3.io)\
