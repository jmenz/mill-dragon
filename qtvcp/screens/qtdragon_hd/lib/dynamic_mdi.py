from PyQt5 import QtCore, QtWidgets
from qtvcp.core import Status

STATUS = Status()

class DynamicMDI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_input = None
        self.gcode_dict = {
            'G0': ['A'], 'G00': ['A'],
            'G1': ['A', 'F'], 'G01': ['A', 'F'],
            'G2': ['A', 'I', 'J', 'K', 'R', 'P', 'F'],
            'G3': ['A', 'I', 'J', 'K', 'R', 'P', 'F'],
            'G4': ['P'], 'G76': ['Z', 'P', 'I', 'J', 'K', 'R', 'Q', 'H', 'E', 'L'],
            'M3': ['S'], 'M4': ['S'], 'M6': ['T']
        }
        self.arg_fields = {}
        self._init_ui()

    def set_target(self, line_edit):
        self.target_input = line_edit

    def showEvent(self, event):
        super().showEvent(event)
        QtCore.QTimer.singleShot(100, self.cmd_edit.setFocus)

    def _get_active_axes(self):
        try:
            stat = STATUS.stat
            stat.poll()
            am = stat.axis_mask
            axes = []
            axisnames = ['X', 'Y', 'Z', 'A', 'B', 'C', 'U', 'V', 'W']
            for i in range(9):
                if am & (1<<i): axes.append(axisnames[i])
            return axes if axes else ['X', 'Y', 'Z']
        except:
            return ['X', 'Y', 'Z']

    def _init_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        left_container = QtWidgets.QWidget()
        self.left_layout = QtWidgets.QVBoxLayout(left_container)
        self.left_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.cmd_edit = QtWidgets.QLineEdit()
        self.cmd_edit.setStyleSheet("font-size: 22pt; color: black; background-color: white; height: 60px; border: 2px solid #555;")
        self.cmd_edit.setAttribute(QtCore.Qt.WA_InputMethodEnabled, False)
        self.cmd_edit.textChanged.connect(self._on_cmd_changed)
        self.left_layout.addWidget(self.cmd_edit)
        
        self.args_container = QtWidgets.QWidget()
        self.args_layout = QtWidgets.QVBoxLayout(self.args_container)
        self.args_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.addWidget(self.args_container)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(left_container)
        main_layout.addWidget(scroll, stretch=1)
        
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        grid = QtWidgets.QGridLayout()
        right_layout.addLayout(grid)

        keys = [
            ('G', 0, 0, 1), ('7', 0, 1, 1), ('8', 0, 2, 1), ('9', 0, 3, 1),
            ('M', 1, 0, 1), ('4', 1, 1, 1), ('5', 1, 2, 1), ('6', 1, 3, 1),
            ('T', 2, 0, 1), ('1', 2, 1, 1), ('2', 2, 2, 1), ('3', 2, 3, 1),
            ('BS', 3, 0, 1), ('0', 3, 1, 1), ('.', 3, 2, 1), ('-', 3, 3, 1),
            ('NEXT', 4, 0, 2), ('EXEC', 4, 2, 2)
        ]

        for text, r, c, span in keys:
            btn = QtWidgets.QPushButton(text)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            btn.setMinimumHeight(70)
            btn.setFocusPolicy(QtCore.Qt.NoFocus)
            btn.setStyleSheet("font-size: 18pt; font-weight: bold;")
            
            if text == 'BS': 
                btn.clicked.connect(self._handle_backspace)
            elif text == 'NEXT': 
                btn.clicked.connect(self._focus_next)
            elif text == 'EXEC': 
                btn.clicked.connect(self._execute_cmd)
                btn.setStyleSheet("font-size: 18pt; font-weight: bold; background-color: #1b5e20; color: white;")
            else: 
                btn.clicked.connect(lambda checked, t=text: self._send_text(t))
            grid.addWidget(btn, r, c, 1, span)
        
        main_layout.addWidget(right_panel, stretch=1)

    def _update_target(self):
        if not self.target_input: return
        base = self.cmd_edit.text().strip().upper()
        if not base: return
        
        parts = [base]
        for p, edit in self.arg_fields.items():
            val = edit.text().strip()
            if val: parts.append(f"{p}{val}")
        
        self.target_input.setText(" ".join(parts))

    def _on_cmd_changed(self, text):
        for i in reversed(range(self.args_layout.count())):
            w = self.args_layout.itemAt(i).widget()
            if w: w.deleteLater()
        self.arg_fields.clear()
        
        cmd = text.strip().upper()
        if cmd in self.gcode_dict:
            axes = self._get_active_axes()
            for p in self.gcode_dict[cmd]:
                params = axes if p == 'A' else [p]
                for param in params:
                    row = QtWidgets.QWidget()
                    l = QtWidgets.QHBoxLayout(row)
                    l.setContentsMargins(0, 2, 0, 2)
                    lbl = QtWidgets.QLabel(param)
                    lbl.setFixedWidth(50); lbl.setStyleSheet("font-size: 18pt; font-weight: bold; color: black;")
                    edit = QtWidgets.QLineEdit()
                    edit.setStyleSheet("font-size: 18pt; color: black; background-color: white; height: 45px; border: 1px solid #999;")
                    edit.setAttribute(QtCore.Qt.WA_InputMethodEnabled, False)
                    edit.textChanged.connect(self._update_target)
                    l.addWidget(lbl); l.addWidget(edit)
                    self.args_layout.addWidget(row)
                    self.arg_fields[param] = edit
        
        self._update_target()

    def _send_text(self, text):
        f = QtWidgets.QApplication.focusWidget()
        if isinstance(f, QtWidgets.QLineEdit): f.insert(text)

    def _handle_backspace(self):
        f = QtWidgets.QApplication.focusWidget()
        if isinstance(f, QtWidgets.QLineEdit): f.backspace()

    def _focus_next(self):
        f = QtWidgets.QApplication.focusWidget()
        all_fields = [self.cmd_edit] + list(self.arg_fields.values())
        if f in all_fields:
            idx = (all_fields.index(f) + 1) % len(all_fields)
            all_fields[idx].setFocus()
        else:
            self.cmd_edit.setFocus()

    def _execute_cmd(self):
        if not self.target_input: return
        if self.target_input.text().strip():
            self.target_input.returnPressed.emit()
            self.cmd_edit.clear()
            self.target_input.clear()
            self.cmd_edit.setFocus()

class MdiFocusFilter(QtCore.QObject):
    def __init__(self, stacked_widget, target_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.target_widget = target_widget

    def eventFilter(self, obj, event):
        if event.type() in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.FocusIn):
            self.stacked_widget.setCurrentWidget(self.target_widget)
            return True 
        return False