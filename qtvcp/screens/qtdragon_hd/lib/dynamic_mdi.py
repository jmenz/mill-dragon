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
        
        self.param_fields = {}
        self.current_base_cmd = ""
        self._init_ui()

    def set_target(self, line_edit):
        self.target_input = line_edit
        self.target_input.textChanged.connect(self._on_target_text_changed)

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.left_scroll = QtWidgets.QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_widget = QtWidgets.QWidget()
        self.left_layout = QtWidgets.QVBoxLayout(self.left_widget)
        self.left_layout.setAlignment(QtCore.Qt.AlignTop)
        self.left_scroll.setWidget(self.left_widget)
        main_layout.addWidget(self.left_scroll, stretch=1)
        
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
        grid = QtWidgets.QGridLayout()
        right_layout.addLayout(grid)

        keys = [
            ('G', 0, 0, 1), ('7', 0, 1, 1), ('8', 0, 2, 1), ('9', 0, 3, 1),
            ('M', 1, 0, 1), ('4', 1, 1, 1), ('5', 1, 2, 1), ('6', 1, 3, 1),
            ('T', 2, 0, 1), ('1', 2, 1, 1), ('2', 2, 2, 1), ('3', 2, 3, 1),
            ('BS',3, 0, 1), ('0', 3, 1, 1), ('.', 3, 2, 1), ('-', 3, 3, 1),
            ('NEXT', 4, 0, 2), ('EXEC', 4, 2, 2)
        ]

        for text, r, c, span in keys:
            btn = QtWidgets.QPushButton(text)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            btn.setMinimumHeight(60)
            btn.setStyleSheet("font-size: 18pt; font-weight: bold;")
            
            btn.setFocusPolicy(QtCore.Qt.NoFocus)
            
            if text == 'BS': 
                btn.clicked.connect(self._handle_backspace)
            elif text == 'NEXT': 
                btn.clicked.connect(self._focus_next)
            elif text == 'EXEC': 
                btn.clicked.connect(self._execute_cmd)
                btn.setStyleSheet("font-size: 18pt; font-weight: bold; background-color: #2e7d32; color: white;")
            else: 
                btn.clicked.connect(lambda checked, t=text: self._send_text(t))
            grid.addWidget(btn, r, c, 1, span)

    def _on_target_text_changed(self, text):
        cmd = text.strip().upper()
        if cmd == self.current_base_cmd:
            return
            
        for i in reversed(range(self.left_layout.count())):
            w = self.left_layout.itemAt(i).widget()
            if w: w.deleteLater()
        
        self.param_fields.clear()
        self.current_base_cmd = cmd
        
        if cmd in self.gcode_dict:
            axes = self._get_active_axes()
            for p in self.gcode_dict[cmd]:
                params = axes if p == 'A' else [p]
                for param in params:
                    row = QtWidgets.QWidget()
                    l = QtWidgets.QHBoxLayout(row)
                    lbl = QtWidgets.QLabel(param)
                    lbl.setFixedWidth(50)
                    lbl.setStyleSheet("font-size: 20pt; font-weight: bold;")
                    edit = QtWidgets.QLineEdit()
                    edit.setStyleSheet("font-size: 20pt; height: 50px;")
                    
                    edit.setAttribute(QtCore.Qt.WA_InputMethodEnabled, False)
                    
                    l.addWidget(lbl); l.addWidget(edit)
                    self.left_layout.addWidget(row)
                    self.param_fields[param] = edit
            
            if self.param_fields:
                list(self.param_fields.values())[0].setFocus()

    def _send_text(self, text):
        f = QtWidgets.QApplication.focusWidget()
        if isinstance(f, QtWidgets.QLineEdit): 
            f.insert(text)

    def _handle_backspace(self):
        f = QtWidgets.QApplication.focusWidget()
        if isinstance(f, QtWidgets.QLineEdit): 
            f.backspace()

    def _focus_next(self):
        f = QtWidgets.QApplication.focusWidget()
        fields = []
        if self.target_input:
            fields.append(self.target_input)
        fields.extend(list(self.param_fields.values()))
        
        if f in fields:
            idx = (fields.index(f) + 1) % len(fields)
            fields[idx].setFocus()
        elif fields:
            fields[0].setFocus()

    def _execute_cmd(self):
        if not self.target_input: return
        
        parts = [self.current_base_cmd]
        for p, edit in self.param_fields.items():
            val = edit.text().strip()
            if val: parts.append(f"{p}{val}")
        
        self.target_input.setText(" ".join(parts))
        self.target_input.returnPressed.emit()
        
        self.target_input.clear()
        self.target_input.setFocus()

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