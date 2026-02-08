# -*- coding: utf-8 -*-

# Ligne 1 : declare l'encodage UTF-8 pour supporter les accents francais dans le code

VERSION = '0.0.1'
# Definit la version de notre application

from setuptools import setup, find_packages
# Importe les outils de packaging Python :
#   - setup : fonction principale pour configurer le package
#   - find_packages : detecte automatiquement les sous-dossiers Python (ceux avec __init__.py)

setup(
    name='nagareessai',
    # Nom du package tel qu'il sera enregistre dans le systeme

    version=VERSION,
    # Numero de version de l'application

    author='Julien',
    # Auteur du projet

    packages=find_packages(),
    # Trouve automatiquement le dossier 'nagareessai/' car il contient un __init__.py

    include_package_data=True,
    # Inclut les fichiers non-Python (comme les .cfg) dans le package

    package_data={'': ['*.cfg']},
    # Specifie que tous les fichiers .cfg doivent etre inclus

    zip_safe=False,
    # Empeche l'installation en archive zip (necessaire pour Nagare)

    install_requires=('nagare',),
    # Declare que l'app depend du framework Nagare

    entry_points="""
    [nagare.applications]
    nagareessai = nagareessai.app:app
    """
    # CRITICAL : c'est ici que Nagare sait ou trouver l'application
    # Format : nom_app = module.fichier:variable_factory
    # 'nagareessai.app:app' signifie :
    #   - va dans le module nagareessai/app.py
    #   - utilise la variable 'app' comme "factory" (constructeur) du composant racine
    # Nagare appelle app() pour creer une nouvelle instance de l'application a chaque session
)
