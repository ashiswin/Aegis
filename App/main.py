import sys
import time
import mainwindow_rc
import routineselectwindow_rc
import routineselectwindow_new_rc
import routinecompletewindow_rc
import accountswindow_rc
import homewindow_rc
from time import sleep
from subprocess import call
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QMessageBox, QProgressDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from urllib import request, parse

state = "init"
points = 0
reps = 5

videoPlaying = True

class LoginThread(QtCore.QThread):
	success = QtCore.pyqtSignal()
	error = QtCore.pyqtSignal(object)

	def __init__(self, NRIC, password, parentQWidget = None, ):
		super(LoginThread, self).__init__(parentQWidget)
		self.NRIC = NRIC
		self.password = password

	def run(self):
		# TODO: Check if login credentials are valid
		self.success.emit()

class ResultSubmitThread(QtCore.QThread):
	success = QtCore.pyqtSignal()
	error = QtCore.pyqtSignal(object)

	def __init__(self, userId, workoutId, routineId, score, parentQWidget = None, ):
		super(ResultSubmitThread, self).__init__(parentQWidget)
		self.userId = userId
		self.workoutId = workoutId
		self.routineId = routineId
		self.score = score
		
	def run(self):
		d = dict()
		d["name"] = "Best Workout"
		d["userId"] = self.userId
		d["workoutId"] = self.workoutId
		d["routineId"] = self.routineId
		d["score"] = self.score
		
		data = parse.urlencode(d).encode()
		req =  request.Request("http://10.0.5.222:1337/api/result/create?name=BestWorkout&userId=" + str(self.userId) + "&workoutId=" + str(self.workoutId) + "&routineId=" + str(self.routineId) + "&score=" + str(self.score), data=data) # this will make the method "POST"
		resp = request.urlopen(req)
		
		self.success.emit()
	
class VideoThread(QtCore.QThread):
	pointUpdate = QtCore.pyqtSignal(object)
	videoReady = QtCore.pyqtSignal()
	
	def __init__(self, label, workout, parentQWidget = None, ):
		global state
		global points
		global reps
		
		super(VideoThread, self).__init__(parentQWidget)
		self.lblVideo = label
		self.workout = workout
		self.running = True
		
		state = "init"
		points = 0
		reps = 5
		
	def run(self):
		import tensorflow as tf
		import ast
		import threading
		import sys
		
		learning_rate = 0.1
		num_steps = 2000
		batch_size = 128
		display_step = 100

		workout = open(self.workout + "workout.txt")
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
			
			fileT = open(self.workout + values[str(i)].strip('\n'), 'r')
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
		saver.save(sess, self.workout + "predictor_model")
		#self.videoReady.emit()
		
		while videoPlaying:
			time.sleep(0.5)
		
		print("yey")
		def processPose(p):
			global state
			global points
			global reps
			
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
				reps -= 1
				self.pointUpdate.emit(points)

		def poser():
			global state
			global points
			global reps
			
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

			while self.running:
				r, image = camera.read()
				
				image_batch = data_to_input(image)

				# Compute prediction with the CNN
				outputs_np = sess2.run(outputs, feed_dict={inputs: image_batch})
				scmap, locref, _ = predict.extract_cnn_output(outputs_np, cfg)

				# Extract maximum scoring location from the heatmap, assume 1 person
				pose = predict.argmax_pose_predict(scmap, locref, cfg.stride)

				# Visualise
				data = visualize.visualize_joints(image, pose)
				frame = cv2.cvtColor(data, 4)
				img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
				pix = QtGui.QPixmap.fromImage(img)
				try:
					self.lblVideo.setPixmap(pix)
				except:
					return
				
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
	def quit(self):
		self.running = False

class VideoWindow(QMainWindow):
	quitSignal = QtCore.pyqtSignal()
	completeSignal = QtCore.pyqtSignal()
	
	def __init__(self, workout):
		super(VideoWindow, self).__init__()
		uic.loadUi('ui/videowindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		videoThread = VideoThread(self.lblVideo, workout, self)
		videoThread.pointUpdate.connect(self.pointUpdate)
		self.quitSignal.connect(videoThread.quit)
		videoThread.videoReady.connect(self.videoReady)
		videoThread.start()
		
		movie = QtGui.QMovie(workout + "instructions.gif")
		self.lblVideo.setMovie(movie)
		movie.finished.connect(self.finishedPlaying)
		movie.start()
		self.movie = movie
		QtCore.QTimer.singleShot(10000, self.finishedPlaying)
		self.btnDone.clicked.connect(self.done)
		self.lblReps.setText(str(reps))
		
	def pointUpdate(self, points):
		self.lblPoints.setText(str(points))
		self.lblReps.setText(str(reps))
		
		if(reps == 0):
			self.completeSignal.emit()
			self.done()
	def done(self):
		global routineViewWindow
		
		self.quitSignal.emit()
		#routineViewWindow.showFullScreen()
		self.hide()
	
	def videoReady(self):
		self.progress.hide()
	
	def finishedPlaying(self):
		global videoPlaying
		print("Video done")
		self.movie.stop()
		self.lblVideo.setMovie(None)
		videoPlaying = False

class RoutineCompleteWindow(QMainWindow):
	def __init__(self, workoutType):
		super(RoutineCompleteWindow, self).__init__()
		uic.loadUi('ui/strengthcompletewindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		self.show()
		self.btnBack.clicked.connect(self.back)
	
	def back(self):
		global routineSelectWindow
		routineSelectWindow.showFullScreen()
		self.hide()
	

class HomeWindow(QMainWindow):
	def __init__(self):
		super(HomeWindow, self).__init__()
		uic.loadUi('ui/homewindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		#self.btnLogout.clicked.connect(self.logout)
		self.btnExercise.clicked.connect(self.exercise)
		self.btnRewards.clicked.connect(self.rewards)
		self.btnAccount.clicked.connect(self.account)
		
	def exercise(self):
		global routineSelectWindow
		routineSelectWindow = RoutineSelectWindow()
		routineSelectWindow.showFullScreen()
		self.hide()

	def rewards(self):
		global rewardsWindow
		rewardsWindow = RewardsWindow()
		rewardsWindow.showFullScreen()
		self.hide()

	def account(self):
		global accountsWindow
		accountsWindow = AccountsWindow()
		accountsWindow.showFullScreen()
		self.hide()

class RewardsWindow(QMainWindow):
	def __init__(self):
		super(RewardsWindow, self).__init__()
		uic.loadUi('ui/rewardswindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		self.btnHome.clicked.connect(self.home)
		#self.btnStrength.clicked.connect(self.strength)
		#self.btnBalance.clicked.connect(self.balance)
		#self.btnFlexibility.clicked.connect(self.flexibility)
		
	def home(self):
		global homeWindow
		homeWindow.showFullScreen()
		self.hide()

class AccountsWindow(QMainWindow):
	def __init__(self):
		super(AccountsWindow, self).__init__()
		uic.loadUi('ui/accountswindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		self.btnHome.clicked.connect(self.home)
		#self.btnStrength.clicked.connect(self.strength)
		#self.btnBalance.clicked.connect(self.balance)
		#self.btnFlexibility.clicked.connect(self.flexibility)
		
	def home(self):
		global homeWindow
		homeWindow.showFullScreen()
		self.hide()

class RoutineSelectWindow(QMainWindow):
	def __init__(self):
		super(RoutineSelectWindow, self).__init__()
		uic.loadUi('ui/routineselectwindow-new.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		self.btnHome.clicked.connect(self.home)
		self.btnStrength.clicked.connect(self.strength)
		self.btnBalance.clicked.connect(self.balance)
		self.btnFlexibility.clicked.connect(self.flexibility)
		
	def logout(self):
		global mainWindow
		mainWindow.showFullScreen()
		self.hide()
		mainWindow.logout()
	
	def home(self):
		global homeWindow
		homeWindow.showFullScreen()
		self.hide()
	
	def strength(self):
		global routineViewWindow
		routineViewWindow = RoutineViewWindow("Strength")
		routineViewWindow.showFullScreen()
		self.hide()
	
	def balance(self):
		global routineViewWindow
		routineViewWindow = RoutineViewWindow("Balance")
		routineViewWindow.showFullScreen()
		self.hide()
	
	def flexibility(self):
		global routineViewWindow
		routineViewWindow = RoutineViewWindow("Flexibility")
		routineViewWindow.showFullScreen()
		self.hide()

class RoutineViewWindow(QMainWindow):
	def __init__(self, workoutType):
		super(RoutineViewWindow, self).__init__()
		uic.loadUi('ui/routineviewwindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)
		
		self.workoutType = workoutType
		
		self.lblWorkoutType.setText(workoutType + " Routine")
		self.lblWorkoutMascot.setPixmap(QPixmap(workoutType + ".png"))
		self.btnBack.clicked.connect(self.back)
		self.btnStart.clicked.connect(self.start)
		
		self.position = 0
		self.routinePoints = 0
		self.workouts = []
		
		if workoutType == "Strength":
			self.workouts = ["workouts/armextension/", "workouts/sitstand/", "workouts/armextension/"]

	def back(self):
		global routineSelectWindow
		routineSelectWindow.showFullScreen()
		self.hide()
	
	def start(self):
		global videoWindow
		videoWindow = VideoWindow(self.workouts[self.position])
		videoWindow.showFullScreen()
		videoWindow.completeSignal.connect(self.nextWorkout)
		self.hide()
	
	def nextWorkout(self):
		self.position += 1
		self.routinePoints += points
		
		resultSubmitThread = ResultSubmitThread(3, self.position + 5, 23, points, self)
		resultSubmitThread.start()
		print(self.position)
		if self.position == 2:
			global routineCompleteWindow
			routineCompleteWindow = RoutineCompleteWindow(self.workoutType)
			routineCompleteWindow.showFullScreen()
			self.hide()
			print("Showing completion window")
			return
		self.start()

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		uic.loadUi('ui/mainwindow.ui', self)
		self.setWindowFlags(QtCore.Qt.Widget | QtCore.Qt.FramelessWindowHint)

		self.btnLogin.clicked.connect(self.login) # Listen for confirm button press
		self.btnClose.clicked.connect(self.close) # Listen for close button press
		
		self.show()
	
	def close(self):
		msgBox = QMessageBox()
		msgBox.setWindowTitle("Close Aegis")
		msgBox.setText("Do you really want to quit Aegis?")
		msgBox.addButton(QMessageBox.Yes)
		msgBox.addButton(QMessageBox.No)
		ret = msgBox.exec_()
		if ret == QMessageBox.Yes:
			quit()
			sys.exit(0)
	
	def login(self):
		loginThread = LoginThread(self.txtNRIC.text(), self.txtPassword.text(), self)
		loginThread.success.connect(self.success)
		loginThread.error.connect(self.error)
		loginThread.start()
	
	def logout(self):
		global routineSelectWindow
		global videoWindow
		routineSelectWindow = None
		videoWindow = None
		
	def success(self):
		global homeWindow
		homeWindow = HomeWindow()
		homeWindow.showFullScreen()
		self.hide()
		
	def error(self, response):
		msgBox = QMessageBox()
		msgBox.setWindowTitle("Error")
		msgBox.setText("Something went wrong: " + response.message)
		msgBox.addButton(QMessageBox.Ok)
		msgBox.exec_()
		return

app = QApplication(sys.argv)
mainWindow = MainWindow()
homeWindow = None
rewardsWindow = None
routineSelectWindow = None
routineViewWindow = None
routineCompleteWindow = None
videoWindow = None
mainWindow.showFullScreen()
sys.exit(app.exec_())
