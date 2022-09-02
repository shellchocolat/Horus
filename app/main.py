from time import sleep
from flask import Blueprint, render_template, request
from flask_cors import CORS, cross_origin
import secrets
from picamera import PiCamera
import time
import os
import sys
import threading

main = Blueprint("main", __name__)


try:
    camera = PiCamera()
except Exception as e:
    print(str(e))
    print("Camera is not working")
    sys.exit(1)


@main.route("/", methods=["GET"])
@cross_origin()
def home():
    camera_on = camera_status()
    
    return render_template("index.html", camera_on=camera_on)

@main.route("/", methods=["POST"])
@cross_origin()
def do_camera_action():
    response = request.get_json()

    camera_state = response['camera_state'] # true, false
    camera_mode = response['camera_mode'] # picture, video, preview
    filename = response['filename']

    if camera_state == True:
        camera_on = True
    else:
        stop_recording_video()
        camera_on = False
        return render_template("index.html", camera_on=camera_on)

    if filename == "":
        filename = secrets.token_hex(nbytes=5)

    # do action about the cam here
    if camera_mode == "picture":
        take_picture("./app/static/pictures/" + filename + ".png")
        camera_on = False
    elif camera_mode == "video":
        try:
            #record_video(filename, 5*60) # 5*60 = 5 min
            x = threading.Thread(target=record_video, args=(filename, 5*60, )) # 5*60 = 5 min
            x.start()
            time.sleep(1)
        except Exception as e:
            print(str(e))
        camera_on = True 
    else:
        # code preview here 
        #try:
        #    x = threading.Thread(target=preview_video)
        #    x.start()
        #    time.sleep(1)
        #except Exception as e:
        #    print(str(e))
        camera_on = True 

    return render_template("index.html", camera_on=camera_on)

@main.route("/file", methods=["DELETE"])
@cross_origin()
def delete_file():
    try:
        response = request.get_json()
        filename = response['filename']
        print("Deleting file " + filename)
    
        if "pic-" in filename:
            filename = "./app/static/pictures/" + filename.replace("pic-", "")
            os.remove(filename + ".png")
            time.sleep(1)
        elif "vid-" in filename:
            filename = "./app/static/videos/" + filename.replace("vid-", "")
            os.remove(filename + ".png")
            os.remove(filename + ".h264")
            time.sleep(1)
        else:
            pass
    except Exception as e:
        print(str(e))

    camera_on = camera_status()
    return render_template("index.html", camera_on=camera_on)

@main.route("/file", methods=["PUT"])
@cross_origin()
def rename_file():
    try:
        response = request.get_json()
        old_filename = response['old_filename']
        new_filename = response['new_filename']
        print("Renaming file " + old_filename + " into " + new_filename)
    
        if "pic-" in old_filename:
            base = "./app/static/pictures/"
            old_filename = base + old_filename.replace("pic-", "")
            new_filename = base + new_filename
            os.rename(old_filename + ".png", new_filename + ".png")
            time.sleep(1)
        elif "vid-" in filename:
            base = "./app/static/videos/"
            old_filename = base + old_filename.replace("vid-", "")
            new_filename = base + new_filename
            os.rename(old_filename + ".h264", new_filename + ".h264") # rename the video .h264
            os.rename(old_filename + ".png", new_filename + ".png") # rename the miniature .png
            time.sleep(1)
        else:
            pass
    except Exception as e:
        print(str(e))

    camera_on = camera_status()
    return render_template("index.html", camera_on=camera_on)


@main.route("/pictures", methods=["GET"])
@cross_origin()
def list_pictures():
    print("Listing pictures")
    r = []
    for f in os.listdir("./app/static/pictures"):
        if ".png" in f:
            r.append(f.replace(".png", ""))

    camera_on = camera_status()
    return render_template("index.html", pictures=r, camera_on=camera_on)

@main.route("/videos", methods=["GET"])
@cross_origin()
def list_videos():
    print("Listing videos")
    r = []
    for f in os.listdir("./app/static/videos"):
        if ".png" in f:
            r.append(f.replace(".png", ""))

    camera_on = camera_status()
    return render_template("index.html", videos=r, camera_on=camera_on)

def camera_status():
    # if recording, return True. If not, return False
    try:
        r = camera.recording
    except:
        r = False
    return r

def record_video(filename, video_crunch):
    print("recording into " + filename)
    try:
        part = ".part-"
        part_num = 1
        rec_len = video_crunch # 5 min
        filename = "./app/static/videos/" + filename + part
        camera.capture(filename + str(part_num) + ".png")
        camera.start_recording(filename + str(part_num) + '.h264')
        camera.wait_recording(rec_len)
        while True:
            part_num += 1
            camera.capture(filename + str(part_num) + ".png")
            camera.split_recording(filename + str(part_num) + '.h264')
            camera.wait_recording(rec_len)
        camera.stop_recording()
    except Exception as e:
        print(str(e))
        return False
    return True

def stop_recording_video():
    print("stop recording")
    try:
        camera.stop_recording()
    except Exception as e:
        print(str(e))
        return False
    return True

def take_picture(filename):
    print("taking picture into " + filename)
    try:
        camera.capture(filename)
    except Exception as e:
        print(str(e))
        return False
    return True
