# my-tube

Une application de desktop moderne et intuitive pour télécharger des vidéos YouTube dans différents formats et qualités.

## Fonctionnalités

- Interface graphique moderne et conviviale
- Récupération des informations détaillées des vidéos YouTube
- Affichage de la miniature, du titre, de la durée et du nom de la chaîne
- Liste complète des formats disponibles avec leurs caractéristiques (résolution, FPS, taille)
- Téléchargement rapide dans le format sélectionné
- Barre de progression en temps réel avec informations de vitesse et temps restant
- Sélection personnalisée du dossier de destination

## Prérequis

- Python 3.6 ou supérieur
- Bibliothèques requises (voir section Installation)

## Installation

1. Clonez ce dépôt :
   ```
   git clone https://github.com/RomeoManoela/my-tube.git
   
   cd my-tube
   
   python -m venv venv
   
   pip install -r requirements.txt
   ```

## Utilisation

Lancez l'application :
```
python main.py
```

1. Collez l'URL d'une vidéo YouTube dans le champ prévu
2. Cliquez sur "Récupérer" pour obtenir les informations et formats disponibles
3. Sélectionnez le format souhaité dans la liste
4. (Optionnel) Choisissez un dossier de destination différent
5. Cliquez sur "Télécharger" ou double-cliquez sur le format choisi
6. Attendez la fin du téléchargement

## Dépendances

- yt-dlp : Moteur de téléchargement YouTube
- tkinter : Interface graphique
- Pillow : Traitement d'images pour les miniatures
- humanize : Formatage des tailles de fichiers
- requests : Récupération des miniatures
