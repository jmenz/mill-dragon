from PyQt5 import QtCore, QtWidgets, QtGui

class TouchyNumpad(QtWidgets.QDialog):
    def __init__(self, title="Enter Value", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.value = None
        self.back_sym = '\u2190'
        
        layout = QtWidgets.QVBoxLayout(self)
        

        self.display = QtWidgets.QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(QtCore.Qt.AlignRight)
        self.display.setMinimumHeight(60)
        self.display.setStyleSheet("font-size: 20pt;")
        layout.addWidget(self.display)
        
        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid)

        buttons = [
            ('ESC', 0, 0), ('CLR', 0, 1), (self.back_sym, 0, 2),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
            ('0', 4, 0), ('.', 4, 1), ('-', 4, 2),
            ('OK', 5, 0)
        ]
        
        for text, row, col in buttons:
            btn = QtWidgets.QPushButton(text)
            btn.setMinimumSize(70, 70)
            btn.setStyleSheet("font-size: 16pt; font-weight: bold;")
            
            if text == 'OK':
                btn.setObjectName("btn_numpad_ok")
                grid.addWidget(btn, row, col, 1, 3)
            else:
                if text == 'ESC':
                    btn.setObjectName("btn_numpad_esc")
                grid.addWidget(btn, row, col)
            
            btn.clicked.connect(lambda _, t=text: self.on_click(t))

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
        elif text == self.back_sym:
            self.display.setText(current[:-1])
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
            
        title = self.property('numpad_title') or self.accessibleName() or "Input Value"
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
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            
            if isinstance(obj, QtWidgets.QLineEdit) and not obj.isReadOnly():
                
                title = obj.property('numpad_title')
        
                if not title:
                    raw_name = obj.objectName().replace('lineEdit_', '')
                    title = raw_name.replace('_', ' ').title()
                
                dialog = TouchyNumpad(title, obj.window())
                dialog.display.setText(obj.text())
                
                if dialog.exec_() == QtWidgets.QDialog.Accepted and dialog.value is not None:
                    obj.setText(str(dialog.value))
                    obj.editingFinished.emit()
                    
                return True
                
        return super().eventFilter(obj, event)