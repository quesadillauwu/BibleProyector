# BibleProyector

**BibleProyector** es un software de código abierto diseñado para la proyección de textos bíblicos en doble pantalla (monitor de control + proyector físico). Está optimizado para servicios en iglesias, ofreciendo una interfaz moderna, rápida y un motor de fondos dinámicos.

## Características Principales
* **Selección Ágil:** Navegación rápida por Libro, Capítulo y Versículo mediante menús desplegables.
* **Doble Pantalla Nativa:** Panel de control independiente de la pantalla de proyección.
* **Motor de Fondos (Backgrounds):**
    * *Color sólido:* Selector de matiz/saturación integrado.
    * *Imágenes estáticas:* Soporte para alta resolución con filtro *Blur* (desenfoque) ajustable en tiempo real.
    * *Fondos animados:* Reproducción nativa de video (MP4/MOV) en bucle (loop) infinito para "Motion Backgrounds".
* **Interfaz Moderna:** Diseño dark-mode con acentos visuales y sombras dinámicas.
* **Multiplataforma:** Desarrollado en Python, compatible con Windows, Linux y macOS.

## Especificaciones Técnicas (Tech Stack)
* **Lenguaje:** Python 3.10+
* **Interfaz Gráfica:** PyQt6 (Qt)
* **Procesamiento de Imagen:** Pillow (PIL)
* **Motor Multimedia:** PyQt6-QtMultimedia (GStreamer en Linux / Media Foundation en Windows)
* **Fuente de Datos:** Archivo JSON local (`RVA2015_vid_1782.json`). El archivo JSON con el texto bíblico (`RVA2015_vid_1782.json`) utilizado en este proyecto fue obtenido del repositorio [mrk214](https://github.com/mrk214/bible-data-es-spa). ¡Agradecemos su esfuerzo por digitalizar y compartir la Palabra!

---

## Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto en cualquier computadora nueva.

### 1. Clonar el repositorio
Abre una terminal (o PowerShell en Windows) y descarga el código:
```bash
git clone https://github.com/quesadillauwu/BibleProyector.git
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
Con el entorno activado `(venv)`, instala los requerimientos:
```bash
pip install -r requirements.txt
```
*(Nota para usuarios Linux: Si los videos MP4 no se reproducen, asegúrate de tener instalados los códecs de tu sistema: `sudo apt install gstreamer1.0-libav gstreamer1.0-plugins-good`)*

### 4. Ejecutar el Proyector
Asegúrate de que el archivo JSON de la Biblia esté en la misma carpeta que el script principal.
```bash
python main.py
```

---

## Cómo Usar el Gestor

1.  **Conectar Pantalla:** Si tienes un proyector conectado, marca la casilla *"Pantalla completa (proyector físico)"* y presiona el botón verde **ABRIR PANTALLA**. El texto se lanzará automáticamente al segundo monitor.
2.  **Buscar Versículo:** Usa la tarjeta central para seleccionar Libro, Capítulo y Versículo. Verás una vista previa del texto.
3.  **Proyectar:** Presiona el botón morado **✦ PROYECTAR** para mandar el texto a la pantalla principal.
4.  **Cambiar Fondo:** En la barra lateral izquierda, selecciona el tipo de fondo. Puedes ajustar la oscuridad (dim) para mejorar el contraste del texto dorado/blanco con tu imagen o video.

---

## Flujo de Trabajo (Para Desarrolladores)

Si haces modificaciones en el código y quieres guardar los cambios en la nube (GitHub), usa los siguientes comandos en la terminal, o utiliza el panel de **Source Control** en VS Code:

```bash
# 1. Preparar los archivos modificados
git add .

# 2. Guardar la versión con un mensaje descriptivo
git commit -m "Agregada nueva función X"

# 3. Subir los cambios al repositorio
git push
```
Para descargar las últimas actualizaciones en otra computadora, simplemente usa: `git pull`.
