# -*- coding: utf-8 -*-

# ===========================================================================
# models.py — Modele de donnees Anime
# Utilise Elixir, une couche declarative au-dessus de SQLAlchemy
# ===========================================================================

from elixir import Entity, Field, using_options
# Entity  : classe de base pour definir une table en base de donnees
# Field   : definit une colonne de la table
# using_options : permet de configurer le comportement de l'entite (nom de table, etc.)

from sqlalchemy import Integer, String, MetaData
# Integer : type colonne pour les nombres entiers
# String  : type colonne pour les chaines de caracteres (VARCHAR en SQL)
# MetaData: objet central de SQLAlchemy qui stocke la description de toutes les tables
# SQLAlchemy = Python SQL toolkit & Mapper (C'est un ORM)

__metadata__ = MetaData()
# Cree l'objet MetaData global
# C'est cet objet que Nagare utilise (reference dans nagareessai.cfg)
# pour lier nos modeles au moteur de base de donnees au demarrage


class Anime(Entity):
    # Definit la classe Anime qui correspond a la table 'anime' en BDD
    # Entity herite de la classe de base Elixir :
    #   - cree automatiquement un champ 'id' (Integer, primary_key, auto_increment)
    #   - fournit des methodes de requete : .query, .get(), .get_by(), .delete()

    using_options(tablename='anime', auto_primarykey=False)
    # tablename='anime'       : le nom exact de la table MySQL existante
    # auto_primarykey=False   : desactive la creation auto d'un champ 'id' par Elixir
    #                           car on definit nous-meme le champ id ci-dessous
    #                           (pour correspondre exactement a la table existante)

    id = Field(Integer, primary_key=True, autoincrement=True)
    # Colonne 'id' : entier, cle primaire, auto-increment
    # Correspond a : id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY

    imagepath = Field(String(500))
    # Colonne 'imagepath' : chaine de 500 caracteres max
    # Stocke le chemin vers l'image de l'anime (ex: 'static/images/frieren.jpg')
    # Correspond a : imagepath varchar(500)

    title = Field(String(500))
    # Colonne 'title' : chaine de 500 caracteres max
    # Le titre de l'anime
    # Correspond a : title varchar(500)

    numberseason = Field(Integer)
    # Colonne 'numberseason' : entier
    # Le numero de saison
    # Correspond a : numberseason int(11)

    numberepisodes = Field(Integer)
    # Colonne 'numberepisodes' : entier
    # Le nombre d'episodes
    # Correspond a : numberepisodes int(11)

    description = Field(String(3000))
    # Colonne 'description' : chaine de 3000 caracteres max
    # La description de l'anime
    # Correspond a : description varchar(3000)
