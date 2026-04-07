# BibleProyector 

![Python Version](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)
![License](https://img.shields.io/badge/Licencia-Open%20Source-success)

**BibleProyector** es un software gratuito y de código abierto diseñado para la proyección de textos bíblicos en pantallas secundarias. Está optimizado para servicios en iglesias, ofreciendo una interfaz elegante, rápida y un potente motor de fondos multimedia.

*(Agrega aquí una captura de pantalla de tu programa)*
> `![Interfaz de BibleProyector](ruta_de_tu_imagen.png)`

##  Características Principales
* **Selección Ágil:** Navegación ultra rápida por Libro, Capítulo y Versículo.
* **Doble Pantalla Nativa:** Panel de control independiente de la pantalla de proyección (soporte para proyector físico o captura vía OBS).
* **Motor de Fondos (Backgrounds):**
    * *Color sólido:* Selector de paleta integrado.
    * *Imágenes estáticas:* Soporte para alta resolución con filtro *Blur* (desenfoque) ajustable en tiempo real.
    * *Fondos animados:* Reproducción nativa de video (MP4/MOV) en bucle infinito (Motion Backgrounds).
    * *Filtro de Oscuridad (Dim):* Mejora el contraste del texto sobre fondos claros.
* **Transiciones Suaves:** Efecto de desvanecimiento (*crossfade*) al cambiar de versículo.
* **Interfaz Elegante:** Diseño "Material Dark" profesional y sin distracciones.

---

##  Descarga Rápida (Para Usuarios de Windows)

Si solo quieres usar el programa en tu iglesia y no eres programador, no necesitas instalar Python. 

1. Ve a la sección de **[Releases](https://github.com/quesadillauwu/BibleProyector/releases)** a la derecha de esta página.
2. Descarga el archivo `BibleProyector_v1.0_Windows.rar` (o `.zip`).
3. Descomprime la carpeta en tu computadora.
4. Ejecuta el archivo `BibleProyector.exe`. ¡No requiere instalación!

---

##  Soporte, Dudas y Sugerencias

¿Tienes alguna idea para mejorar el programa, encontraste un error, o necesitas ayuda para conectarlo a tu proyector? 
¡Únete a nuestra comunidad en la pestaña de **[Discussions](https://github.com/quesadillauwu/BibleProyector/discussions)**! Ahí respondemos dudas y tomamos nota para futuras actualizaciones.

---

##  Instalación y Compilación (Para Desarrolladores)

Si eres desarrollador y deseas modificar el código fuente, sigue estos pasos:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/quesadillauwu/BibleProyector.git](https://github.com/quesadillauwu/BibleProyector.git)
cd BibleProyector
```

### 2. Crear un Entorno Virtual
Es indispensable para aislar las librerías del sistema.

**En Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar Dependencias
Con el entorno activado, instala los requerimientos:
```bash
pip install -r requirements.txt
```
*(Nota para usuarios Linux: Si los videos MP4 no se reproducen, asegúrate de tener instalados los códecs de tu sistema: `sudo apt install gstreamer1.0-libav gstreamer1.0-plugins-good`)*

### 4. Ejecutar el Código
Asegúrate de que el archivo JSON de la Biblia esté en la misma carpeta que el script principal.
```bash
python main.py
```

### Flujo de Trabajo con Git
Para guardar tus modificaciones en la nube:
```bash
git add .
git commit -m "Agregada nueva función X"
git push
```

---

##  Especificaciones Técnicas (Tech Stack)
* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica:** PyQt6 (Qt)
* **Procesamiento de Imagen:** Pillow (PIL)
* **Motor Multimedia:** PyQt6-QtMultimedia (GStreamer en Linux / Media Foundation en Windows)
* **Fuente de Datos:** El archivo JSON con el texto bíblico (`RVA2015_vid_1782.json`) utilizado en este proyecto fue obtenido del increíble repositorio de [mrk214](https://github.com/mrk214/bible-data-es-spa). ¡Agradecemos su esfuerzo por digitalizar y compartir la Palabra!
