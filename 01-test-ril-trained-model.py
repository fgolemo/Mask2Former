import os.path

import matplotlib.pyplot as plt
from detectron2.utils.logger import setup_logger
from tqdm import trange

setup_logger()
setup_logger(name="mask2former")
import numpy as np
import cv2
import torch

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data import MetadataCatalog
from detectron2.projects.deeplab import add_deeplab_config

# import Mask2Former project
from mask2former import (
    add_maskformer2_config,
)


ril_metadata = MetadataCatalog.get("rilv7")


cfg = get_cfg()
add_deeplab_config(cfg)
add_maskformer2_config(cfg)
cfg.merge_from_file("configs/ril/panoptic-segmentation/maskformer2_R50_bs16_50ep.yaml")
cfg.MODEL.WEIGHTS = "output/model_final.pth"
cfg.MODEL.MASK_FORMER.TEST.SEMANTIC_ON = False
cfg.MODEL.MASK_FORMER.TEST.INSTANCE_ON = False
cfg.MODEL.MASK_FORMER.TEST.PANOPTIC_ON = True
predictor = DefaultPredictor(cfg)


def eval_on_img(img):
    outputs = predictor(im)
    v = Visualizer(im[:, :, ::-1], ril_metadata, scale=1.2, instance_mode=ColorMode.IMAGE_BW)
    panoptic_result = v.draw_panoptic_seg(outputs["panoptic_seg"][0].to("cpu"), outputs["panoptic_seg"][1]).get_image()
    return panoptic_result


for IMG in trange(10):
    img_name = str(IMG + 1).zfill(5)

    im = cv2.imread(os.path.expanduser(f"~/dev/ril-digitaltwin/scripts/imgs/512/generatorv7/{img_name}.png"))
    panoptic_result = eval_on_img(im)
    cv2.imwrite(f"output/pred-{img_name}.png", panoptic_result[:, :, ::-1])

for i in range(2):
    im = cv2.imread(f"real-test-{i+1}.jpg")
    panoptic_result = eval_on_img(im)
    cv2.imwrite(f"output/pred-real-{i+1}.jpg", panoptic_result[:, :, ::-1])

print("done")