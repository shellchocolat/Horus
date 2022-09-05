
sudo apt-get update && sudo apt-get upgrade
sudo apt-get install -y gunicorn python3-pip python3-picamera curl git vim

pip3 install -r ./requirements.txt

# set Horus as a service
service_name="horus.service"
sudo cp ./horus.service /lib/systemd/system/$service_name
sudo chmod 644 /lib/systemd/system/$service_name
sudo systemctl daemon-reload
sudo systemctl enable $service_name
sudo systemctl start $service_name
sudo systemctl status $service_name

# disable the led on the camera
sudo echo "disable_camera_led=1" >> /boot/config.txt