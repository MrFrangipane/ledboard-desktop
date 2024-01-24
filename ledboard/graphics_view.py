from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QFrame, QGraphicsView


class GraphicsView(QGraphicsView):

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)

        self._zoom = 0
        self._drag_anchor = 0, 0

        self.setRenderHint(QPainter.Antialiasing, True)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)

        self._frustum = QRectF(0, 0, self.size().width(), self.size().height())
        self._update_frustum()

    def _update_frustum(self):
        self.setSceneRect(self._frustum)
        self.fitInView(self._frustum, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
        else:
            factor = 0.8

        position = self.mapToScene(event.position().toPoint())
        w = self._frustum.width() / factor
        h = self._frustum.height() / factor

        self._frustum = QRectF(
            position.x() - (position.x() - self._frustum.left()) / factor,
            position.y() - (position.y() - self._frustum.top()) / factor,
            w, h
        )
        self._update_frustum()

        QGraphicsView.wheelEvent(self, event)

    def mousePressEvent(self, event):
        self._drag_anchor = self.mapToScene(event.position().toPoint())

        QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        position = self.mapToScene(event.position().toPoint())
        delta = self._drag_anchor - position

        self._frustum.adjust(delta.x(), delta.y(), delta.x(), delta.y())
        self._update_frustum()

        QGraphicsView.mouseMoveEvent(self, event)

    # TODO
    """
    def resizeEvent(self, event):
        w, h = self.size().width(), self.size().height()
        if 0 in [w, h]:
            self.resize(self._last_size)
        delta = max(w / self._last_size.width(), h / self._last_size.height())
        self._set_viewer_zoom(delta)
        self._last_size = self.size()
        super(NodeViewer, self).resizeEvent(event)
    """
