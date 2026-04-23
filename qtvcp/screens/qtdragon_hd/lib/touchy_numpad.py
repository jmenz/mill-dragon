from PyQt5 import QtCore, QtWidgets, QtGui
from qtvcp.core import Status

STATUS = Status()

class TouchyNumpad(QtWidgets.QDialog):
    def __init__(self, title="Enter Value", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.value = None
        back_sym = '\u2190'
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.display = QtWidgets.QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(QtCore.Qt.AlignRight)
        self.display.setMinimumHeight(60)
        self.display.setStyleSheet("font-size: 20pt;")
        layout.addWidget(self.display)
        
        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid)

        # Matrix: (Text, Row, Col, ColSpan, Handler)
        matrix = [
            ('ESC', 0, 0, 1, self.reject),      ('CLR', 0, 1, 1, self.display.clear), (back_sym, 0, 2, 1, self._handle_backspace),
            ('7', 1, 0, 1, self._handle_digit), ('8', 1, 1, 1, self._handle_digit), ('9', 1, 2, 1, self._handle_digit),
            ('4', 2, 0, 1, self._handle_digit), ('5', 2, 1, 1, self._handle_digit), ('6', 2, 2, 1, self._handle_digit),
            ('1', 3, 0, 1, self._handle_digit), ('2', 3, 1, 1, self._handle_digit), ('3', 3, 2, 1, self._handle_digit),
            ('0', 4, 0, 1, self._handle_digit), ('.', 4, 1, 1, self._handle_dot),   ('-', 4, 2, 1, self._handle_sign),
            ('OK', 5, 0, 3, self._handle_ok),
            ('X', 6, 0, 1, lambda: self._handle_axis(0)),
            ('Y', 6, 1, 1, lambda: self._handle_axis(1)),
            ('Z', 6, 2, 1, lambda: self._handle_axis(2))
        ]

        for text, row, col, span, handler in matrix:
            btn = QtWidgets.QPushButton(text)
            btn.setMinimumSize(70, 70)
            btn.setStyleSheet("font-size: 16pt; font-weight: bold;")
            
            if text == 'OK': btn.setObjectName("btn_numpad_ok")
            if text == 'ESC': btn.setObjectName("btn_numpad_esc")
            
            grid.addWidget(btn, row, col, 1, span)
            
            if handler == self._handle_digit:
                btn.clicked.connect(lambda checked, t=text, h=handler: h(t))
            else:
                btn.clicked.connect(lambda checked, h=handler: h())

    def _handle_axis(self, axis_idx):
        try:
            stat = STATUS.stat
            val = stat.position[axis_idx] - stat.g5x_offset[axis_idx] - stat.g92_offset[axis_idx] - stat.tool_offset[axis_idx]
            prec = 3 if stat.linear_units == 1 else 4
            self.display.setText(f"{val:.{prec}f}")
        except:
            pass

    def _handle_digit(self, digit):
        self.display.setText(self.display.text() + digit)

    def _handle_backspace(self):
        self.display.setText(self.display.text()[:-1])

    def _handle_sign(self):
        current = self.display.text()
        if current.startswith('-'):
            self.display.setText(current[1:])
        else:
            self.display.setText('-' + current)

    def _handle_dot(self):
        current = self.display.text()
        if '.' not in current:
            if not current or current == '-':
                self.display.setText(current + '0.')
            else:
                self.display.setText(current + '.')

    def _handle_ok(self):
        current = self.display.text()
        if not current or current in ('.', '-', '-.'):
            current = "0"
        if current.endswith('.'):
            current = current[:-1]
        self.value = current
        self.accept()


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
            if (val != 0):
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
                if (float(obj.text()) != 0):
                    dialog.display.setText(obj.text())
                
                if dialog.exec_() == QtWidgets.QDialog.Accepted and dialog.value is not None:
                    obj.setText(str(dialog.value))
                    obj.editingFinished.emit()
                    
                return True
                
        return super().eventFilter(obj, event)