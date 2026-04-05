import sys
import json
import traceback
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QPushButton, QComboBox, QHBoxLayout, QSpinBox,
                             QCheckBox, QFileDialog, QFrame, QSizePolicy,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient, QPalette

# ─────────────────────────────────────────────
#  PALETA GLOBAL
# ─────────────────────────────────────────────
DARK_BG      = "#0D0D0F"
PANEL_BG     = "#13131A"
CARD_BG      = "#1A1A26"
BORDER       = "#2A2A3F"
ACCENT       = "#7C5CBF"        # púrpura sagrado
ACCENT_GLOW  = "#9D7DE8"
GOLD         = "#C9A94D"
TEXT_PRIMARY = "#E8E6F0"
TEXT_MUTED   = "#6B6885"
SUCCESS      = "#2ECC71"
INFO         = "#3498DB"
DANGER       = "#E74C3C"

STYLESHEET_GLOBAL = f"""
QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'DejaVu Sans', sans-serif;
    font-size: 10pt;
}}

/* ── Combo Box ── */
QComboBox {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {ACCENT};
    min-height: 28px;
}}
QComboBox:hover {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {ACCENT_GLOW};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    selection-background-color: {ACCENT};
    outline: none;
    padding: 4px;
}}

/* ── SpinBox ── */
QSpinBox {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    color: {TEXT_PRIMARY};
    min-height: 28px;
}}
QSpinBox:hover {{
    border-color: {ACCENT};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BORDER};
    border-radius: 4px;
    width: 18px;
    margin: 2px;
}}
QSpinBox::up-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid {ACCENT_GLOW};
}}
QSpinBox::down-arrow {{
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {ACCENT_GLOW};
}}

/* ── CheckBox ── */
QCheckBox {{
    spacing: 10px;
    color: {TEXT_MUTED};
}}
QCheckBox:hover {{
    color: {TEXT_PRIMARY};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {BORDER};
    background: {CARD_BG};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT_GLOW};
    image: none;
}}

/* ── Scrollbars ── */
QScrollBar:vertical {{
    background: {CARD_BG};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {ACCENT};
    border-radius: 3px;
    min-height: 20px;
}}
"""


def make_shadow(color=ACCENT, blur=20, offset=(0, 4)):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(color))
    shadow.setOffset(*offset)
    return shadow


def section_label(text):
    lbl = QLabel(text.upper())
    lbl.setStyleSheet(f"""
        color: {TEXT_MUTED};
        font-size: 8pt;
        font-weight: 700;
        letter-spacing: 2px;
        padding-bottom: 4px;
    """)
    return lbl


def divider():
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {BORDER}; background: {BORDER}; max-height: 1px;")
    return line


# ─────────────────────────────────────────────
#  BOTONES PERSONALIZADOS
# ─────────────────────────────────────────────
class StyledButton(QPushButton):
    def __init__(self, text, color_bg, color_hover, color_text="white",
                 icon_char="", bold=True):
        super().__init__(f"{icon_char}  {text}" if icon_char else text)
        self._bg = color_bg
        self._hover = color_hover
        self._text = color_text
        self._bold = bold
        self._apply(self._bg)

    def _apply(self, bg):
        weight = "700" if self._bold else "500"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {self._text};
                border: none;
                border-radius: 10px;
                padding: 10px 18px;
                font-weight: {weight};
                font-size: 10pt;
                letter-spacing: 0.5px;
            }}
            QPushButton:pressed {{
                background-color: {self._hover};
                padding-top: 12px;
            }}
        """)

    def enterEvent(self, e):
        self._apply(self._hover)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._apply(self._bg)
        super().leaveEvent(e)


# ─────────────────────────────────────────────
#  PANTALLA DE PROYECCIÓN
# ─────────────────────────────────────────────
class PantallaProyeccion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proyección — Pantalla Secundaria")
        self.setObjectName("fondo_principal")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.bg_color = "black"
        self.font_color = "white"
        self.font_family = "Georgia"
        self.font_size = 45
        self.background_image = ""

        layout = QVBoxLayout()
        layout.setContentsMargins(60, 60, 60, 40)

        self.label_texto = QLabel("Listo para proyectar")
        self.label_texto.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_texto.setWordWrap(True)

        self.label_ref = QLabel("")
        self.label_ref.setAlignment(Qt.AlignmentFlag.AlignRight)

        layout.addWidget(self.label_texto, stretch=1)
        layout.addWidget(self.label_ref)
        self.setLayout(layout)
        self.actualizar_estilos()

    def actualizar_estilos(self):
        self.label_texto.setStyleSheet(f"""
            color: {self.font_color};
            font-family: '{self.font_family}';
            font-size: {self.font_size}pt;
            background: transparent;
            line-height: 1.5;
        """)
        self.label_ref.setStyleSheet(f"""
            color: {self.font_color};
            font-family: '{self.font_family}';
            font-size: {int(self.font_size * 0.55)}pt;
            font-style: italic;
            background: transparent;
            opacity: 0.75;
            padding-bottom: 10px;
        """)
        if self.background_image:
            ruta = self.background_image.replace("\\", "/")
            self.setStyleSheet(f"""
                #fondo_principal {{
                    border-image: url('{ruta}');
                    background-color: black;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                #fondo_principal {{
                    background-color: {self.bg_color};
                }}
            """)


# ─────────────────────────────────────────────
#  PANEL DE CONTROL REDISEÑADO
# ─────────────────────────────────────────────
class PanelControl(QWidget):
    def __init__(self, ventana_proyeccion):
        super().__init__()
        self.proyector = ventana_proyeccion
        self.biblia = self.cargar_datos()

        self.setWindowTitle("Gestor de Proyección Bíblica")
        self.setMinimumSize(800, 560)
        self.setStyleSheet(STYLESHEET_GLOBAL)

        # Layout raíz: sidebar izquierdo + área principal
        root = QHBoxLayout()
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        # ── SIDEBAR ──────────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"""
            background-color: {PANEL_BG};
            border-right: 1px solid {BORDER};
        """)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)
        sb_layout.setSpacing(0)

        # Logo / título
        header = QWidget()
        header.setFixedHeight(100)
        header.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 {ACCENT},
                stop:1 {PANEL_BG}
            );
            border-bottom: 1px solid {BORDER};
        """)
        h_lay = QVBoxLayout(header)
        h_lay.setContentsMargins(20, 16, 20, 12)

        cross = QLabel("✝")
        cross.setStyleSheet(f"color: white; font-size: 22pt; background: transparent;")
        cross.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_title = QLabel("PROYECTOR")
        app_title.setStyleSheet(f"""
            color: white;
            font-size: 10pt;
            font-weight: 800;
            letter-spacing: 4px;
            background: transparent;
        """)
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        h_lay.addWidget(cross)
        h_lay.addWidget(app_title)
        sb_layout.addWidget(header)

        # Opciones de estilo en sidebar
        style_area = QWidget()
        style_area.setStyleSheet("background: transparent;")
        sa = QVBoxLayout(style_area)
        sa.setContentsMargins(16, 20, 16, 20)
        sa.setSpacing(14)

        sa.addWidget(section_label("Fondo"))
        self.combo_fondo = QComboBox()
        self.combo_fondo.addItems([
            "Black", "DarkBlue", "DarkRed", "DarkGreen", "Navy", "DimGray"
        ])
        self.combo_fondo.currentTextChanged.connect(self.cambiar_fondo_color)
        sa.addWidget(self.combo_fondo)

        self.btn_img_fondo = StyledButton(
            "Imagen de fondo", "#2A2A3F", ACCENT, icon_char="🖼", bold=False
        )
        self.btn_img_fondo.clicked.connect(self.elegir_imagen_fondo)
        sa.addWidget(self.btn_img_fondo)

        sa.addWidget(divider())
        sa.addWidget(section_label("Tipografía"))

        self.combo_fuente = QComboBox()
        self.combo_fuente.addItems([
            "Georgia", "Times New Roman", "Verdana",
            "Montserrat", "DejaVu Sans", "Arial"
        ])
        self.combo_fuente.currentTextChanged.connect(self.cambiar_fuente)
        sa.addWidget(self.combo_fuente)

        row_size = QHBoxLayout()
        row_size.addWidget(QLabel("Tamaño:"))
        self.spin_size = QSpinBox()
        self.spin_size.setRange(16, 150)
        self.spin_size.setValue(45)
        self.spin_size.valueChanged.connect(self.cambiar_tamano)
        row_size.addWidget(self.spin_size)
        sa.addLayout(row_size)

        sa.addWidget(divider())

        self.check_pantalla_completa = QCheckBox("Pantalla completa\n(proyector físico)")
        sa.addWidget(self.check_pantalla_completa)

        sa.addStretch()
        sb_layout.addWidget(style_area, stretch=1)

        # ── ÁREA PRINCIPAL ────────────────────────────
        main_area = QWidget()
        main_area.setStyleSheet(f"background-color: {DARK_BG};")
        ma = QVBoxLayout(main_area)
        ma.setContentsMargins(32, 28, 32, 24)
        ma.setSpacing(20)

        # Título sección
        page_title = QLabel("Selección de Versículo")
        page_title.setStyleSheet(f"""
            color: {TEXT_PRIMARY};
            font-size: 16pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        ma.addWidget(page_title)

        subtitle = QLabel("Navega el texto sagrado y proyéctalo en pantalla")
        subtitle.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt;")
        ma.addWidget(subtitle)

        ma.addWidget(divider())

        # ── Tarjeta de selección ──
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

        self.combo_libro = QComboBox()
        self.combo_libro.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        lbl_cap = QLabel("Cap.")
        lbl_cap.setStyleSheet(f"color: {TEXT_MUTED}; min-width: 28px;")
        self.combo_capitulo = QComboBox()
        self.combo_capitulo.setFixedWidth(72)
        lbl_ver = QLabel("Ver.")
        lbl_ver.setStyleSheet(f"color: {TEXT_MUTED}; min-width: 28px;")
        self.combo_versiculo = QComboBox()
        self.combo_versiculo.setFixedWidth(90)

        sel_row.addWidget(self.combo_libro)
        sel_row.addWidget(lbl_cap)
        sel_row.addWidget(self.combo_capitulo)
        sel_row.addWidget(lbl_ver)
        sel_row.addWidget(self.combo_versiculo)
        c_lay.addLayout(sel_row)

        # Vista previa del versículo
        self.preview_label = QLabel("—")
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.preview_label.setStyleSheet(f"""
            color: {GOLD};
            font-size: 10pt;
            font-style: italic;
            background: {DARK_BG};
            border-radius: 8px;
            padding: 12px 14px;
            line-height: 1.6;
        """)
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setMaximumHeight(140)
        c_lay.addWidget(self.preview_label)

        # Referencia
        self.ref_label = QLabel("")
        self.ref_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9pt; padding-left: 4px;")
        c_lay.addWidget(self.ref_label)

        ma.addWidget(card)

        # ── Botones de acción ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_lanzar = StyledButton(
            "ABRIR PANTALLA", "#1E2A1E", SUCCESS, icon_char="📺", bold=True
        )
        self.btn_lanzar.clicked.connect(self.alternar_proyector)

        self.btn_proyectar = StyledButton(
            "PROYECTAR", ACCENT, ACCENT_GLOW, icon_char="✦", bold=True
        )
        self.btn_proyectar.setMinimumHeight(52)
        self.btn_proyectar.setGraphicsEffect(make_shadow(ACCENT_GLOW, blur=25))
        self.btn_proyectar.clicked.connect(self.enviar_texto)
        self.btn_proyectar.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 14px 24px;
                font-weight: 700;
                font-size: 12pt;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_GLOW};
            }}
            QPushButton:pressed {{
                background-color: #6A4DAF;
            }}
        """)

        btn_row.addWidget(self.btn_lanzar, stretch=1)
        btn_row.addWidget(self.btn_proyectar, stretch=2)
        ma.addLayout(btn_row)

        # Status bar
        self.status_lbl = QLabel("● Sin conexión con pantalla")
        self.status_lbl.setStyleSheet(f"color: {DANGER}; font-size: 8pt;")
        ma.addWidget(self.status_lbl)

        ma.addStretch()

        # ── Unir sidebar + main ──
        root.addWidget(sidebar)
        root.addWidget(main_area, stretch=1)
        self.setLayout(root)

        self.inicializar_selectores()

    # ─── DATOS ───────────────────────────────────
    def cargar_datos(self):
        nombre_archivo = 'RVA2015_vid_1782.json'
        try:
            with open(nombre_archivo, 'r', encoding='utf-8-sig') as f:
                datos = json.load(f)
                return datos['books'] if isinstance(datos, dict) and 'books' in datos else datos
        except FileNotFoundError:
            print(f"Error: No se encontró '{nombre_archivo}'.")
            return []

    def inicializar_selectores(self):
        if not self.biblia:
            return
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
                        if not nums:
                            continue
                        num_str = (f"{nums[0]}-{nums[-1]}"
                                   if len(nums) > 1 else str(nums[0]))
                        texto = ""
                        if item.get('rlw_lines'):
                            texto = "\n".join(
                                " ".join(s.get('text', '') for s in r)
                                for r in item['rlw_lines']
                            )
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

    # ─── ESTILO / FONDO ──────────────────────────
    def elegir_imagen_fondo(self):
        archivo, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen de fondo", "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if archivo:
            self.proyector.background_image = archivo
            self.proyector.actualizar_estilos()

    def cambiar_fondo_color(self, color):
        self.proyector.background_image = ""
        self.proyector.bg_color = color.lower()
        self.proyector.actualizar_estilos()

    def cambiar_fuente(self, fuente):
        self.proyector.font_family = fuente
        self.proyector.actualizar_estilos()

    def cambiar_tamano(self, valor):
        self.proyector.font_size = valor
        self.proyector.actualizar_estilos()

    # ─── ACCIONES ────────────────────────────────
    def alternar_proyector(self):
        if self.proyector.isVisible():
            self.proyector.hide()
            self.btn_lanzar.setText("📺  ABRIR PANTALLA")
            self.status_lbl.setText("● Sin conexión con pantalla")
            self.status_lbl.setStyleSheet(f"color: {DANGER}; font-size: 8pt;")
        else:
            if self.check_pantalla_completa.isChecked():
                screens = QApplication.screens()
                if len(screens) > 1:
                    self.proyector.move(screens[1].geometry().topLeft())
                    self.proyector.showFullScreen()
                else:
                    self.proyector.showFullScreen()
            else:
                self.proyector.resize(1280, 720)
                self.proyector.showNormal()
            self.btn_lanzar.setText("⏹  CERRAR PANTALLA")
            self.status_lbl.setText("● Pantalla activa")
            self.status_lbl.setStyleSheet(f"color: {SUCCESS}; font-size: 8pt;")

    def enviar_texto(self):
        idx_l = self.combo_libro.currentIndex()
        idx_c = self.combo_capitulo.currentIndex()
        num_str = self.combo_versiculo.currentText()
        if idx_l >= 0 and idx_c >= 0 and num_str:
            if hasattr(self, 'versiculos_diccionario'):
                texto = self.versiculos_diccionario.get(num_str, "")
                ref = (f"{self.combo_libro.currentText()} "
                       f"{self.combo_capitulo.currentText()}:{num_str}")
                self.proyector.label_texto.setText(texto)
                self.proyector.label_ref.setText(ref)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana_p = PantallaProyeccion()
    ventana_c = PanelControl(ventana_p)
    ventana_c.show()
    sys.exit(app.exec())