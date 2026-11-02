import xml.etree.ElementTree as ET

class GeneradorAltimetria:
    def __init__(self, archivo_xml, archivo_svg):
        self.archivo_xml = archivo_xml
        self.archivo_svg = archivo_svg
        self.ns = {'u': 'http://www.uniovi.es'}
        self.arbol = None
        self.raiz = None
        self.puntos = []

    def cargar_xml(self):
        try:
            self.arbol = ET.parse(self.archivo_xml)
            self.raiz = self.arbol.getroot()
            print("XML cargado correctamente para altimetría.")
        except Exception as e:
            print(f"Error al cargar el XML: {e}")

    def extraer_datos(self):
        if self.raiz is None:
            return

        # 1. Salida
        alt_inicio = self.raiz.find('.//u:coordenadas_inicio/u:coordenadas/u:altitud_geo', self.ns).text
        ciudad_inicio = self.raiz.find('.//u:ciudad_inicio', self.ns).text
        self.puntos.append((0.0, float(alt_inicio), f"Salida: {ciudad_inicio}"))

        # 2. Hitos
        hitos = self.raiz.findall('.//u:hitos/*', self.ns)
        for h in hitos:
            dist = float(h.find('u:distancia', self.ns).text)
            alt = float(h.find('u:coordenadas/u:altitud_geo', self.ns).text)
            if 'puerto' in h.tag:
                cat = h.find('u:categoria_puerto', self.ns).text
                nombre = f"Puerto Cat.{cat}"
            else:
                nombre = "Sprint"
            self.puntos.append((dist, alt, nombre))

        # 3. Puntos Anónimos
        anonimos = self.raiz.findall('.//u:puntos_anonimos/u:punto_anonimo', self.ns)
        for p in anonimos:
            dist = float(p.find('u:distancia', self.ns).text)
            alt = float(p.find('u:coordenadas/u:altitud_geo', self.ns).text)
            etiqueta_nombre = p.find('u:nombre_punto', self.ns)
            nombre = etiqueta_nombre.text if etiqueta_nombre is not None else "Punto"
            self.puntos.append((dist, alt, nombre))

        # 4. Meta
        longitud_total = float(self.raiz.find('.//u:longitud', self.ns).text)
        alt_fin = self.raiz.find('.//u:coordenadas_fin/u:coordenadas/u:altitud_geo', self.ns).text
        ciudad_fin = self.raiz.find('.//u:ciudad_fin', self.ns).text
        self.puntos.append((longitud_total, float(alt_fin), f"Meta: {ciudad_fin}"))

        self.puntos.sort(key=lambda x: x[0])

    def generar_svg(self):
        if not self.puntos:
            return

        ancho_svg = 1400
        alto_svg = 700
        margen_x = 100
        margen_y_sup = 100
        margen_y_inf = 200

        max_dist = max(p[0] for p in self.puntos)
        max_alt = max(p[1] for p in self.puntos)

        escala_x = (ancho_svg - 2 * margen_x) / max_dist
        escala_y = (alto_svg - margen_y_sup - margen_y_inf) / max_alt

        with open(self.archivo_svg, 'w', encoding='utf-8') as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho_svg} {alto_svg}" width="100%" height="100%">\n')
            f.write('    <rect width="100%" height="100%" fill="white" />\n')
            f.write('    <style>\n')
            f.write('        .texto { font-family: Arial, sans-serif; font-size: 13px; fill: black; }\n')
            f.write('        .linea-guia { stroke: #cccccc; stroke-dasharray: 5,5; stroke-width: 1; }\n')
            f.write('    </style>\n')

            tramos_alt = 5
            for i in range(tramos_alt + 1):
                alt_guia = (max_alt / tramos_alt) * i
                y_guia = alto_svg - margen_y_inf - (alt_guia * escala_y)
                f.write(f'    <line x1="{margen_x - 10}" y1="{y_guia}" x2="{ancho_svg - margen_x}" y2="{y_guia}" class="linea-guia" />\n')
                f.write(f'    <text x="{margen_x - 15}" y="{y_guia + 4}" text-anchor="end" class="texto">{int(alt_guia)}m</text>\n')

            coords_polilinea = f"{margen_x},{alto_svg - margen_y_inf} "
            
            for dist, alt, nombre in self.puntos:
                x = margen_x + (dist * escala_x)
                y = alto_svg - margen_y_inf - (alt * escala_y)
                coords_polilinea += f"{x},{y} "
                
                f.write(f'    <line x1="{x}" y1="{alto_svg - margen_y_inf}" x2="{x}" y2="{y}" class="linea-guia" />\n')
                
                y_texto = alto_svg - margen_y_inf + 15
                f.write(f'    <text x="{x}" y="{y_texto}" transform="rotate(90 {x},{y_texto})" text-anchor="start" class="texto">{nombre} ({dist} km)</text>\n')

            x_final = margen_x + (max_dist * escala_x)
            coords_polilinea += f"{x_final},{alto_svg - margen_y_inf} "
            coords_polilinea += f"{margen_x},{alto_svg - margen_y_inf}"

            f.write(f'    <polyline points="{coords_polilinea}" fill="none" stroke="red" stroke-width="3" />\n')

            f.write(f'    <line x1="{margen_x}" y1="{alto_svg - margen_y_inf}" x2="{x_final}" y2="{alto_svg - margen_y_inf}" stroke="black" stroke-width="2" />\n')
            
            f.write('</svg>\n')

    def generar(self):
        self.cargar_xml()
        self.extraer_datos()
        self.generar_svg()
        print(f"¡Éxito! Archivo {self.archivo_svg} generado correctamente.")

if __name__ == "__main__":
    xml_entrada = "etapaEsquema.xml"
    svg_salida = "altimetria.svg"
    
    generador = GeneradorAltimetria(xml_entrada, svg_salida)
    generador.generar()