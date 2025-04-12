# my-tube

Une application de desktop moderne et intuitive pour télécharger des vidéos YouTube dans différents formats et qualités.

## Fonctionnalités

- Interface graphique
- Récupération des informations détaillées des vidéos YouTube
- Affichage de la miniature, du titre, de la durée et du nom de la chaîne
- Liste complète des formats disponibles avec leurs caractéristiques (résolution, FPS, taille)
- Téléchargement rapide dans le format sélectionné
- Barre de progression en temps réel avec informations de vitesse et temps restant
- Sélection personnalisée du dossier de destination

## Installation manuelle (ubuntu/debian)

1. Téléchargez le fichier .deb depuis la [page des releases](https://github.com/RomeoManoela/my-tube/releases/tag/Youtube)
2. Installez-le avec la commande:
   ```
   sudo dpkg -i my-tube_1.0.0.deb
   sudo apt-get install -f  # Pour résoudre les dépendances manquantes (optionel)
   ```

## Désinstallation

Pour désinstaller my-tube de votre système, utilisez l'une des méthodes suivantes:

### Via la ligne de commande
```
sudo apt remove my-tube
```
ou
```
sudo dpkg -r my-tube
```

### Via un gestionnaire de paquets graphique
Vous pouvez également utiliser un gestionnaire de paquets graphique comme Synaptic ou le Centre de logiciels Ubuntu:
1. Recherchez "my-tube"
2. Sélectionnez le paquet
3. Cliquez sur "Supprimer" ou "Désinstaller"


## Utilisation

LanCez l'application :

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
