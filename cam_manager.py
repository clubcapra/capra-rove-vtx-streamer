import yaml
import subprocess
import socket
import threading
import time
import signal
import sys

class CameraManager:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.current_cam = None
        self.process = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(('0.0.0.0', self.config['hooks']['udp']['port']))
        self.running = True

    def start_camera_stream(self, cam_id):
        cam = next((c for c in self.config['cameras'] if c['id'] == cam_id), None)
        if not cam:
            print(f"Camera {cam_id} not found in config.")
            return

        cmd = [
            'gst-launch-1.0',
            'rtspsrc', 'location=' + cam['stream_url'], 'latency=0',
            'protocols=tcp', 'drop-on-latency=true', 'is-live=true',
            '!',
            'application/x-rtp,media=video,encoding-name=H265',
            '!',
            'rtph265depay',
            '!',
            'h265parse', 'config-interval=-1',
            '!',
            'avdec_h265',
            '!',
            'videoconvert',
            '!',
            'queue', 'max-size-buffers=1', 'leaky=downstream',
            '!',
            'kmssink', 'sync=false'
        ]

        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.current_cam = cam_id
        print(f"Started stream for camera: {cam_id}")

    def switch_camera(self, cam_id):
        if self.process:
            self.process.terminate()
        self.start_camera_stream(cam_id)

    def listen_udp(self):
        while self.running:
            data, _ = self.udp_socket.recvfrom(1)
            new_cam = data.decode()
            self.switch_camera(new_cam)

    def monitor_process(self):
        while self.running:
            if self.process and self.process.poll() is not None:
                print("Process crashed, restarting...")
                self.start_camera_stream(self.current_cam)
            time.sleep(5)

    def run(self):
        self.start_camera_stream(self.config['cameras'][0]['id'])
        udp_thread = threading.Thread(target=self.listen_udp)
        monitor_thread = threading.Thread(target=self.monitor_process)
        udp_thread.start()
        monitor_thread.start()
        udp_thread.join()
        monitor_thread.join()

    def stop(self):
        self.running = False
        if self.process:
            self.process.terminate()
        self.udp_socket.close()

def signal_handler(sig, frame):
    print('Shutting down...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    manager = CameraManager('config.yaml')
    manager.run()
