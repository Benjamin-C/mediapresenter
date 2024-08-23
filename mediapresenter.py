#!.venv/bin/python

# Using https://github.com/jaseg/python-mpv
import mpv

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QKeySequence, QPalette, QColor
from PyQt5.QtCore import * # Qt,QTimer

from os import listdir, walk
from os.path import isfile, isdir, join

import time

import flask

# The user's home directory
from os.path import expanduser
HOME = expanduser("~")

import sys

isPhotoSlideshow = False
musicname = ''
photoList = []
nextPhoto = 0;
photoTime = 0;
photoPrefix = ''

# Config variables I may want to change later
class Config():
    autoload_next = True
    autoplay_next = False
    swap_on_load = False
    defaultRootPath = expanduser(sys.argv[1] if len(sys.argv) > 1 else '~/Videos')
    print("path:", defaultRootPath)
    video_file_types = ('.mp4', '.wav', '.png')
# status variables

config = Config()

class Status():
    stopped = False

status = Status()

MULTIPLAYER_DELAY = 0.01
PHOTO_START = 'photo?'

player = mpv.MPV(ytdl=True, input_vo_keyboard=True)
player.pause = True
player.fullscreen = True
player.fs_screen = 1
time.sleep(0.01)
player2 = mpv.MPV(ytdl=True, input_vo_keyboard=True)
player2.pause = True
player.pause = True
player2.fullscreen = True
player2.fs_screen = 1

# The lenght of the current video in Player in seconds
current_video_length = 0

# player.play('/home/benjamin/Music/ncs/FatRat/TheFatRat - Telescope.mp3')
# time.sleep(MULTIPLAYER_DELAY)
# player2.play('/home/benjamin/Videos/test.mp4')

video_current_filename = '/home/benjamin/Videos/test.mp4'
video_queue_filename = ''

app = QApplication([])
api = flask.Flask(__name__)

@api.route("/")
def api_home():
    return flask.render_template('index.html')

# Force the style to be the same on all OSs:
app.setStyle("gtk2")

# Now use a palette to switch to dark colors:
palette = QPalette()
palette.setColor(QPalette.Window, QColor(53, 53, 53))
palette.setColor(QPalette.WindowText, Qt.white)
palette.setColor(QPalette.Base, QColor(25, 25, 25))
palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
palette.setColor(QPalette.ToolTipBase, Qt.white)
palette.setColor(QPalette.ToolTipText, Qt.white)
palette.setColor(QPalette.Text, Qt.white)
palette.setColor(QPalette.Button, QColor(53, 53, 53))
palette.setColor(QPalette.ButtonText, Qt.white)
palette.setColor(QPalette.BrightText, Qt.red)
palette.setColor(QPalette.Link, QColor(42, 130, 218))
palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
palette.setColor(QPalette.HighlightedText, Qt.black)
app.setPalette(palette)

app.setApplicationName("Ben's Media Presenter")

def strTime(seconds):
    seconds = round(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    str = (f'{h:d}' if (h > 0) else '') + f'{m:02d}:{s:02d}'
    return str

num = 0

class ControlButtons(QWidget):
    def __init__(self, parent=None):
        super(ControlButtons, self).__init__(parent)

        self.originalPalette = QApplication.palette()

#Layout setups

        queueLayout = QVBoxLayout()

        self.nextTrackLabel = QLabel()
        queueLayout.addWidget(self.nextTrackLabel)
        self.currentTrackLabel = QLabel()
        queueLayout.addWidget(self.currentTrackLabel)
        self.updateNext()

# Control buttons
        controlLayout = QHBoxLayout()

        self.pauseButton = QPushButton("Start Paused")
        controlLayout.addWidget(self.pauseButton)

        self.playButton = QPushButton("Start")
        controlLayout.addWidget(self.playButton)

        self.loadButton = QPushButton("Load next")
        controlLayout.addWidget(self.loadButton)

# Time buttons
        timeLayout = QHBoxLayout()

        timeLabel = QLabel()
        timeLayout.addWidget(timeLabel)

        timeSlider = QSlider(Qt.Horizontal)
        timeLayout.addWidget(timeSlider)

        durLabel = QLabel()
        timeLayout.addWidget(durLabel)

# Main window layout
        verticalLayout = QVBoxLayout()
        verticalLayout.addLayout(queueLayout)
        verticalLayout.addLayout(controlLayout)
        verticalLayout.addLayout(timeLayout)

        self.setLayout(verticalLayout)

        def self_pauseVideo():
            if not player.active:
                self.playVideo()
            self.pauseVideo()
        self.pauseButton.clicked.connect(self_pauseVideo)
        def self_playVideo():
            if player.active:
                self.stopVideo()
            else:
                self.playVideo()
        self.playButton.clicked.connect(self_playVideo)
        def self_loadVideo():
            print(f"Click!")
            self.loadVideo()
        self.loadButton.clicked.connect(self_loadVideo)

        # Time buttons
        timeLabel.setText("-:-")
        self.timeLabel = timeLabel

        def time_slider_moved():
            if player.active:
                player.seek(timeSlider.value() / 100, reference='absolute')
                timeLabel.setText(strTime(timeSlider.value() / 100))

        timeSlider.sliderMoved.connect(time_slider_moved)

        def time_slider_released():
            if player.active:
                player.seek(timeSlider.value() / 100, reference='absolute')
        timeSlider.sliderReleased.connect(time_slider_released)
        self.timeSlider = timeSlider

        durLabel.setText("-:-")
        self.durLabel = durLabel

# Onclicks
# Control buttons
    def pauseVideo(self, state=None):
        if state == None:
            player.cycle('pause')
        else:
            player.pause = state
        self.pauseButton.setText("Play" if player.pause else "Pause")

    def playVideo(self):
        status.stopped = False
        print(f"Now Playing: {video_current_filename}")
        global isPhotoSlideshow
        global photoList
        global nextPhoto
        global photoTime
        global photoPrefix
        if video_current_filename.startswith(PHOTO_START):
            isPhotoSlideshow = True
            musicname = ''
            photoList = []
            path = video_current_filename.split('?')
            if(len(path) > 1):
                photoPrefix = path[1]
                for (dirpath, dirnames, filenames) in walk(photoPrefix):
                    for name in filenames:
                        if name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                            photoList.append(name)
                        if name.lower().endswith('.mp3'):
                            print(photoPrefix[:photoPrefix.rindex("/")])
                            musicname = photoPrefix + '/' + name;
                    break
                photoList.sort()
                print(photoList)
                print(musicname)
                player.play(musicname)
                nextPhoto = 0;
                print('Playing music now I think')
            else:
                print('Please specify path to load from')

            # print("This is a photo slideshow, I don't know what to do with it")
        else:
            isPhotoSlideshow = False
            player.play(video_current_filename)
            time.sleep(MULTIPLAYER_DELAY)

        # window.setWindowState(window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        #
        # # this will activate the window
        # window.activateWindow()

        self.pauseVideo(False)
        self.pauseButton.setText("Pause");
        self.playButton.setText('Stop')

    def stopVideo(self):
        print("Stopping")
        status.stopped = True
        player.stop()
        player2.stop()
        self.playButton.setText('Start')
        self.pauseButton.setText('Start Paused')

    def loadVideo(self, play=None, mayswap=True):
        global num
        mynum = num
        num += 1

        print(f"{mynum} Loading")
        player.stop()
        global video_current_filename
        global video_queue_filename

        tmp = video_current_filename
        print(f"{mynum} - {tmp} :: {video_queue_filename} >> {video_current_filename}")
        video_current_filename = video_queue_filename
        print(f"{mynum} - {tmp} :: {video_queue_filename} >> {video_current_filename}")
        print(f"{mynum} - Swap? {config.swap_on_load and mayswap}")
        if config.swap_on_load and mayswap:
            video_queue_filename = tmp
            print(f"{mynum} - {tmp} :: {video_queue_filename} >> {video_current_filename}")

        self.playVideo()
        print(f'play/autoplay {play} :: {config.autoplay_next}')
        if play == None:
            play = config.autoplay_next
        self.pauseVideo(not play)
        self.updateNext()
        print(f"{mynum} - end")

    def updateNext(self):
        self.nextTrackLabel.setText(f"Next: {PHOTO_START if video_queue_filename.startswith(PHOTO_START) else ''}{video_queue_filename.rsplit('/', 1)[-1]}")
        self.currentTrackLabel.setText(f"Current: {PHOTO_START if video_current_filename.startswith(PHOTO_START) else ''}{video_current_filename.rsplit('/', 1)[-1]}")

controlLayout = ControlButtons()

def setupPhotoFolder(dirname):
    print(dirname)
    global video_queue_filename
    video_queue_filename = PHOTO_START + dirname
    controlLayout.updateNext()
    print(video_queue_filename)

class TreeVideoSelector(QTreeView):
    def __init__(self, rootPath=config.defaultRootPath):
        QTreeView.__init__(self)
        self.fsmodel = QFileSystemModel()
        self.setModel(self.fsmodel)
        self.fsmodel.setRootPath(QDir.rootPath())
        self.setRoot(rootPath)
        self.clicked.connect(self.itemClickedListener)
        self.doubleClicked.connect(self.doubleClickedListener)
        self.sizeHint = lambda: QSize(370, 600)
        for i in range(1, self.fsmodel.columnCount()):
            self.setColumnHidden(i, True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu)

    def openMenu(self, position):
        menu = QMenu()
        queueMenu = QAction("Queue", self)
        queueMenu.triggered.connect(self.menu_queue)
        menu.addAction(queueMenu)
        playMenu = QAction("Play now", self)
        playMenu.triggered.connect(self.menu_play)
        menu.addAction(playMenu)
        photoMenu = QAction("Play Photos", self)
        photoMenu.triggered.connect(self.menu_photos)
        menu.addAction(photoMenu)
        rootMenu = QAction("Set Root", self)
        rootMenu.triggered.connect(self.menu_setRoot)
        menu.addAction(rootMenu)

        menu.exec_(self.viewport().mapToGlobal(position))
    # def mousePressEvent (self, event):
    #     print("child clicked ! ")
    #     if event.button() == Qt.RightButton:
    #         print("right click !")
    #     QtGui.QTreeView.mousePressEvent(self, event)

    def menu_queue(self):
        self.setupQueue(self.fsmodel.filePath(self.selectionModel().selectedIndexes()[0]))

    def menu_play(self):
        self.setupPlay(self.fsmodel.filePath(self.selectionModel().selectedIndexes()[0]))

    def menu_photos(self):
        setupPhotoFolder(self.fsmodel.filePath(self.selectionModel().selectedIndexes()[0]))

    def menu_setRoot(self):
        self.setRoot(self.fsmodel.filePath(self.selectionModel().selectedIndexes()[0]))

    def setRoot(self, newRoot):
        self.rootPath = newRoot;
        self.setRootIndex(self.fsmodel.index(newRoot))

    def itemClickedListener(self, signal):
        file_path = self.model().filePath(signal)
        print(signal)
        # print(f'{file_path}<')
        if file_path.endswith(config.video_file_types):
            # print(file_path)
            self.setupQueue(file_path)

    def setupQueue(self, file_path):
        global video_queue_filename
        video_queue_filename = file_path
        controlLayout.updateNext()

    def doubleClickedListener(self, signal):
        file_path = self.model().filePath(signal)
        # print(f'{file_path}<')
        if file_path.endswith(config.video_file_types):
            # print(file_path)
            self.setupPlay(file_path)

    def setupPlay(self, file_path):
        global video_queue_filename
        video_queue_filename = file_path
        controlLayout.updateNext()
        controlLayout.loadVideo(mayswap=False)

    def rightClickedListener(self, signal):
        print(f'I have been double clicked at {self.model().filePath(signal)}');

        pass
        # file_path=self.model().filePath(signal)
        # print(file_path)

tree = TreeVideoSelector()

# Main window class
class MainWindow(QMainWindow):
    def __init__(self, controlbuttons, parent=None):
        super(MainWindow, self).__init__(parent)
        verticalLayout = QVBoxLayout()

        verticalLayout.addWidget(tree)
        verticalLayout.addWidget(controlbuttons)

        mainWidget = QWidget()
        mainWidget.setLayout(verticalLayout)
        self.setCentralWidget(mainWidget)
        self.setWindowTitle("Ben's Media Presenter")

        # menu = self.menuBar()#.addMenu("&File")
        # file_menu = QMenu("&File", self)
        # menu.addMenu(file_menu)
        #
        # open_action = QAction("&Open")
        # def open_file():
        #     # global file_path
        #     path = QFileDialog.getOpenFileName(window, "Open")[0]
        #     if path:
        #         # text.setPlainText(open(path).read())
        #         # file_path = path
        #         print(path)
        # open_action.triggered.connect(open_file)
        # open_action.setShortcut(QKeySequence.Open)
        # file_menu.addAction(open_action)

        self._createMenuBar()

    def openRootFolder(self):
        dirname = ''
        dirname = QFileDialog.getExistingDirectory(self, "Select the root folder for videos",
            HOME + "/Videos",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dirname == '':
            dirname = QFileDialog.getExistingDirectory(self, "You must select the root folder for videos",
                HOME + "/Videos",
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if dirname == '':
                return

        print(dirname)
        tree.setRoot(dirname)

    def openPhotoFolder(self):
        print('Open Photo Folder')
        dirname = ''
        startpoint = tree.rootPath
        dirname = QFileDialog.getExistingDirectory(self, "Select the folder containing the photos and music",
            startpoint, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dirname == '':
            dirname = QFileDialog.getExistingDirectory(self, "You must select the folder containing the photos and music",
                startpoint, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
            if dirname == '':
                return
        setupPhotoFolder(dirname)

    def debug_setQueue(self):
        print('SEtting...')
        name, done = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')
        if done:
            global video_queue_filename
            video_queue_filename = name
            controlLayout.updateNext()
            print('DEBUG set queue to', name)

    def _createMenuBar(self):
        menuBar = self.menuBar()

        self.openAction = QAction("&Open...", self)
        def self_openFolder():
            self.openRootFolder()
        self.openAction.triggered.connect(self_openFolder)
        self.openPhotoAction = QAction("&Open Photos...", self)
        def self_openPhotoFolder():
            self.openPhotoFolder()
        self.openPhotoAction.triggered.connect(self_openPhotoFolder)
        self.exitAction = QAction("&Exit", self)
        def closeWindow():
            self.close()
        self.exitAction.triggered.connect(closeWindow)

        self.autoloadAction = QAction("Autoload Queue on EoF", self, checkable=True, checked=config.autoload_next)
        def onAutoloadAction():
            global config
            config.autoload_next = self.autoloadAction.isChecked()
        self.autoloadAction.toggled.connect(onAutoloadAction)
        self.autoplayAction = QAction("Autoplay loaded videos", self, checkable=True, checked=config.autoplay_next)
        def onAutoplayAction():
            global config
            config.autoplay_next = self.autoplayAction.isChecked()
        self.autoplayAction.toggled.connect(onAutoplayAction)
        self.swaponloadAction = QAction("Swap queue on load", self, checkable=True, checked=config.swap_on_load)
        def onAutoplayAction():
            global config
            config.swap_on_load = self.swaponloadAction.isChecked() or True
        self.swaponloadAction.toggled.connect(onAutoplayAction)

        self.debugNextAction = QAction("&Set queue...", self)
        def self_debug_setQueue():
            self.debug_setQueue()
        self.debugNextAction.triggered.connect(self_debug_setQueue)

        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.openPhotoAction)
        fileMenu.addAction(self.exitAction)

        # Config menu
        configMenu = menuBar.addMenu("&Config")
        configMenu.addAction(self.autoloadAction)
        configMenu.addAction(self.autoplayAction)
        configMenu.addAction(self.swaponloadAction)

        # Debug menu
        fileMenu = QMenu("&Debug", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.debugNextAction)

        #Keyboard shortcuts, also add shortcuts to MPV down below
        def onKeyPause():
            my_pause_binding()
        self.pauseSc = QShortcut(QKeySequence('space'), self, onKeyPause)

        def onKeyRestart():
            my_restart_binding()
        self.pauseSc = QShortcut(QKeySequence('r'), self, onKeyRestart)

        def onKeySeekBack():
            my_seek_back_binding()
        self.seekBackSc = QShortcut(Qt.Key_Left, self, onKeySeekBack)

        def onKeySeekForward():
            my_seek_forward_binding()
        self.seeForwardSc = QShortcut(Qt.Key_Right, self, onKeySeekForward)


        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def closeEvent(self, e):
        answer = QMessageBox.question(
            window, None,
            "Are you sure you want to exit?",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if answer & QMessageBox.Ok:
            pass # Do nothing
        elif answer & QMessageBox.Cancel:
            e.ignore()

window = MainWindow(controlLayout)

# Add keyboard shortcuts here in addition to in MainWindow above
# @player.on_key_press('q')
# def my_q_binding():
#     player.stop()
#     # player.toggle_osd()
#
@player.on_key_press('space')
def my_pause_binding():
    controlLayout.pauseVideo()

@api.route('/pause')
def api_pause():
    my_pause_binding()
    return str(player.pause)

@api.route('/stop')
def api_stop():
    controlLayout.stopVideo()
    return str(status.stopped)

@player.on_key_press('left')
def my_seek_back_binding():
    player.seek(-5)

@api.route('/seekback')
def api_seek_back():
    my_seek_back_binding()
    return "OK"

@player.on_key_press('right')
def my_seek_forward_binding():
    player.seek(5)

@api.route('/seekforward')
def api_seek_forward():
    my_seek_forward_binding()
    return "OK"

@player.on_key_press('r')
def my_restart_binding():
    player.seek(0, reference='absolute')
    controlLayout.pauseVideo(True)

@api.route('/seekstart')
def api_seek_start():
    my_restart_binding()
    return "OK"

@api.route('/next')
def api_next():
    controlLayout.loadVideo()
    return "OK"

@api.route('/duration')
def api_duration():
    return controlLayout.durLabel.text()

@api.route('/time')
def api_time():
    return controlLayout.timeLabel.text()

@api.route('/status')
def api_status():
    data = {
        "duration": controlLayout.durLabel.text(),
        "time": controlLayout.timeLabel.text(),
        "stopped": status.stopped,
        "paused": player.pause,
        "name": video_current_filename,
        "next": video_queue_filename
    }
    return data


print('Got here')

@player.property_observer('time-pos')
def time_observer(_name, value):
    # Here, _value is either None if nothing is playing or a float containing
    # fractional seconds since the beginning of the file.
    if not controlLayout.timeSlider.isSliderDown():
        if value != None:
            # print('Now playing at {:.2f}s'.format(value))
            if isPhotoSlideshow:
                if value > 0.01:
                    global nextPhoto
                    if value > nextPhoto:
                        nextPhoto += photoTime
                        global photoList
                        photoName = photoPrefix + '/' + photoList.pop(0);
                        player2.play(photoName);
                        print(f'Next photo "{photoName}"')

            controlLayout.timeSlider.setValue(int(value * 100))
            controlLayout.timeLabel.setText(strTime(controlLayout.timeSlider.value() / 100))
            # window.timeLabel.setText(strTime())
        else:
            controlLayout.timeSlider.setValue(0)
            controlLayout.timeSlider.setDisabled(True)
            controlLayout.timeLabel.setText('-:-')

@player.property_observer('duration')
def dur_observer(_name, value):
    # Here, _value is either None if nothing is playing or a float containing
    # fractional seconds since the beginning of the file.
    if value != None:
        print('Length is {:.2f}s'.format(value))
        print(f'isPhotoSlideshow? {isPhotoSlideshow}')
        current_video_length = value;
        if(isPhotoSlideshow):
            global photoTime;
            photoTime = value / len(photoList);
            print(f'There are {len(photoList)} photos')
            print(f'Photo time is {photoTime}')
        controlLayout.timeSlider.setMaximum(int(value * 100))
        controlLayout.timeSlider.setDisabled(False)
        controlLayout.durLabel.setText(strTime(value))
    else:
        controlLayout.timeSlider.setDisabled(True)
        controlLayout.timeSlider.setMaximum(0)
        controlLayout.timeLabel.setText('-:-')
        controlLayout.durLabel.setText('-:-')

@player.property_observer('eof-reached')
def dur_observer(_name, value):
    if value == None:
        if config.autoload_next and not status.stopped:
            controlLayout.loadVideo(config.autoplay_next)
        else:
            controlLayout.stopVideo()

class WebServerThread(QThread):
    def run(self):
        api.run(host='0.0.0.0')

web_server_thread = WebServerThread()
web_server_thread.start()  # Start the Web Server thread

print("This application must be closed from the window, ctl+c will not work.")
window.show()
app.exec_()