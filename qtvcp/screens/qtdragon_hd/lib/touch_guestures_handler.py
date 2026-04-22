from PyQt5 import QtCore, QtWidgets
from qtvcp.core import Status
STATUS = Status()

class GraphicsTouchFilter(QtCore.QObject):
    def __init__(self, target_widget, parent=None):
        super().__init__(parent)
        self.target = target_widget
        self.is_rotating = False

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Gesture:
            pinch = event.gesture(QtCore.Qt.PinchGesture)
            if pinch and pinch.state() == QtCore.Qt.GestureUpdated:
                scale = pinch.scaleFactor()
                if scale > 0:
                    self.target.distance = self.target.distance / scale
                    self.target.update()
                    return True

        elif event.type() in (QtCore.QEvent.TouchBegin, QtCore.QEvent.TouchUpdate, QtCore.QEvent.TouchEnd):
            points = event.touchPoints()
            
            if len(points) == 3:
                cx = int(sum(p.pos().x() for p in points) / 3.0)
                cy = int(sum(p.pos().y() for p in points) / 3.0)

                if not self.is_rotating:
                    self.is_rotating = True
                    stat = STATUS.stat
                    conv = 25.4 if stat.linear_units == 1 else 1.0
                    
                    self.target.xcenter = stat.actual_position[0] / conv
                    self.target.ycenter = stat.actual_position[1] / conv
                    self.target.zcenter = stat.actual_position[2] / conv
                    self.target.recordMouse(cx, cy)
                else:
                    self.target.rotateOrTranslate(cx, cy)
                    self.target.update()
                
                return True
            else:
                self.is_rotating = False

        return super().eventFilter(obj, event)