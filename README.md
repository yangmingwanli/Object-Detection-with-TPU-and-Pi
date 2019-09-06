# Object-Detection-with-TPU-and-Pi
Detect common objects of interests for autonomous vehicle, e.g. car, person, traffic light, stop sign, etc. using Coral(Google) new TPU achieving 4 TOPS at 0.5 watts, and tiny SBC such as new Raspberry Pi 4, a perfect combo for fast deep learning inference on the move or low power.

## Demo Video
[Link to Youtube](https://www.youtube.com/watch?v=yIPw2N0GQg8)

As seen from the youtube video above, it maintains very respectable 20~30 FPS, detecting car, person, traffic light, etc. 

![Alt text](detect.png?raw=true "Title")

## Hardware Used
[Coral TPU USB accelerator](https://coral.withgoogle.com/products/accelerator/)

[Raspberry Pi 4](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/)

[Raspberry Pi camera v2](https://www.raspberrypi.org/products/camera-module-v2/)

[Raspberry Pi touch display](https://www.raspberrypi.org/products/raspberry-pi-touch-display/)

## Model Used
MobileNet V2 trained on COCO dataset and optimized for TPU inference

## What scipt does:
Detect objects of interests, warning if object is near center of image, non-maximum suppression.

## Try it out
Burn Coral [prebuilt image](https://github.com/google-coral/edgetpu-platforms#prebuilt-images-for-raspberry-pis) to Raspberry Pi 4. 

cd to examples-camera/gstreamer folder and copy over detect.py in this repo.

Connect all hardwares, get into front seat of a car.

```bash
python3 detect.py
```
