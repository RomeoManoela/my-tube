# Installation de MyTube

## Installation manuelle (ubuntu/debian)

1. Téléchargez le fichier .deb depuis la [page des releases](https://github.com/RomeoManoela/my-tube/releases/tag/Youtube)
2. Installez-le avec la commande:
   ```
   sudo dpkg -i my-tube_1.0.0.deb
   sudo apt-get install -f  # Pour résoudre les dépendances manquantes
   ```

## Désinstallation

Pour désinstaller MyTube de votre système, utilisez l'une des méthodes suivantes:

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
