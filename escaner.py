import json

def escanear_json(nombre_archivo):
    print(f"\n--- INICIANDO ESCÁNER PARA: {nombre_archivo} ---")
    try:
        with open(nombre_archivo, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            
        if isinstance(data, dict):
            print("\n1. Llaves principales del archivo:")
            print("   ->", list(data.keys()))
            
            if 'books' in data:
                libros = data['books']
                print("\n2. La llave 'books' contiene una:", type(libros).__name__)
                
                if isinstance(libros, list) and len(libros) > 0:
                    libro = libros[0]
                    print("\n3. Llaves internas de un Libro (ej. Génesis):")
                    print("   ->", list(libro.keys()))
                    
                    if 'chapters' in libro:
                        capitulos = libro['chapters']
                        print("\n4. La llave 'chapters' contiene una:", type(capitulos).__name__)
                        
                        if isinstance(capitulos, list) and len(capitulos) > 0:
                            capitulo = capitulos[0]
                            print("\n5. El Capítulo 1 es de tipo:", type(capitulo).__name__)
                            
                            if isinstance(capitulo, dict):
                                llaves_cap = list(capitulo.keys())
                                print("\n6. Llaves dentro del Capítulo 1 (mostrando las primeras 15):")
                                print("   ->", llaves_cap[:15])
                                
                                # Si hay una llave que parezca versículo (ej. "1"), vemos qué tiene adentro
                                if "1" in capitulo:
                                    print("\n7. El versículo '1' contiene un:", type(capitulo["1"]).__name__)
                                    if isinstance(capitulo["1"], dict):
                                        print("   Sus llaves son ->", list(capitulo["1"].keys()))

        print("\n--- ESCANEO COMPLETADO ---")
        
    except Exception as e:
        print(f"Error al leer: {e}")

# Ejecutar el escáner
escanear_json('RVA2015_vid_1782.json')