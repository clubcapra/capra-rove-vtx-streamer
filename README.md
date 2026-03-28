## Procedure

- 1. stop le desktop : `sudo systemctl stop lightdm`
- 2. pour rediriger le flux video sur le HDMI
  ```bash
  gst-launch-1.0   rtspsrc location=rtsp://192.168.2.30:554/     latency=0 protocols=tcp drop-on-latency=true is-live=true   ! application/x-rtp,media=video,encoding-name=H265   ! rtph265depay   ! h265parse config-interval=-1   ! avdec_h265   ! videoconvert   ! queue max-size-buffers=1 leaky=downstream   ! kmssink sync=false
  ```

## TODO

- [x] switch les cam depuis un endpoint udp
- [ ] relancer la commande depuis endpoint
- [ ] lancer la commande au démarage du pi

## Config

```yaml
cameras:
  - id: "0"
    ip: "192.168.2.30"
    port: 554
    stream_url: "rtsp://192.168.2.30:554"
    active: true
  - id: "4"
    ip: "192.168.2.34"
    port: 554
    stream_url: "rtsp://192.168.2.34:554"
    active: false
hooks:
  udp:
    port: 5540
    
```
