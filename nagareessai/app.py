# -*- coding: utf-8 -*-

# - AnimeList : affiche la liste des animes (page d'accueil)
# - AnimeApp  : composant RACINE, contient self.content et gere la navigation
# - AnimeForm : formulaire de creation / modification
#
# Flux : AnimeApp rend self.content. self.content bascule entre AnimeList et AnimeForm avec becomes()

import os
import cgi

from nagare import component, presentation, var
# component    : Component() encapsule un objet Python en composant web Nagare
# presentation : @render_for associe une vue HTML a une classe Python
# var          : Var() est un conteneur de valeur utilisable comme callback de formulaire

from nagareessai.models import Anime
# Importe notre modele Anime (Elixir Entity) pour les operations CRUD

# COMPOSANT 1 : AnimeList - Page d'accueil et liste des animes

class AnimeList(object):
    """Affiche tous les animes de la BDD avec les actions creer/modifier/supprimer
    Recoit une reference vers AnimeApp (self.app) pour pouvoir
    declencher la navigation (basculer vers le formulaire)"""

    def __init__(self, app):
        self.app = app
        # Stocke une reference vers le composant parent (AnimeApp)
        # Necessaire pour appeler app.show_form() et naviguer vers le formulaire

    def create_anime(self):
        "Demande a AnimeApp de basculer vers un formulaire vide."
        self.app.show_form(anime=None)
        # Appelle la methode de AnimeApp qui fait content.becomes(AnimeForm())

    def edit_anime(self, anime_id):
        "Demande a AnimeApp de basculer vers un formulaire pre-rempli."
        anime = Anime.get(anime_id)
        # Anime.get(id) : methode Elixir qui fait SELECT * FROM anime WHERE id = ?
        # Retourne l'objet Anime ou None si non trouve
        if anime:
            self.app.show_form(anime=anime)

    def delete_anime(self, anime_id):
        "Supprime un anime de la BDD. La page se rafraichit automatiquement."
        anime = Anime.get(anime_id)
        if anime:
            anime.delete()
            # anime.delete() : methode Elixir qui fait DELETE FROM anime WHERE id = ?
            # Nagare refresh la page automatiquement apres l'appel en BDD


# Rendu HTML de la liste des animes 
@presentation.render_for(AnimeList)
def render_anime_list(self, h, *args):
    """Genere le HTML de la page d'accueil.
        self : l'instance AnimeList
        h : renderer HTML
        *args : arguments supplementaires (Aucun dans notre cas mais bonne pratique ?)"""

    # TITRE
    h << h.h1('Mes Animes')
    # h << element : ajoute l'element au DOM courant
    # h.h1('texte') cree <h1>texte</h1>

    # BOUTON CREER
    h << h.a('+ Creer un Anime', class_='btn btn-create').action(self.create_anime)
    # h.a('texte') cree un lien <a>texte</a>
    # .action(self.create_anime) : au clic Nagare appelle la fonction self.create_anime() definit plus haut

    h << h.hr
    # <hr> : ligne de separation

    # REQUETE BDD : Get All
    animes = Anime.query.all()
    # Anime.query : objet Query Elixir/SQLAlchemy pour la table anime
    # .all() : execute SELECT * FROM anime et retourne tout les objets Anime en BDD

    if not animes:
        # SI BDD VIDE
        h << h.p('Aucun anime enregistre. Cliquez sur "Creer" pour commencer !', class_='empty-message')
    else:
        # GRILLE DE CARD D'ANIMES
        with h.div(class_='anime-grid'):

            for anime in animes:
                # Boucle sur chaque anime de la BDD. Identique a de l'Angular

                with h.div(class_='anime-card'):
                    # Creer une card pour chaque anime

                    h << h.img(src='/static/nagareessai/images/' + anime.imagepath, alt=anime.title, class_='anime-img')
                    # Image de l'anime
                    # Le chemin complet : /static/nagareessai/ + imagepath

                    h << h.h3(anime.title)
                    # Titre en <h3>

                    h << h.p('Saison : ' + str(anime.numberseason) + ' | Episodes : ' + str(anime.numberepisodes))
                    # Infos saison et episodes. Str convertit le nombre vers du texte

                    h << h.p(anime.description, class_='anime-desc')
                    # Description 

                    with h.div(class_='anime-actions'):
                        # Zone des boutons d'action Modifier et Supprimer

                        h << h.a('Modifier', class_='btn btn-edit').action(self.edit_anime, anime.id)
                        # Au clic -> self.edit_anime(anime.id)

                        h << ' '
                        # Espace entre les boutons

                        h << h.a('Supprimer', class_='btn btn-delete').action(self.delete_anime, anime.id)
                        # Au clic -> self.delete_anime(anime.id)

    return h.root


# COMPOSANT 2 : AnimeForm - Formulaire creation / modification

class AnimeForm(object):
    """Formulaire pour creer ou modifier un anime.
    Si anime=None  -> mode creation (champs vides)
    Si anime=objet -> mode edition (champs pre-remplis avec les donnees existantes)"""

    def __init__(self, anime=None):
        self.anime = anime
        # Stocke l'anime existant (ou None si creation)

        #   var.Var(valeur) cree un conteneur reactif :
        self.title = var.Var(anime.title if anime else '')
        self.imagepath = var.Var(anime.imagepath if anime else '')
        self.uploaded_filename = None  # Nom du fichier uploade (string)
        self.uploaded_data = None     # Contenu binaire du fichier (bytes)
        self.numberseason = var.Var(str(anime.numberseason) if anime else '')
        self.numberepisodes = var.Var(str(anime.numberepisodes) if anime else '')
        self.description = var.Var(anime.description if anime else '')
        # numberseason/numberepisodes convertis en str car les inputs HTML sont du texte
        self.error_message = ''

    def handle_upload(self, upload):
        # Recoit le cgi.FieldStorage du champ file, lit le contenu immediatement et stocke le nom + l'image
        if isinstance(upload, cgi.FieldStorage) and upload.filename:
            # isinstance verifie que l'image uploader soit du bon type et verifie egalement que celui ci a bien un filename qui n'est pas vide
            self.uploaded_filename = os.path.basename(upload.filename)
            self.uploaded_data = upload.file.read()

    def validate_and_save(self, comp):
        # Valide les champs, sauvegarde en BDD, et retourne a la liste.
        # comp: le Component qui encapsule le formulaire.

        # Recupere les valeurs actuelles des Var
        title = self.title()
        numberseason = self.numberseason()
        numberepisodes = self.numberepisodes()
        description = self.description()

        # Traitement de l'image
        if self.uploaded_data:
            # Nouveau fichier uploader : on le sauvegarde dans static/images/
            destination = os.path.join('static', 'images', self.uploaded_filename)
            with open(destination, 'wb') as file:
                file.write(self.uploaded_data)
            imagepath = self.uploaded_filename
        elif self.anime:
            # Mode modification sans nouveau fichier d'image : on garde l'iamge deja existante
            imagepath = self.anime.imagepath
        else:
            imagepath = ''

        # VALIDATION : champs obligatoires
        if not title or not imagepath or not numberseason or not numberepisodes or not description:
            self.error_message = 'Tous les champs sont obligatoires !'
            return

        # VALIDATION : nombres entiers
        try:
            numberseason = int(numberseason)
            numberepisodes = int(numberepisodes)
        except ValueError:
            self.error_message = 'Saison et episodes doivent etre des nombres entiers !'
            return

        if self.anime:
            # UPDATE : modifie l'anime existant
            self.anime.title = title
            self.anime.imagepath = imagepath
            self.anime.numberseason = numberseason
            self.anime.numberepisodes = numberepisodes
            self.anime.description = description
            # Modifier les attributs d'un objet Elixir = UPDATE en BDD
        else:
            # INSERT : cree un nouvel anime
            Anime(
                title=title,
                imagepath=imagepath,
                numberseason=numberseason,
                numberepisodes=numberepisodes,
                description=description
            )
            # Instancier un Entity Elixir = INSERT INTO anime(...)

        comp.answer()
        # comp.answer() declenche le callback on_answer() enregistre par AnimeApp

    def cancel(self, comp):
        # Annule et retourne a la liste sans sauvegarder
        comp.answer()


# Rendu HTML du formulaire
@presentation.render_for(AnimeForm)
def render_anime_form(self, h, comp, *args):
    #Genere le HTML du formulaire de creation/edition

    # TITRE
    h << h.h1('Modifier un Anime' if self.anime else 'Creer un Anime')

    # ERREUR (si validation echouee)
    if self.error_message:
        h << h.div(self.error_message, class_='error')

    # FORMULAIRE
    with h.form:
        # h.form cree <form method="POST">
        # Nagare gere l'action et le routage des callbacks automatiquement

        # Champ Titre
        h << h.label('Titre :', for_='title')
        h << h.input(type='text', id='title', value=self.title()).action(self.title)
        # value=self.title() : valeur actuelle du Var (remplie ou vide)
        h << h.br

        # Champ Image (upload)
        h << h.label('Image :', for_='imagepath')
        if self.anime and self.anime.imagepath:
            # En mode modification on verifie qu'une image existe et son path. Si oui on affiche le path actuel
            h << h.p('Image actuelle : ' + self.anime.imagepath, class_='current-image')
        h << h.input(type='file', id='imagepath', class_='file-hidden').action(self.handle_upload)
        h << h.label('Importer Image', for_='imagepath', class_='btn btn-save btn-file')
        h << h.br

        # Champ Numero de saison
        h << h.label('Numero de saison :', for_='numberseason')
        h << h.input(type='text', id='numberseason', value=self.numberseason()).action(self.numberseason)
        h << h.br

        # Champ Nombre d'episodes
        h << h.label("Nombre d'episodes :", for_='numberepisodes')
        h << h.input(type='text', id='numberepisodes', value=self.numberepisodes()).action(self.numberepisodes)
        h << h.br

        # Champ Description
        h << h.label('Description :', for_='description')
        with h.textarea(id='description', rows='5', cols='50').action(self.description):
            h << self.description()
        # textarea avec .action() fonctionne comme input : Nagare passe le contenu au Var
        h << h.br

        # Bouton Valider
        h << h.input(type='submit', value='Valider', class_='btn btn-save').action(self.validate_and_save, comp)
        # .action(self.validate_and_save, comp) :
        # au clic sur Valider  Nagare appelle self.validate_and_save

        h << ' '

        # Bouton Annuler
        h << h.input(type='submit', value='Annuler', class_='btn btn-cancel').action(self.cancel, comp)

    return h.root

# COMPOSANT 3 : AnimeApp — Composant RACINE (navigateur)

class AnimeApp(object):
    """Composant racine de l'application.

    Contient self.content : Le Component Nagare qui bascule entre AnimeList (page d'accueil) et AnimeForm (formulaire).

    C'est le SEUL composant rendu par Nagare. Son render affiche self.content,
    qui lui-meme rend soit AnimeList soit AnimeForm selon l'etat de navigation."""

    def __init__(self):
        self.content = component.Component(AnimeList(self))
        # Cree un Component Nagare contenant un AnimeList
        # AnimeList recoit 'self' (AnimeApp) pour pouvoir naviguer
        # Au depart, l'application affiche la liste des animes

    def show_form(self, anime=None):
        #Bascule self.content vers le formulaire
        
        self.content.becomes(AnimeForm(anime))
        # Avant : self.content rendait AnimeList
        # Apres : self.content rend AnimeForm

        self.content.on_answer(self.show_list)
        # on_answer(callback) : quand AnimeForm fait comp.answer(),

    def show_list(self, answer=None):
        # Retourne self.content vers la liste des animes
        
        self.content.becomes(AnimeList(self))
        # Remplace le formulaire par une nouvelle instance d'AnimeList
        # La page d'accueil se re-affiche avec les donnees a jour


# Racine : rend self.content dans un container
@presentation.render_for(AnimeApp)
def render_anime_app(self, h, *args):
    # Rendu du composant racine. C'est self.content qui decide QUOI afficher

    # Charge le CSS dans le header
    h.head.css_url('css/style.css')

    with h.div(class_='container'):
        h << self.content
    return h.root


app = AnimeApp
# Nagare appelle app() = AnimeApp() pour creer le composant racine a chaque nouvelle session utilisateur
