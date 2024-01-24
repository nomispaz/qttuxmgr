import sys
from subprocess import run

from PyQt6.QtCore import QSize, Qt, QProcess, QByteArray
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
        QApplication,
        QPushButton,
        QMainWindow,
        QVBoxLayout,
        QGridLayout,
        QWidget,
        QPlainTextEdit,
        QInputDialog,
        QLineEdit,
        QDialogButtonBox
)

def Execute(cmd):
    return run([cmd], shell=True, capture_output=True, text=True)

def ReadDistro():
    return Execute("lsb_release -a | grep \"Distributor ID\" | tr \"[:upper:]\" \"[:lower:]\"").stdout[16:].lstrip().rstrip()

# Subclass QMainWindow to customize your application's main window
class QtTuxMgrWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # QProcess object for external app
        self.process = None
        self.password = ""

        self.setWindowTitle("nomispaz Tux Manager")

        self.vDistro = ReadDistro()

        self.button = QPushButton("Sync Repositories")
        self.button.clicked.connect(self.sync_repo)

        self.button2 = QPushButton("Update")
        self.button2.clicked.connect(self.update_system)

        #Window for output of subprocess (started with QProcess)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont('Awesome', 20))

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        layout.addWidget(self.output)

        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    #print to Textbox
    def message(self, s):
        self.output.appendPlainText(s)

    #handle error printout
    def handle_stderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    #handle stdout of process
    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def process_finished(self):
        self.message("Process finished.")
        self.process = None

    #print message of process state
    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def getPassword(self):
        vInputText, ok = QInputDialog.getText(self, "Text Input Dialog", "Enter root password:", QLineEdit.EchoMode.Password)
        if ok:
            self.password = vInputText

    def create_process(self):
        if self.process is None:  # No process running.
            self.message("Executing process")
            
            self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.process.setInputChannelMode(QProcess.InputChannelMode.ForwardedInputChannel)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.process_finished)  # Clean up once complete.
    
    def sync_repo(self):
        
        match self.vDistro:
            case "gentoo":
                cmd = "sudo -S emerge --sync gentoo_localrepo"
        
        self.create_process()
        self.getPassword()
        self.process.start('bash', ['-c', "echo " + self.password + " | " + cmd])
        
    
    def update_system(self):
        
        self.create_process()
        self.getPassword()
        
        match self.vDistro:
            case "gentoo":
                cmd = "sudo -S emerge -pvuDNg @world"
                #self.process.start('bash', ['-c', "echo " + self.password + " | " + cmd])
                self.process.start('bash')
                self.process.write('ls -l \n\n'.encode())

def main():
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    qttuxmgrApp = QApplication(sys.argv)

    # Create a Qt widget, which will be our window.
    qttuxmgrWindow = QtTuxMgrWindow()
    # IMPORTANT!!!!! Windows are hidden by default.
    qttuxmgrWindow.show()  

    # Start the event loop.
    sys.exit(qttuxmgrApp.exec())

if __name__ == "__main__":
    main()