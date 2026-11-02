import xml.etree.ElementTree as ET

class GeneradorKML:
    def __init__(self, archivo_xml, archivo_kml):
        self.archivo_xml = archivo_xml
        self.archivo_kml = archivo_kml
        
        self.ns = {'u': 'http://www.uniovi.es'}
        
        self.arbol = None
        self.raiz = None

    def cargar_xml(self):
        try:
            self.arbol = ET.parse(self.archivo_xml)
            self.raiz = self.arbol.getroot()
            print("XML cargado correctamente en memoria.")
        except Exception as e:
            print(f"Error al cargar el XML: {e}")

    def escribir_prologo_kml(self, archivo):
        prologo = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
    <name>Planimetría de la Etapa</name>
    <description>Ruta de la etapa de La Vuelta 2026 generada con Python</description>
    
    <!-- Estilo ROJO para Salida y Meta (ff0000ff) -->
    <Style id="estiloRojo">
        <IconStyle><color>ff0000ff</color><Icon><href>http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png</href></Icon></IconStyle>
    </Style>
    
    <!-- Estilo VERDE para Puertos de montaña (ff00ff00) -->
    <Style id="estiloVerde">
        <IconStyle><color>ff00ff00</color><Icon><href>http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png</href></Icon></IconStyle>
    </Style>
    
    <!-- Estilo AZUL para Sprints (ffff0000) -->
    <Style id="estiloAzul">
        <IconStyle><color>ffff0000</color><Icon><href>http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png</href></Icon></IconStyle>
    </Style>
    
    <!-- Estilo AMARILLO para Puntos Anónimos (ff00ffff) -->
    <Style id="estiloAmarillo">
        <IconStyle><color>ff00ffff</color><Icon><href>http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png</href></Icon></IconStyle>
    </Style>
    
    <!-- Estilo ROJO y con grosor 4 para la LÍNEA que une toda la ruta -->
    <Style id="estiloLinea">
        <LineStyle><color>ff0000ff</color><width>4</width></LineStyle>
    </Style>
"""
        archivo.write(prologo)

    def escribir_epilogo_kml(self, archivo):
        epilogo = """</Document>
</kml>
"""
        archivo.write(epilogo)


    def escribir_punto(self, archivo, nombre, descripcion, lon, lat, alt, estilo):
        punto = f"""    <Placemark>
        <name>{nombre}</name>
        <description>{descripcion}</description>
        <styleUrl>#{estilo}</styleUrl>
        <Point>
            <coordinates>{lon},{lat},{alt}</coordinates>
        </Point>
    </Placemark>
"""
        archivo.write(punto)

    def dibujar_inicio_fin(self, archivo):
        inicio = self.raiz.find('.//u:coordenadas_inicio/u:coordenadas', self.ns)
        if inicio is not None:
            lon = inicio.find('u:longitud_geo', self.ns).text
            lat = inicio.find('u:latitud_geo', self.ns).text
            alt = inicio.find('u:altitud_geo', self.ns).text
            self.escribir_punto(archivo, "Salida", "Inicio de la etapa", lon, lat, alt, "estiloRojo")

        fin = self.raiz.find('.//u:coordenadas_fin/u:coordenadas', self.ns)
        if fin is not None:
            lon = fin.find('u:longitud_geo', self.ns).text
            lat = fin.find('u:latitud_geo', self.ns).text
            alt = fin.find('u:altitud_geo', self.ns).text
            self.escribir_punto(archivo, "Meta", "Fin de la etapa", lon, lat, alt, "estiloRojo")

    def dibujar_hitos_y_puntos(self, archivo):
        # 1. Puertos de montaña (VERDE)
        puertos = self.raiz.findall('.//u:hitos/u:puerto_montaña', self.ns)
        for puerto in puertos:
            categoria = puerto.find('u:categoria_puerto', self.ns).text
            nombre = f"Puerto (Cat. {categoria})"
            
            coord = puerto.find('u:coordenadas', self.ns)
            lon = coord.find('u:longitud_geo', self.ns).text
            lat = coord.find('u:latitud_geo', self.ns).text
            alt = coord.find('u:altitud_geo', self.ns).text
            self.escribir_punto(archivo, nombre, "Puerto de montaña", lon, lat, alt, "estiloVerde")

        # 2. Sprints (AZUL)
        sprints = self.raiz.findall('.//u:hitos/u:sprint', self.ns)
        for sprint in sprints:
            tipo = sprint.find('u:tipo_sprint', self.ns).text
            nombre = f"Sprint {tipo}"
            
            coord = sprint.find('u:coordenadas', self.ns)
            lon = coord.find('u:longitud_geo', self.ns).text
            lat = coord.find('u:latitud_geo', self.ns).text
            alt = coord.find('u:altitud_geo', self.ns).text
            self.escribir_punto(archivo, nombre, "Sprint intermedio", lon, lat, alt, "estiloAzul")

        # 3. Puntos anónimos (AMARILLO)
        puntos = self.raiz.findall('.//u:puntos_anonimos/u:punto_anonimo', self.ns)
        for p in puntos:
            etiqueta_nombre = p.find('u:nombre_punto', self.ns)
            nombre = etiqueta_nombre.text if etiqueta_nombre is not None else "Punto de ruta"
            
            coord = p.find('u:coordenadas', self.ns)
            lon = coord.find('u:longitud_geo', self.ns).text
            lat = coord.find('u:latitud_geo', self.ns).text
            alt = coord.find('u:altitud_geo', self.ns).text
            self.escribir_punto(archivo, nombre, "Punto de ruta", lon, lat, alt, "estiloAmarillo")

    def dibujar_linea(self, archivo):
        puntos_ruta = []
        # 1. Añadimos el Inicio (asumimos distancia 0.0)
        inicio = self.raiz.find('.//u:coordenadas_inicio/u:coordenadas', self.ns)
        if inicio is not None:
            puntos_ruta.append((0.0, inicio.find('u:longitud_geo', self.ns).text, 
                                     inicio.find('u:latitud_geo', self.ns).text, 
                                     inicio.find('u:altitud_geo', self.ns).text))
            
        # 2. Añadimos Hitos (Puertos y Sprints)
        hitos = self.raiz.findall('.//u:hitos/*', self.ns)
        for h in hitos:
            dist = float(h.find('u:distancia', self.ns).text)
            coord = h.find('u:coordenadas', self.ns)
            puntos_ruta.append((dist, coord.find('u:longitud_geo', self.ns).text, 
                                      coord.find('u:latitud_geo', self.ns).text, 
                                      coord.find('u:altitud_geo', self.ns).text))
                                      
        # 3. Añadimos Puntos anónimos
        anonimos = self.raiz.findall('.//u:puntos_anonimos/u:punto_anonimo', self.ns)
        for p in anonimos:
            dist = float(p.find('u:distancia', self.ns).text)
            coord = p.find('u:coordenadas', self.ns)
            puntos_ruta.append((dist, coord.find('u:longitud_geo', self.ns).text, 
                                      coord.find('u:latitud_geo', self.ns).text, 
                                      coord.find('u:altitud_geo', self.ns).text))
                                      
        # 4. Añadimos la Meta
        fin = self.raiz.find('.//u:coordenadas_fin/u:coordenadas', self.ns)
        longitud_total = float(self.raiz.find('.//u:longitud', self.ns).text)
        if fin is not None:
            puntos_ruta.append((longitud_total, fin.find('u:longitud_geo', self.ns).text, 
                                                fin.find('u:latitud_geo', self.ns).text, 
                                                fin.find('u:altitud_geo', self.ns).text))
                                                
        puntos_ruta.sort(key=lambda x: x[0])
        
        coords_str = " ".join([f"{p[1]},{p[2]},{p[3]}" for p in puntos_ruta])
        
        linea = f"""    <Placemark>
        <name>Ruta de la Etapa</name>
        <styleUrl>#estiloLinea</styleUrl>
        <LineString>
            <extrude>1</extrude>
            <tessellate>1</tessellate>
            <coordinates>
                {coords_str}
            </coordinates>
        </LineString>
    </Placemark>
"""
        archivo.write(linea)

    def generar(self):
        self.cargar_xml()
        if self.arbol is None:
            return
            
        with open(self.archivo_kml, 'w', encoding='utf-8') as f:
            self.escribir_prologo_kml(f)
            self.dibujar_inicio_fin(f)
            self.dibujar_hitos_y_puntos(f)
            self.dibujar_linea(f)
            self.escribir_epilogo_kml(f)
            
        print(f"¡Éxito! Archivo {self.archivo_kml} generado correctamente.")


if __name__ == "__main__":
    xml_entrada = "etapaEsquema.xml"
    kml_salida = "etapa.kml"
    
    generador = GeneradorKML(xml_entrada, kml_salida)
    generador.generar()