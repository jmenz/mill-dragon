from PyQt5 import QtCore, QtWidgets, QtGui

class TouchyNumpad(QtWidgets.QDialog):
    def __init__(self, title="Enter Value", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.value = None
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Поле вводу
        self.display = QtWidgets.QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(QtCore.Qt.AlignRight)
        
        # Задаємо висоту для тачскріна
        self.display.setMinimumHeight(60)
        
        self.display.setStyleSheet("font-size: 20pt;")
        
        layout.addWidget(self.display)
        
        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('.', 3, 1), ('-', 3, 2),
            ('CLR', 4, 0),('ESC', 4, 1), ('OK', 4, 2)
        ]
        
        for btn_text, row, col in buttons:
            btn = QtWidgets.QPushButton(btn_text)
            btn.setMinimumSize(70, 70)
            btn.setStyleSheet("font-size: 16pt; font-weight: bold;")
            
            if btn_text == 'OK':
                btn.setObjectName("btn_numpad_ok")
            elif btn_text == 'ESC':
                btn.setObjectName("btn_numpad_esc")
                
            grid.addWidget(btn, row, col)
            btn.clicked.connect(lambda checked, text=btn_text: self.on_click(text))

    def on_click(self, text):
        current = self.display.text()
        if text == 'OK':
            val = current

            if not val or val in ('.', '-', '-.'):
                val = "0"
            
            if val.endswith('.'):
                val = val[:-1]
            
            self.value = val
            self.accept()
        elif text == 'ESC':
            self.reject()
        elif text == 'CLR':
            self.display.clear()
        elif text == '-':
            if current.startswith('-'):
                self.display.setText(current[1:])
            else:
                self.display.setText('-' + current)
        elif text == '.':
            if '.' not in current:
                if not current or current == '-':
                    self.display.setText(current + '0.')
                else:
                    self.display.setText(current + '.')
        else:
            self.display.setText(current + text)

class TouchyLineEdit(QtWidgets.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

    def mousePressEvent(self, event):
        if self.isReadOnly():
            super().mousePressEvent(event)
            return
            
        title = self.property('touchy_title') or self.accessibleName() or "Input Value"
        dialog = TouchyNumpad(title, self.window())
        
        try:
            val = self.text()
            float(val)
            dialog.display.setText(val)
        except (ValueError, TypeError):
            pass
            
        if dialog.exec_() == QtWidgets.QDialog.Accepted and dialog.value is not None:
            self.setText(str(dialog.value))
            self.editingFinished.emit()
            self.returnPressed.emit()

class TouchyEventFilter(QtCore.QObject):
    def eventFilter(self, receiver, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if isinstance(receiver, QtWidgets.QLineEdit) and not receiver.isReadOnly():

                title = receiver.property('touchy_title') or receiver.accessibleName() or "Input Value"
                
                dialog = TouchyNumpad(title, receiver.window())
                val = receiver.text()
                try:
                    float(val)
                    dialog.display.setText(val)
                except:
                    pass
                if dialog.exec_() == QtWidgets.QDialog.Accepted and dialog.value is not None:
                    receiver.setText(str(dialog.value))
                    receiver.editingFinished.emit()
                    receiver.returnPressed.emit()
                return True 
        return super().eventFilter(receiver, event)