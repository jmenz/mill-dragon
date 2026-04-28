from PyQt5 import QtCore, QtWidgets, QtGui
from qtvcp.core import Status

STATUS = Status()

def _(txt): return txt

class DynamicMDI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.target_input = None
        self.close_callback = None
        
        self.gcode_dict = {
            'M3' : [_('Spindle CW'), 'S'],
            'M4' : [_('Spindle CCW'), 'S'],
            'M6' : [_('Tool change'), 'T'],
            'M61' : [_('Set tool number'), 'Q'],
            'M66' : [_('Input control'), 'P', 'E', 'L', 'Q'],
            'G0' : [_('Straight rapid'), 'A'],
            'G00' : [_('Straight rapid'), 'A'],
            'G1' : [_('Straight feed'), 'A', 'F'],
            'G01' : [_('Straight feed'), 'A', 'F'],
            'G2' : [_('Arc CW'), 'A', 'I', 'J', 'K', 'R', 'P', 'F'],
            'G02' : [_('Arc CW'), 'A', 'I', 'J', 'K', 'R', 'P', 'F'],
            'G3' : [_('Arc CCW'), 'A', 'I', 'J', 'K', 'R', 'P', 'F'],
            'G03' : [_('Arc CCW'), 'A', 'I', 'J', 'K', 'R', 'P', 'F'],
            'G4' : [_('Dwell'), 'P'],
            'G04' : [_('Dwell'), 'P'],
            'G10' : [_('Setup'), 'L', 'P', 'A', 'Q', 'R', 'J', 'I'],
            'G33' : [_('Spindle synchronized feed'), 'A', 'K'],
            'G33.1' : [_('Rigid tap'), 'Z', 'K'],
            'G38.2' : [_('Probe'), 'A', 'F'],
            'G38.3' : [_('Probe'), 'A', 'F'],
            'G38.4' : [_('Probe'), 'A', 'F'],
            'G38.5' : [_('Probe'), 'A', 'F'],
            'G41' : [_('Radius compensation left'), 'D'],
            'G42' : [_('Radius compensation right'), 'D'],
            'G41.1' : [_('Radius compensation left, immediate'), 'D', 'L'],
            'G42.1' : [_('Radius compensation right, immediate'), 'D', 'L'],
            'G43' : [_('Tool length offset'), 'H'],
            'G43.1' : [_('Tool length offset immediate'), 'A'],
            'G43.2' : [_('Tool length offset additional'), 'H', 'A'],
            'G53' : [_('Motion in unoffset coordinates'), 'G', 'A', 'F'],
            'G64' : [_('Continuous mode'), 'P', 'Q'],
            'G76' : [_('Thread'), 'Z', 'P', 'I', 'J', 'K', 'R', 'Q', 'H', 'E', 'L'],
            'G81' : [_('Drill'), 'A', 'R', 'L', 'F'],
            'G82' : [_('Drill with dwell'), 'A', 'R', 'L', 'P', 'F'],
            'G83' : [_('Peck drill'), 'A', 'R', 'L', 'Q', 'F'],
            'G73' : [_('Chip-break drill'), 'A', 'R', 'L', 'Q', 'F'],
            'G85' : [_('Bore'), 'A', 'R', 'L', 'F'],
            'G89' : [_('Bore with dwell'), 'A', 'R', 'L', 'P', 'F'],
            'G92' : [_('Offset all coordinate systems'), 'A'],
            'G96' : [_('CSS Mode'), 'S', 'D'],
        }
        self.arg_fields = {}
        self._init_ui()
        self._init_shotcuts()

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
        
        left_container = QtWidgets.QFrame()
        left_container.setFrameShape(QtWidgets.QFrame.StyledPanel)
        
        self.left_layout = QtWidgets.QVBoxLayout(left_container)
        self.left_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self.cmd_desc_label = QtWidgets.QLabel("")
        self.cmd_desc_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        self.cmd_desc_label.setFixedHeight(25)
        self.left_layout.addWidget(self.cmd_desc_label)
        
        self.cmd_edit = QtWidgets.QLineEdit()
        self.cmd_edit.setStyleSheet("font-size: 22pt;")
        self.cmd_edit.setMinimumHeight(60)
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
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame) 
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
            
            if text == 'BS': 
                btn.setStyleSheet("font-size: 18pt; font-weight: bold;")
                btn.clicked.connect(self._handle_backspace)
            elif text == 'NEXT': 
                btn.setStyleSheet("font-size: 18pt; font-weight: bold;")
                btn.clicked.connect(self._focus_next)
            elif text == 'EXEC': 
                btn.setStyleSheet("font-size: 18pt; font-weight: bold; background-color: #1b5e20; color: white;")
                btn.clicked.connect(self._execute_cmd)
            else: 
                btn.setStyleSheet("font-size: 18pt; font-weight: bold;")
                btn.clicked.connect(lambda checked, t=text: self._send_text(t))
            
            grid.addWidget(btn, r, c, 1, span)
        
        main_layout.addWidget(right_panel, stretch=1)

    def _init_shotcuts(self):
        self.tab_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Tab), self)
        self.tab_shortcut.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.tab_shortcut.activated.connect(self._focus_next)

        self.enter_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Return), self)
        self.enter_shortcut.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.enter_shortcut.activated.connect(self._execute_cmd)

        self.numpad_enter_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Enter), self)
        self.numpad_enter_shortcut.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.numpad_enter_shortcut.activated.connect(self._execute_cmd)

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
            self.cmd_desc_label.setText(self.gcode_dict[cmd][0])
            axes = self._get_active_axes()
            for p in self.gcode_dict[cmd][1:]:
                params = axes if p == 'A' else [p]
                for param in params:
                    row = QtWidgets.QWidget()
                    l = QtWidgets.QHBoxLayout(row)
                    l.setContentsMargins(0, 2, 0, 2)
                    
                    lbl = QtWidgets.QLabel(param)
                    lbl.setFixedWidth(50)
                    lbl.setStyleSheet("font-size: 18pt; font-weight: bold;")
                    
                    edit = QtWidgets.QLineEdit()
                    edit.setStyleSheet("font-size: 18pt;")
                    edit.setMinimumHeight(45)
                    edit.setAttribute(QtCore.Qt.WA_InputMethodEnabled, False)
                    edit.textChanged.connect(self._update_target)
                    
                    l.addWidget(lbl)
                    l.addWidget(edit)
                    self.args_layout.addWidget(row)
                    self.arg_fields[param] = edit
        else:
            self.cmd_desc_label.setText("")
            
        self._update_target()

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
        all_fields = [self.cmd_edit] + list(self.arg_fields.values())
        if f in all_fields:
            idx = (all_fields.index(f) + 1) % len(all_fields)
            all_fields[idx].setFocus()
        else:
            self.cmd_edit.setFocus()

    def _execute_cmd(self):
        if not self.target_input: return
        
        if self.cmd_edit.text().strip():
            self._update_target()
        
        command_text = self.target_input.text().strip()
        if command_text:
            self.target_input.returnPressed.emit()
            self.cmd_edit.clear()
            self.cmd_desc_label.setText("")
            self.target_input.clear()
            self.target_input.clearFocus()
            
            if self.close_callback:
                self.close_callback()


class MdiFocusFilter(QtCore.QObject):
    def __init__(self, stacked_widget, target_widget, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.target_widget = target_widget
        self.prev_index = 0

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.FocusIn:
            current = self.stacked_widget.currentWidget()
            
            if current != self.target_widget:
                self.prev_index = self.stacked_widget.currentIndex()
                self.stacked_widget.setCurrentWidget(self.target_widget)
            
            QtCore.QTimer.singleShot(50, self.target_widget.cmd_edit.setFocus)
            
            return False 
            
        return False

    def return_to_previous(self):
        self.stacked_widget.setCurrentIndex(self.prev_index)