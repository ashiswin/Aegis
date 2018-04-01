import os
import sys
import cv2
import time
import numpy as np

sys.path.append(os.path.dirname(__file__) + "/../")

from scipy.misc import imread

from config import load_config
from nnet import predict
from util import visualize
from dataset.pose_dataset import data_to_input
cfg = load_config("demo/pose_cfg.yaml")

# Load and setup CNN part detector
sess, inputs, outputs = predict.setup_pose_prediction(cfg)

camera = cv2.VideoCapture(0)
# Read image from file
file_name = "demo/obama.jpeg"

dataFile = open('noaction-1.txt', 'w')

while True:
	r, image = camera.read()
	
	image_batch = data_to_input(image)

	# Compute prediction with the CNN
	outputs_np = sess.run(outputs, feed_dict={inputs: image_batch})
	scmap, locref, _ = predict.extract_cnn_output(outputs_np, cfg)

	# Extract maximum scoring location from the heatmap, assume 1 person
	pose = predict.argmax_pose_predict(scmap, locref, cfg.stride)

	# Visualise
	data = visualize.visualize_joints(image, pose)
	cv2.imshow('image', data)
	cv2.waitKey(1)
	
	arr = []
	for i in range(14):
		arr += pose[i].tolist()[0:2]
	
	dataFile.write(str(arr) + "\n")
	print(str(arr))
visualize.waitforbuttonpress()
