import tensorflow as tf
import ast
import threading
import sys

learning_rate = 0.1
num_steps = 2000
batch_size = 128
display_step = 100

workout = open(sys.argv[1] + "workout.txt")
values = dict()

for l in workout:
	arr = l.split(" ")
	values[arr[0]] = arr[1]

# Network Parameters
n_hidden_1 = 84 # 1st layer number of neurons
n_hidden_2 = 42 # 2nd layer number of neurons
num_input = 28 # MNIST data input (img shape: 28*28)
num_classes = int(values["classes"]) # MNIST total classes (0-9 digits)

trainingDataX = []
trainingDataY = []

for i in range(int(values["classes"])):
	onehot = [0] * int(values["classes"])
	onehot[i] = 1
	
	fileT = open(sys.argv[1] + values[str(i)].strip('\n'), 'r')
	for l in fileT:
		trainingDataX.append(ast.literal_eval(l))
		trainingDataY.append(onehot)

X = tf.placeholder("float", [None, num_input])
Y = tf.placeholder("float", [None, num_classes])

weights = {
    'h1': tf.Variable(tf.random_normal([num_input, n_hidden_1])),
    'h2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2])),
    'out': tf.Variable(tf.random_normal([n_hidden_2, num_classes]))
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1])),
    'b2': tf.Variable(tf.random_normal([n_hidden_2])),
    'out': tf.Variable(tf.random_normal([num_classes]))
}

# Create model
def neural_net(x):
    # Hidden fully connected layer with 256 neurons
    layer_1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
    # Hidden fully connected layer with 256 neurons
    layer_2 = tf.add(tf.matmul(layer_1, weights['h2']), biases['b2'])
    # Output fully connected layer with a neuron for each class
    out_layer = tf.matmul(layer_2, weights['out']) + biases['out']
    return out_layer

# Construct model
logits = neural_net(X)
prediction = tf.nn.softmax(logits)

# Define loss and optimizer
loss_op = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
    logits=logits, labels=Y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
train_op = optimizer.minimize(loss_op)

# Evaluate model
correct_pred = tf.equal(tf.argmax(prediction, 1), tf.argmax(Y, 1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initialize the variables (i.e. assign their default value)
init = tf.global_variables_initializer()

saver = tf.train.Saver(tf.trainable_variables())

# Start training
sess = tf.Session()

# Run the initializer
sess.run(init)

for step in range(1, num_steps+1):
	batch_x, batch_y = trainingDataX, trainingDataY
	# Run optimization op (backprop)
	sess.run(train_op, feed_dict={X: batch_x, Y: batch_y})
	if step % display_step == 0 or step == 1:
	    # Calculate batch loss and accuracy
	    loss, acc = sess.run([loss_op, accuracy], feed_dict={X: batch_x,
				                                 Y: batch_y})
	    print("Step " + str(step) + ", Minibatch Loss= " + \
		  "{:.4f}".format(loss) + ", Training Accuracy= " + \
		  "{:.3f}".format(acc))

print("Optimization Finished!")
saver.save(sess, sys.argv[1] + "predictor_model")

state = "init"
points = 0

def processPose(p):
	global state
	global points

	position = -1
	for i in range(len(p[0])):
		if p[0][i] == 1.0:
			position = i
			break
	if position == int(values["startact"]) and state == "init":
		state = "acted"
	elif position == int(values["endact"]) and state == "acted":
		state = "completed"
	elif position == int(values["startact"]) and state == "completed":
		state = "init"
		points += 1

def poser():
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
	sess2, inputs, outputs = predict.setup_pose_prediction(cfg)

	camera = cv2.VideoCapture(0)
	# Read image from file
	
	prevPoints = -1

	while True:
		r, image = camera.read()
		
		image_batch = data_to_input(image)

		# Compute prediction with the CNN
		outputs_np = sess2.run(outputs, feed_dict={inputs: image_batch})
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
		
		predictedPose = sess.run(prediction, feed_dict={X: [arr]})
		processPose(predictedPose)
		
		if prevPoints != points:
			print("Current points: " + str(points))
			prevPoints = points
t = threading.Thread(target=poser).start()
t.join()
