import sys
from subprocess import run
from time import sleep

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

        self.okcancel = None

        self.setWindowTitle("nomispaz Tux Manager")

        self.vDistro = ReadDistro()

        self.button = QPushButton("Sync Repositories")
        self.button.clicked.connect(self.sync_repo)

        self.button2 = QPushButton("Update")
        self.button2.clicked.connect(self.update_system)

        self.buttonOk = QPushButton("Continue")
        self.buttonOk.clicked.connect(self.event_continue)

        self.buttonCancel = QPushButton("Cancel")
        self.buttonCancel.clicked.connect(self.event_cancel)

        #Window for output of subprocess (started with QProcess)
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont('Awesome', 20))

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        layout.addWidget(self.output)
        layout.addWidget(self.buttonOk)
        layout.addWidget(self.buttonCancel)

        widget = QWidget()
        widget.setLayout(layout)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    def event_continue(self):
        self.okcancel = "ok"
        self.sendCommandToProcess("yes")

    def event_cancel(self):
        self.okcancel = "cancel"
        self.sendCommandToProcess("no")

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

    #read password from input dialog (masked with asterixes)
    def getPassword(self):
        vInputText, ok = QInputDialog.getText(self, "Text Input Dialog", "Enter root password:", QLineEdit.EchoMode.Password)
        if ok:
            self.password = vInputText

    #setup qprocess
    def create_process(self):
        if self.process is None:  # No process running.
            self.message("Executing process")
            
            self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect(self.handle_stderr)
            self.process.stateChanged.connect(self.handle_state)
            self.process.finished.connect(self.process_finished)  # Clean up once complete.
    
    #Event: Synchronize repository
    def sync_repo(self):
        self.okcancel = None
        self.create_process()

        match self.vDistro:
            case "gentoo":
                cmd = "sudo -S emerge --sync gentoo_localrepo"
        
        
        self.getPassword()
        #echo password to enable -S
        self.process.start('bash', ['-c', "echo " + self.password + " | " + cmd])

        #cleanup at the end
        self.okcancel = None
        
    #send commands to running qprocess into started (hidden) shell
    def sendCommandToProcess(self, cmd):
        self.writeCommand = QByteArray()
        self.writeCommand.append(cmd.encode())
        self.writeCommand.append("\n".encode())
        self.process.write(self.writeCommand)
        self.writeCommand.clear()
    
    #Event: Perform update
    def update_system(self):
        self.okcancel = None
        self.create_process()
        
        match self.vDistro:
            case "gentoo":
                cmd = "sudo -S emerge -pvuDNg @world"
                #self.process.start('bash', ['-i', cmd])
                
        self.process.start('/bin/bash')
        self.sendCommandToProcess(cmd)
        self.getPassword()
        self.sendCommandToProcess(self.password)
        
        self.message("Continue?")
        self.message(self.okcancel)

            
        
        #cleanup at the end
        self.okcancel = None
                
###############################################################################

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