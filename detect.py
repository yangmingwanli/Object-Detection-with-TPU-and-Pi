# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo which runs object detection on camera frames.

export TEST_DATA=/usr/lib/python3/dist-packages/edgetpu/test_data

Run face detection model:
python3 -m edgetpuvision.detect \
  --model ${TEST_DATA}/mobilenet_ssd_v2_face_quant_postprocess_edgetpu.tflite

Run coco model:
python3 -m edgetpuvision.detect \
  --model ${TEST_DATA}/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite \
  --labels ${TEST_DATA}/coco_labels.txt
"""
import argparse
import time
import re
import svgwrite
import imp
import os
from edgetpu.detection.engine import DetectionEngine
import gstreamer

def load_labels(path):
    p = re.compile(r'\s*(\d+)(.+)')
    with open(path, 'r', encoding='utf-8') as f:
       lines = (p.match(line).groups() for line in f.readlines())
       return {int(num): text.strip() for num, text in lines}

def shadow_text(dwg, x, y, text, font_size=20):
    dwg.add(dwg.text(text, insert=(x+1, y+1), fill='black', font_size=font_size))
    dwg.add(dwg.text(text, insert=(x, y), fill='white', font_size=font_size))

def generate_svg(dwg, objs, labels, text_lines):
    width, height = dwg.attribs['width'], dwg.attribs['height']
    for y, line in enumerate(text_lines):
        shadow_text(dwg, 10, y*20, line)
    for obj in objs:
        x0, y0, x1, y1 = obj.bounding_box.flatten().tolist()
        x, y, w, h = x0, y0, x1 - x0, y1 - y0
        x, y, w, h = int(x * width), int(y * height), int(w * width), int(h * height)
        percent = int(100 * obj.score)
        label = '%d%% %s' % (percent, labels[obj.label_id])
        shadow_text(dwg, x, y - 5, label)
        cx, cy = x + w//2, y + h//2
        # warninig if it's centered
        if abs(cx - width//2) < 50 and abs(cy - height//2) < 50:
            shadow_text(dwg, cx, cy, 'WARNING')
            # make a alarm sound, but slow down detection fps
            # os.system('aplay /home/pi/Horn2.wav')
        dwg.add(dwg.rect(insert=(x,y), size=(w, h),
                        fill='red', fill_opacity=0.3, stroke='white'))
        
def iou(box1, box2):
    # get intersaction 
    xi1 = max(box1[0],box2[0])
    yi1 = max(box1[1],box2[1])
    xi2 = min(box1[2],box2[2])
    yi2 = min(box1[3],box2[3])
    inter_area = max(xi2-xi1,0)*max(yi2-yi1,0)
    box1_area = (box1[2]-box1[0])*(box1[3]-box1[1])
    box2_area = (box2[2]-box2[0])*(box2[3]-box2[1])
    union_area = box1_area + box2_area - inter_area
    iou = inter_area/union_area
    return iou

def main():
    default_model_dir = '../all_models'
    default_model = 'mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite'
    default_labels = 'coco_labels.txt'
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', help='.tflite model path',
                        default=os.path.join(default_model_dir,default_model))
    parser.add_argument('--labels', help='label file path',
                        default=os.path.join(default_model_dir, default_labels))
    parser.add_argument('--top_k', type=int, default=10,
                        help='number of classes with highest score to display')
    parser.add_argument('--threshold', type=float, default=0.3,
                        help='class score threshold')
    args = parser.parse_args()

    print("Loading %s with %s labels."%(args.model, args.labels))
    engine = DetectionEngine(args.model)
    labels = load_labels(args.labels)

    last_time = time.monotonic()
    def user_callback(image, svg_canvas):
      nonlocal last_time
      start_time = time.monotonic()
      objs = engine.DetectWithImage(image, threshold=args.threshold,
                                    keep_aspect_ratio=True, relative_coord=True,
                                    top_k=args.top_k)
      end_time = time.monotonic()
      text_lines = [
          'Inference: %.2f ms' %((end_time - start_time) * 1000),
          'FPS: %.2f fps' %(1.0/(end_time - last_time)),
      ]
      print(' '.join(text_lines))
      last_time = end_time
      
      # keep only relevant classes, e.g. person, car, truck, train, stop sign, traffic lights, etc.
      objs = [obj for obj in objs if obj.label_id in [0,1,2,3,5,6,7,9,12]]
      # non max suppression
      objs.sort(key=lambda x: x.score)
      keep = []
      while objs:
          max_score_obj = objs.pop()
          keep.append(max_score_obj)
          tmp = []
          for obj in objs:
              if iou(obj.bounding_box.flatten().tolist(),max_score_obj.bounding_box.flatten().tolist()) < 0.1:
                  tmp.append(obj)
          objs = tmp
          
      generate_svg(svg_canvas, keep, labels, text_lines)

    result = gstreamer.run_pipeline(user_callback)

if __name__ == '__main__':
    main()
