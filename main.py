import sys
import json
import math
import io
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QPushButton, QComboBox, QHBoxLayout, QSpinBox,
                             QCheckBox, QFileDialog, QFrame, QSizePolicy,
                             QGraphicsDropShadowEffect, QSlider, QStackedWidget)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (QPixmap, QColor, QPainter, QPen, QImage,
                         QConicalGradient, QRadialGradient, QLinearGradient,
                         QBrush)
from PyQt6.QtCore import QBuffer

try:
    from PIL import Image, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ─────────────────────────────────────────────
#  PALETA
# ─────────────────────────────────────────────
DARK_BG      = "#0D0D0F"
PANEL_BG     = "#13131A"
CARD_BG      = "#1A1A26"
BORDER       = "#2A2A3F"
ACCENT       = "#7C5CBF"
ACCENT_GLOW  = "#9D7DE8"
GOLD         = "#C9A94D"
TEXT_PRIMARY = "#E8E6F0"
TEXT_MUTED   = "#6B6885"
SUCCESS      = "#2ECC71"
DANGER       = "#E74C3C"

STYLESHEET_GLOBAL = f"""
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'DejaVu Sans', sans-serif;
    font-size: 10pt;
}}
QComboBox {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 36px 6px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
    min-height: 28px;
}}
QComboBox:hover {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: right center;
    width: 30px;
    border: none;
    background: transparent;
}}
QComboBox::down-arrow {{ image: none; width: 0px; height: 0px; }}
QComboBox QAbstractItemView {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    outline: none;
    padding: 4px;
}}
QSpinBox {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 28px 6px 10px;
    color: {TEXT_PRIMARY};
    min-height: 28px;
    font-size: 11pt;
}}
QSpinBox:hover {{ border-color: {ACCENT}; }}
QSpinBox::up-button {{
    subcontrol-origin: border; subcontrol-position: top right;
    background: transparent; border: none; width: 22px; height: 16px;
}}
QSpinBox::down-button {{
    subcontrol-origin: border; subcontrol-position: bottom right;
    background: transparent; border: none; width: 22px; height: 16px;
}}
QSpinBox::up-arrow, QSpinBox::down-arrow {{ image: none; width: 0; height: 0; }}
QCheckBox {{ spacing: 10px; color: {TEXT_MUTED}; }}
QCheckBox:hover {{ color: {TEXT_PRIMARY}; }}
QCheckBox::indicator {{
    width: 18px; height: 18px; border-radius: 5px;
    border: 1px solid {BORDER}; background: {CARD_BG};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT}; border-color: {ACCENT_GLOW};
}}
QScrollBar:vertical {{ background: {CARD_BG}; width: 6px; border-radius: 3px; }}
QScrollBar::handle:vertical {{ background: {ACCENT}; border-radius: 3px; min-height: 20px; }}
QSlider::groove:horizontal {{
    height: 4px; background: {BORDER}; border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT_GLOW}; border: 2px solid {ACCENT};
    width: 14px; height: 14px; margin: -5px 0; border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{ background: white; border-color: {ACCENT_GLOW}; }}
QSlider::sub-page:horizontal {{ background: {ACCENT}; border-radius: 2px; }}
"""

# ─────────────────────────────────────────────
#  WIDGETS REUTILIZABLES
# ─────────────────────────────────────────────
class ArrowComboBox(QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(ACCENT_GLOW), 2.0, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        cx, cy, s = self.width() - 15, self.height() // 2, 4
        painter.drawLine(cx - s, cy - 2, cx, cy + 3)
        painter.drawLine(cx, cy + 3, cx + s, cy - 2)


class ArrowSpinBox(QSpinBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(ACCENT_GLOW), 2.0, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        w, h, cx, s = self.width(), self.height(), self.width() - 11, 3
        cy_up = h // 4
        painter.drawLine(cx - s, cy_up + s, cx, cy_up - s)
        painter.drawLine(cx, cy_up - s, cx + s, cy_up + s)
        cy_dn = h * 3 // 4
        painter.drawLine(cx - s, cy_dn - s, cx, cy_dn + s)
        painter.drawLine(cx, cy_dn + s, cx + s, cy_dn - s)


def make_shadow(color=ACCENT, blur=20, offset=(0, 4)):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(color))
    shadow.setOffset(*offset)
    return shadow

def section_label(text):
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:8pt;font-weight:700;"
                      f"letter-spacing:2px;padding-bottom:2px;background:transparent;")
    return lbl

def divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"background:{BORDER};border:none;")
    line.setFixedHeight(1)
    return line

def slider_row(label_text, lo, hi, default, on_change):
    row_lbl = QHBoxLayout()
    lbl = QLabel(label_text)
    lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:9pt;background:transparent;")
    val_lbl = QLabel(str(default))
    val_lbl.setStyleSheet(f"color:{ACCENT_GLOW};font-size:9pt;font-weight:700;background:transparent;")
    val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
    row_lbl.addWidget(lbl)
    row_lbl.addStretch()
    row_lbl.addWidget(val_lbl)

    sl = QSlider(Qt.Orientation.Horizontal)
    sl.setRange(lo, hi)
    sl.setValue(default)

    container = QVBoxLayout()
    container.setSpacing(4)
    container.addLayout(row_lbl)
    container.addWidget(sl)

    def _on_change(v):
        val_lbl.setText(str(v))
        on_change(v)

    sl.valueChanged.connect(_on_change)
    return container, sl, val_lbl


class StyledButton(QPushButton):
    def __init__(self, text, color_bg, color_hover, color_text="white",
                 icon_char="", bold=True):
        super().__init__(f"{icon_char}  {text}" if icon_char else text)
        self._bg, self._hover, self._text, self._bold = color_bg, color_hover, color_text, bold
        self._apply(self._bg)

    def _apply(self, bg):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg}; color: {self._text}; border: none;
                border-radius: 10px; padding: 10px 18px;
                font-weight: {"700" if self._bold else "500"};
                font-size: 10pt; letter-spacing: 0.5px;
            }}
            QPushButton:pressed {{ background-color: {self._hover}; padding-top: 12px; }}
        """)

    def enterEvent(self, e): self._apply(self._hover); super().enterEvent(e)
    def leaveEvent(self, e): self._apply(self._bg);    super().leaveEvent(e)


# ─────────────────────────────────────────────
#  COLOR PICKER (rueda HSV + cuadro SV)
# ─────────────────────────────────────────────
class HueRing(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 180)
        self._hue = 0
        self._dragging = False

    def hue(self): return self._hue
    def set_hue(self, h):
        self._hue = h % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        R_out, R_in = min(cx, cy) - 2, min(cx, cy) - 20

        steps = 360
        for i in range(steps):
            angle_start = -i
            color = QColor.fromHsv(i, 255, 255)
            painter.setPen(QPen(color, 0))
            painter.setBrush(QBrush(color))
            path_angle = 360 / steps + 0.5
            painter.drawPie(
                QRectF(cx - R_out, cy - R_out, R_out * 2, R_out * 2),
                int(angle_start * 16), int(path_angle * 16)
            )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(CARD_BG)))
        painter.drawEllipse(QRectF(cx - R_in, cy - R_in, R_in * 2, R_in * 2))

        # CORRECCIÓN DE ÁNGULO DEL INDICADOR
        angle_rad = math.radians(self._hue)
        R_mid = (R_out + R_in) / 2
        ix = cx + R_mid * math.cos(angle_rad)
        iy = cy + R_mid * math.sin(angle_rad)
        painter.setPen(QPen(QColor("white"), 2))
        painter.setBrush(QBrush(QColor.fromHsv(self._hue, 255, 255)))
        painter.drawEllipse(QPointF(ix, iy), 8, 8)

    def _hue_from_pos(self, x, y):
        cx, cy = self.width() / 2, self.height() / 2
        angle = math.degrees(math.atan2(y - cy, x - cx))
        # CORRECCIÓN: el ángulo ahora sigue la misma orientación que el dibujo
        return int(angle) % 360

    def _in_ring(self, x, y):
        cx, cy = self.width() / 2, self.height() / 2
        R_out = min(cx, cy) - 2
        R_in  = min(cx, cy) - 20
        d = math.hypot(x - cx, y - cy)
        return R_in <= d <= R_out

    def mousePressEvent(self, e):
        if self._in_ring(e.position().x(), e.position().y()):
            self._dragging = True
            self._update_hue(e.position().x(), e.position().y())

    def mouseMoveEvent(self, e):
        if self._dragging:
            self._update_hue(e.position().x(), e.position().y())

    def mouseReleaseEvent(self, e):
        self._dragging = False

    def _update_hue(self, x, y):
        self._hue = self._hue_from_pos(x, y)
        self.update()
        if hasattr(self, '_on_hue_changed'):
            self._on_hue_changed(self._hue)


class SVSquare(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # CORRECCIÓN DE TAMAÑO: 96x96 encaja perfectamente dentro del hueco de 140px
        self.setFixedSize(96, 96)
        self._hue = 0
        self._sat = 255
        self._val = 200
        self._dragging = False

    def set_hue(self, h):
        self._hue = h
        self.update()

    def color(self):
        return QColor.fromHsv(self._hue, self._sat, self._val)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        rect = QRectF(0, 0, w, h)

        grad_h = QLinearGradient(0, 0, w, 0)
        grad_h.setColorAt(0, QColor("white"))
        grad_h.setColorAt(1, QColor.fromHsv(self._hue, 255, 255))
        painter.fillRect(rect, grad_h)

        grad_v = QLinearGradient(0, 0, 0, h)
        grad_v.setColorAt(0, QColor(0, 0, 0, 0))
        grad_v.setColorAt(1, QColor(0, 0, 0, 255))
        painter.fillRect(rect, grad_v)

        cx = self._sat / 255 * w
        cy = (1 - self._val / 255) * h
        painter.setPen(QPen(QColor("white"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), 6, 6)

    def _update_sv(self, x, y):
        w, h = self.width(), self.height()
        self._sat = max(0, min(255, int(x / w * 255)))
        self._val = max(0, min(255, int((1 - y / h) * 255)))
        self.update()
        if hasattr(self, '_on_color_changed'):
            self._on_color_changed(self.color())

    def mousePressEvent(self, e):
        self._dragging = True
        self._update_sv(e.position().x(), e.position().y())

    def mouseMoveEvent(self, e):
        if self._dragging:
            self._update_sv(e.position().x(), e.position().y())

    def mouseReleaseEvent(self, e):
        self._dragging = False


class ColorPicker(QWidget):
    def __init__(self, on_color_changed, parent=None):
        super().__init__(parent)
        self._callback = on_color_changed
        self.setStyleSheet("background:transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.ring = HueRing()
        self.sv   = SVSquare()

        container = QWidget()
        container.setFixedSize(180, 180)
        self.ring.setParent(container)
        self.ring.move(0, 0)
        self.sv.setParent(container)
        
        # CORRECCIÓN DE CENTRADO (calculado en base a 96px)
        sv_x = (180 - 96) // 2
        sv_y = (180 - 96) // 2
        self.sv.move(sv_x, sv_y)

        row.addStretch()
        row.addWidget(container)
        row.addStretch()
        layout.addLayout(row)

        self.color_preview = QLabel()
        self.color_preview.setFixedHeight(28)
        self.color_preview.setStyleSheet(
            "border-radius: 6px; border: 1px solid #2A2A3F;"
        )
        self.hex_label = QLabel("#ffffff")
        self.hex_label.setStyleSheet(
            f"color:{TEXT_MUTED};font-size:9pt;background:transparent;"
        )
        self.hex_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.color_preview)
        layout.addWidget(self.hex_label)

        self.ring._on_hue_changed = self._hue_changed
        self.sv._on_color_changed  = self._color_changed
        self._update_preview(self.sv.color())

    def _hue_changed(self, h):
        self.sv.set_hue(h)
        self._update_preview(self.sv.color())

    def _color_changed(self, color):
        self._update_preview(color)

    def _update_preview(self, color):
        self.color_preview.setStyleSheet(
            f"background-color: {color.name()}; border-radius:6px; border:1px solid #2A2A3F;"
        )
        self.hex_label.setText(color.name().upper())
        self._callback(color)


# ─────────────────────────────────────────────
#  PANEL DE FONDO 
# ─────────────────────────────────────────────
class PanelFondo(QWidget):
    def __init__(self, proyector, parent=None):
        super().__init__(parent)
        self.proyector = proyector
        self.setStyleSheet("background:transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(section_label("Fondo"))

        self.combo_modo = ArrowComboBox()
        self.combo_modo.addItems(["🎨  Color sólido", "🖼  Imagen", "✨  Animado"])
        layout.addWidget(self.combo_modo)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")

        self.panel_color  = self._build_panel_color()
        self.panel_imagen = self._build_panel_imagen()
        self.panel_anim   = self._build_panel_animado()

        self.stack.addWidget(self.panel_color)   
        self.stack.addWidget(self.panel_imagen)  
        self.stack.addWidget(self.panel_anim)    

        layout.addWidget(self.stack)
        layout.addStretch()

        self.combo_modo.currentIndexChanged.connect(self._cambiar_modo)
        self._cambiar_modo(0)

    def _build_panel_color(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(8)
        self.color_picker = ColorPicker(self._on_color_picked)
        lay.addWidget(self.color_picker)
        return w

    def _build_panel_imagen(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(10)

        btn = StyledButton("Subir imagen", "#2A2A3F", ACCENT, icon_char="🖼", bold=False)
        btn.clicked.connect(self._elegir_imagen)
        lay.addWidget(btn)

        self.lbl_imagen = QLabel("Sin imagen")
        self.lbl_imagen.setStyleSheet(
            f"color:{TEXT_MUTED};font-size:8pt;background:transparent;"
            f"padding:4px 0;"
        )
        self.lbl_imagen.setWordWrap(True)
        lay.addWidget(self.lbl_imagen)

        lay.addWidget(divider())

        sl_blur, self.slider_blur, _ = slider_row(
            "Blur", 0, 10, 0,
            lambda v: self.proyector.set_blur(v)
        )
        lay.addLayout(sl_blur)

        sl_dim, self.slider_dim, _ = slider_row(
            "Oscuridad", 0, 100, 0,
            lambda v: self.proyector.set_dim(int(v / 100 * 220))
        )
        lay.addLayout(sl_dim)

        return w

    def _build_panel_animado(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 8, 0, 0)
        lbl = QLabel("Próximamente…")
        lbl.setStyleSheet(f"color:{TEXT_MUTED};font-size:9pt;background:transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)
        lay.addStretch()
        return w

    def _cambiar_modo(self, idx):
        self.stack.setCurrentIndex(idx)
        if idx == 0: 
            self.proyector.background_image = ""
            self.proyector.actualizar_estilos()
            self._on_color_picked(self.color_picker.sv.color())
        elif idx == 2: 
            self.proyector.background_image = ""
            self.proyector.bg_color = "black"
            self.proyector.actualizar_estilos()

    def _on_color_picked(self, color: QColor):
        self.proyector.background_image = ""
        self.proyector.bg_color = color.name()
        self.proyector.actualizar_estilos()

    def _elegir_imagen(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if archivo:
            import os
            self.lbl_imagen.setText(os.path.basename(archivo))
            self.proyector.background_image = archivo
            self.proyector.actualizar_estilos()


# ─────────────────────────────────────────────
#  PANTALLA DE PROYECCIÓN
# ─────────────────────────────────────────────
class PantallaProyeccion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyección — Pantalla Secundaria")

        self._bg_color_str = "black"
        self.font_color    = "white"
        self.font_family   = "Georgia"
        self.font_size     = 45
        self.background_image  = ""
        self._pixmap           = None
        self._pixmap_blurred   = None
        self._last_blur_amount = -1
        self._last_size        = None
        self.blur_amount   = 0
        self.dim_alpha     = 0

        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 40)

        self.label_texto = QLabel("Listo para proyectar")
        self.label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_texto.setWordWrap(True)
        self.label_texto.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label_ref = QLabel("")
        self.label_ref.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_ref.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout.addWidget(self.label_texto, stretch=1)
        layout.addWidget(self.label_ref)
        self.setLayout(layout)
        self.actualizar_estilos()

    @property
    def bg_color(self): return self._bg_color_str

    @bg_color.setter
    def bg_color(self, v): self._bg_color_str = v if isinstance(v, str) else "black"

    def actualizar_estilos(self):
        self.label_texto.setStyleSheet(
            f"color:{self.font_color};font-family:'{self.font_family}';"
            f"font-size:{self.font_size}pt;background:transparent;"
        )
        self.label_ref.setStyleSheet(
            f"color:{self.font_color};font-family:'{self.font_family}';"
            f"font-size:{int(self.font_size*0.55)}pt;font-style:italic;background:transparent;"
        )
        if self.background_image:
            px = QPixmap(self.background_image)
            self._pixmap = px if not px.isNull() else None
        else:
            self._pixmap = None
            
        self._pixmap_blurred   = None
        self._last_blur_amount = -1
        self.setStyleSheet("")
        self.update()

    def _apply_blur(self):
        if not self._pixmap or self._pixmap.isNull():
            return None
        if self.blur_amount <= 0:
            return self._pixmap
            
        if (self._pixmap_blurred is not None and 
            self._last_blur_amount == self.blur_amount and
            self._last_size == self.size()):
            return self._pixmap_blurred
            
        if not PIL_AVAILABLE:
            print("Instala Pillow (pip install Pillow) para usar el Blur.")
            return self._pixmap

        # TRUCO DE RENDIMIENTO: Escalar la imagen a la MITAD de la pantalla 
        # antes del blur. Esto hace que el cálculo sea 4 veces más rápido,
        # eliminando el "lag" y los saltos sucios al mover el slider.
        target_size = self.size()
        fast_size = target_size / 2 
        
        base_px = self._pixmap.scaled(fast_size, 
                                      Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                      Qt.TransformationMode.SmoothTransformation)

        ba  = QBuffer()
        ba.open(QBuffer.OpenModeFlag.WriteOnly)
        base_px.save(ba, "PNG")
        ba.close()
        
        pil_img = Image.open(io.BytesIO(bytes(ba.data())))
        
        # Como la imagen es más pequeña, el radio no necesita ser tan agresivo.
        # Al convertirlo a float, Pillow hace una transición de difuminado perfecta.
        radius = float(self.blur_amount)
        pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=radius)).convert("RGBA")
        
        w, h    = pil_img.size
        data    = pil_img.tobytes("raw", "RGBA")
        qimg    = QImage(data, w, h, QImage.Format.Format_RGBA8888).copy()
        
        self._pixmap_blurred   = QPixmap.fromImage(qimg)
        self._last_blur_amount = self.blur_amount
        self._last_size        = self.size()
        
        return self._pixmap_blurred

    def set_blur(self, value):
        self.blur_amount = value
        self.update()

    def set_dim(self, value):
        self.dim_alpha = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        px = self._apply_blur()
        if px and not px.isNull():
            scaled = px.scaled(self.size(),
                               Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)
            x = (self.width()  - scaled.width())  // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(self.rect(), QColor(self._bg_color_str))
        if self.dim_alpha > 0:
            painter.fillRect(self.rect(), QColor(0, 0, 0, self.dim_alpha))


# ─────────────────────────────────────────────
#  PANEL DE CONTROL
# ─────────────────────────────────────────────
class PanelControl(QWidget):
    def __init__(self, ventana_proyeccion):
        super().__init__()
        self.proyector = ventana_proyeccion
        self.biblia    = self.cargar_datos()

        self.setWindowTitle("Gestor de Proyección Bíblica")
        self.setMinimumSize(820, 580)
        self.setStyleSheet(STYLESHEET_GLOBAL)

        root = QHBoxLayout()
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── SIDEBAR ──
        sidebar = QWidget()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"background-color:{PANEL_BG};border-right:1px solid {BORDER};")
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 {ACCENT}, stop:1 {PANEL_BG});
            border-bottom: 1px solid {BORDER};
        """)
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(20, 14, 20, 10)
        cross = QLabel("✝")
        cross.setStyleSheet("color:white;font-size:20pt;background:transparent;")
        cross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title = QLabel("PROYECTOR")
        app_title.setStyleSheet(
            "color:white;font-size:9pt;font-weight:800;letter-spacing:4px;background:transparent;"
        )
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_lay.addWidget(cross)
        h_lay.addWidget(app_title)
        sb_layout.addWidget(header)

        # Área de controles 
        ctrl_area = QWidget()
        ctrl_area.setStyleSheet("background:transparent;")
        ca = QVBoxLayout(ctrl_area)
        ca.setContentsMargins(16, 16, 16, 16)
        ca.setSpacing(14)

        self.panel_fondo = PanelFondo(self.proyector)
        ca.addWidget(self.panel_fondo)

        ca.addWidget(divider())
        ca.addWidget(section_label("Tipografía"))

        self.combo_fuente = ArrowComboBox()
        self.combo_fuente.addItems(["Georgia","Times New Roman","Verdana",
                                    "Montserrat","DejaVu Sans","Arial"])
        self.combo_fuente.currentTextChanged.connect(
            lambda f: (setattr(self.proyector, 'font_family', f),
                       self.proyector.actualizar_estilos()))
        ca.addWidget(self.combo_fuente)

        row_size = QHBoxLayout()
        lbl_s = QLabel("Tamaño:")
        lbl_s.setStyleSheet(f"color:{TEXT_MUTED};")
        row_size.addWidget(lbl_s)
        self.spin_size = ArrowSpinBox()
        self.spin_size.setRange(16, 150)
        self.spin_size.setValue(45)
        self.spin_size.valueChanged.connect(
            lambda v: (setattr(self.proyector, 'font_size', v),
                       self.proyector.actualizar_estilos()))
        row_size.addWidget(self.spin_size)
        ca.addLayout(row_size)

        ca.addWidget(divider())
        self.check_pantalla_completa = QCheckBox("Pantalla completa\n(proyector físico)")
        ca.addWidget(self.check_pantalla_completa)
        ca.addStretch()

        sb_layout.addWidget(ctrl_area, stretch=1)

        # ── ÁREA PRINCIPAL ──
        main_area = QWidget()
        main_area.setStyleSheet(f"background-color:{DARK_BG};")
        ma = QVBoxLayout(main_area)
        ma.setContentsMargins(32, 28, 32, 24)
        ma.setSpacing(20)

        page_title = QLabel("Selección de Versículo")
        page_title.setStyleSheet(
            f"color:{TEXT_PRIMARY};font-size:16pt;font-weight:700;letter-spacing:0.5px;")
        ma.addWidget(page_title)

        subtitle = QLabel("Navega el texto sagrado y proyéctalo en pantalla")
        subtitle.setStyleSheet(f"color:{TEXT_MUTED};font-size:9pt;")
        ma.addWidget(subtitle)
        ma.addWidget(divider())

        # Tarjeta
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {CARD_BG};
                border: 1px solid {BORDER};
                border-radius: 14px;
            }}
        """)
        card.setGraphicsEffect(make_shadow(ACCENT, blur=30, offset=(0, 6)))
        c_lay = QVBoxLayout(card)
        c_lay.setContentsMargins(20, 18, 20, 18)
        c_lay.setSpacing(12)
        c_lay.addWidget(section_label("Libro · Capítulo · Versículo"))

        sel_row = QHBoxLayout()
        sel_row.setSpacing(10)
        self.combo_libro = ArrowComboBox()
        self.combo_libro.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lbl_cap = QLabel("Cap.")
        lbl_cap.setStyleSheet(f"color:{TEXT_MUTED};min-width:28px;")
        self.combo_capitulo = ArrowComboBox()
        self.combo_capitulo.setFixedWidth(90)
        lbl_ver = QLabel("Ver.")
        lbl_ver.setStyleSheet(f"color:{TEXT_MUTED};min-width:28px;")
        self.combo_versiculo = ArrowComboBox()
        self.combo_versiculo.setFixedWidth(90)
        sel_row.addWidget(self.combo_libro)
        sel_row.addWidget(lbl_cap)
        sel_row.addWidget(self.combo_capitulo)
        sel_row.addWidget(lbl_ver)
        sel_row.addWidget(self.combo_versiculo)
        c_lay.addLayout(sel_row)

        self.preview_label = QLabel("—")
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.preview_label.setStyleSheet(
            f"color:{GOLD};font-size:10pt;font-style:italic;"
            f"background:{DARK_BG};border-radius:8px;padding:12px 14px;"
        )
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setMaximumHeight(140)
        c_lay.addWidget(self.preview_label)

        self.ref_label = QLabel("")
        self.ref_label.setStyleSheet(f"color:{TEXT_MUTED};font-size:9pt;padding-left:4px;")
        c_lay.addWidget(self.ref_label)
        ma.addWidget(card)

        # Botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_lanzar = StyledButton("ABRIR PANTALLA","#1E2A1E",SUCCESS,icon_char="📺",bold=True)
        self.btn_lanzar.clicked.connect(self.alternar_proyector)

        self.btn_proyectar = QPushButton("✦  PROYECTAR")
        self.btn_proyectar.setMinimumHeight(52)
        self.btn_proyectar.setGraphicsEffect(make_shadow(ACCENT_GLOW, blur=25))
        self.btn_proyectar.clicked.connect(self.enviar_texto)
        self.btn_proyectar.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: white; border: none;
                border-radius: 12px; padding: 14px 24px;
                font-weight: 700; font-size: 14pt; letter-spacing: 1px;
            }}
            QPushButton:hover {{ background-color: {ACCENT_GLOW}; }}
            QPushButton:pressed {{ background-color: #6A4DAF; }}
        """)

        btn_row.addWidget(self.btn_lanzar, stretch=1)
        btn_row.addWidget(self.btn_proyectar, stretch=2)
        ma.addLayout(btn_row)

        self.status_lbl = QLabel("● Sin conexión con pantalla")
        self.status_lbl.setStyleSheet(f"color:{DANGER};font-size:8pt;")
        ma.addWidget(self.status_lbl)
        ma.addStretch()

        root.addWidget(sidebar)
        root.addWidget(main_area, stretch=1)
        self.setLayout(root)
        self.inicializar_selectores()

    # ─── DATOS ───
    def cargar_datos(self):
        try:
            with open('RVA2015_vid_1782.json', 'r', encoding='utf-8-sig') as f:
                datos = json.load(f)
                return datos['books'] if isinstance(datos, dict) and 'books' in datos else datos
        except FileNotFoundError:
            return []

    def inicializar_selectores(self):
        if not self.biblia: return
        for libro in self.biblia:
            nombre = libro.get('name', libro.get('book', libro.get('abbrev', 'Libro')))
            self.combo_libro.addItem(nombre)
        self.combo_libro.currentIndexChanged.connect(self.actualizar_capitulos)
        self.combo_capitulo.currentIndexChanged.connect(self.actualizar_versiculos)
        self.combo_versiculo.currentTextChanged.connect(self.actualizar_preview)
        self.actualizar_capitulos()

    def actualizar_capitulos(self):
        self.combo_capitulo.clear()
        idx = self.combo_libro.currentIndex()
        if idx >= 0:
            for i in range(1, len(self.biblia[idx]['chapters']) + 1):
                self.combo_capitulo.addItem(str(i))

    def actualizar_versiculos(self):
        self.combo_versiculo.clear()
        idx_l = self.combo_libro.currentIndex()
        idx_c = self.combo_capitulo.currentIndex()
        if idx_l >= 0 and idx_c >= 0:
            capitulo = self.biblia[idx_l]['chapters'][idx_c]
            self.versiculos_diccionario = {}
            if isinstance(capitulo, dict) and 'items' in capitulo:
                for item in capitulo['items']:
                    if item.get('type') == 'verse':
                        nums = item.get('verse_numbers', [])
                        if not nums: continue
                        num_str = (f"{nums[0]}-{nums[-1]}" if len(nums) > 1 else str(nums[0]))
                        texto = ""
                        if item.get('rlw_lines'):
                            texto = "\n".join(" ".join(s.get('text','') for s in r)
                                             for r in item['rlw_lines'])
                        elif item.get('lines'):
                            texto = "\n".join(item['lines'])
                        self.versiculos_diccionario[num_str] = texto
            for num in self.versiculos_diccionario:
                self.combo_versiculo.addItem(num)

    def actualizar_preview(self):
        num = self.combo_versiculo.currentText()
        if hasattr(self, 'versiculos_diccionario') and num:
            texto = self.versiculos_diccionario.get(num, "")
            self.preview_label.setText(texto[:300] + ("…" if len(texto) > 300 else ""))
            ref = (f"{self.combo_libro.currentText()} "
                   f"{self.combo_capitulo.currentText()}:{num}")
            self.ref_label.setText(ref)

    def alternar_proyector(self):
        if self.proyector.isVisible():
            self.proyector.hide()
            self.btn_lanzar.setText("📺  ABRIR PANTALLA")
            self.status_lbl.setText("● Sin conexión con pantalla")
            self.status_lbl.setStyleSheet(f"color:{DANGER};font-size:8pt;")
        else:
            if self.check_pantalla_completa.isChecked():
                screens = QApplication.screens()
                target = screens[1] if len(screens) > 1 else screens[0]
                self.proyector.move(target.geometry().topLeft())
                self.proyector.showFullScreen()
            else:
                self.proyector.resize(1280, 720)
                self.proyector.showNormal()
            self.btn_lanzar.setText("⏹  CERRAR PANTALLA")
            self.status_lbl.setText("● Pantalla activa")
            self.status_lbl.setStyleSheet(f"color:{SUCCESS};font-size:8pt;")

    def enviar_texto(self):
        idx_l   = self.combo_libro.currentIndex()
        idx_c   = self.combo_capitulo.currentIndex()
        num_str = self.combo_versiculo.currentText()
        if idx_l >= 0 and idx_c >= 0 and num_str and hasattr(self, 'versiculos_diccionario'):
            texto = self.versiculos_diccionario.get(num_str, "")
            ref   = (f"{self.combo_libro.currentText()} "
                     f"{self.combo_capitulo.currentText()}:{num_str}")
            self.proyector.label_texto.setText(texto)
            self.proyector.label_ref.setText(ref)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_p = PantallaProyeccion()
    ventana_c = PanelControl(ventana_p)
    ventana_c.show()
    sys.exit(app.exec())