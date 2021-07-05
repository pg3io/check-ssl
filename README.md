# Check SSL - Python

![langage](https://img.shields.io/badge/Langage-Python-green.svg) 
![version](https://img.shields.io/badge/version-Beta-purple.svg)
[![Twitter](https://img.shields.io/twitter/follow/pg3io.svg?style=social)](https://twitter.com/intent/follow?screen_name=pg3io)

Vérifie l'expiration d'un certificat SSL pour des urls donnés

## Input

Lister vos urls dans un fichier "yml"

## Output

```
{'url': <URL>, 'expiration': <ssl_expiration_timestamp>, 'dns': [<DNS>]}
```

## Execution

```
export LIST=./sources/list.yml
python3 check_ssl.py
```

## Docker
```
docker build -t pg3io/ssl:0.1 . --no-cache
docker run -d -e LIST=/sources/list.yml --name checkSSL pg3io/ssl:0.1
```

ou simplement en récupérant l'image sur notre registry

```
docker run -d -e LIST=/sources/list.yml --name checkSSL registry.pg3.io:5000/pg3io/ssl:0.1
```

# License

![Apache 2.0 Licence](https://img.shields.io/hexpm/l/plug.svg)

This project is licensed under the [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license - see the [LICENSE](LICENSE) file for details.

# Author Information
This role was created in 21/12/2018 by [PG3](https://pg3.io)\
Maintained in 05/07/2021 by [PG3](https://pg3.io)\