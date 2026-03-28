# Capra Rove VTX Streamer

## Configuration pour le démarrage automatique

1. Passez le Raspberry Pi en mode headless :
   ```bash
   sudo systemctl disable lightdm
   ```

2. Créez le fichier de service systemd :
   ```bash
   sudo nano /etc/systemd/system/cam_manager.service
   ```
   Collez le contenu du fichier `cam_manager.service` dans ce fichier.

3. Modifiez les permissions du fichier :
   ```bash
   sudo chmod 644 /etc/systemd/system/cam_manager.service
   ```

4. Rechargez systemd et activez le service :
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable cam_manager.service
   ```

5. Vérifiez le statut du service :
   ```bash
   sudo systemctl status cam_manager
   ```

## Utilisation

### Configuration des caméras
Pour ajouter des caméras virtuelles, modifiez le fichier `config.yaml` :
- Donnez un identifiant à chaque caméra (utilisé pour le changement de flux)
- Indiquez l'adresse du flux RTSP de chaque caméra

### Changement de caméra en cours d'exécution
Pour basculer vers une autre caméra pendant le fonctionnement :
1. Envoyez l'identifiant de la caméra via UDP
2. Par défaut, la première caméra de la liste est utilisée
3. Exemple avec netcat :
   ```bash
   echo [id] | nc -u [ip] [port]
   ```

## Idee principale

### Arrêt du bureau (mode headless)
1. Arrêtez le bureau graphique :
   ```bash
   sudo systemctl stop lightdm
   ```

### Redirection du flux vidéo vers HDMI
Pour rediriger le flux vidéo depuis le RTSP vers le port HDMI :
```bash
gst-launch-1.0 \
  rtspsrc location=rtsp://192.168.2.30:554/ \
  latency=0 protocols=tcp drop-on-latency=true is-live=true \
  ! application/x-rtp,media=video,encoding-name=H265 \
  ! rtph265depay \
  ! h265parse config-interval=-1 \
  ! avdec_h265 \
  ! videoconvert \
  ! queue max-size-buffers=1 leaky=downstream \
  ! kmssink sync=false
```
