import PyInstaller.__main__
import os
import subprocess
import shutil


current_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_dir)

package_name = "my-tube"
package_version = "1.0.0"
maintainer = "RomeoManoela romeomanoela18@gmail.com"
architecture = "amd64"
description = "Une application de desktop pour télécharger des vidéos YouTube"

PyInstaller.__main__.run([
    'main.py',
    '--name=my-tube',
    '--windowed',
    '--onefile',
    '--icon=youtube.png',
    '--clean',
])

try:

    deb_root = os.path.join(current_dir, f"{package_name}_{package_version}")
    if os.path.exists(deb_root):
        shutil.rmtree(deb_root)

    os.makedirs(os.path.join(deb_root, "usr/bin"))
    os.makedirs(os.path.join(deb_root, "usr/share/applications"))
    os.makedirs(os.path.join(deb_root, "usr/share/icons/hicolor/256x256/apps"))
    os.makedirs(os.path.join(deb_root, "DEBIAN"))

    shutil.copy(
        os.path.join(current_dir, "dist/my-tube"),
        os.path.join(deb_root, "usr/bin/my-tube")
    )
    os.chmod(os.path.join(deb_root, "usr/bin/my-tube"), 0o755)

    shutil.copy(
        os.path.join(current_dir, "youtube.png"),
        os.path.join(deb_root, "usr/share/icons/hicolor/256x256/apps/my-tube.png")
    )

    with open(os.path.join(deb_root, "usr/share/applications/my-tube.desktop"), "w") as f:
        f.write("""[Desktop Entry]
Name=MyTube
Exec=/usr/bin/my-tube
Icon=my-tube
Type=Application
Categories=Utility;AudioVideo;
Comment=Téléchargeur de vidéos YouTube
""")

    installed_size = sum(os.path.getsize(os.path.join(root, file)) 
                         for root, _, files in os.walk(deb_root) 
                         for file in files) // 1024
    
    with open(os.path.join(deb_root, "DEBIAN/control"), "w") as f:
        f.write(f"""Package: {package_name}
Version: {package_version}
Section: utils
Priority: optional
Architecture: {architecture}
Installed-Size: {installed_size}
Maintainer: {maintainer}
Description: {description}
 Une application de bureau qui permet de télécharger des vidéos YouTube
 dans différents formats et qualités.
""")

    subprocess.run(["dpkg-deb", "--build", deb_root])
    print(f"Paquet Debian créé avec succès: {deb_root}.deb")

except Exception as e:
    print(f"Erreur lors de la création du paquet Debian: {e}")
    print("L'exécutable standard a été créé dans le dossier 'dist'")