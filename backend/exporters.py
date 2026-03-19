import simplekml
import ezdxf
import io

def export_to_kml(data, input_file_format):
    kml = simplekml.Kml()
    for row in data:
        if input_file_format == "pnec":
            pnt = kml.newpoint(name=str(row["ponto"]), coords=[(row["converted_x"], row["converted_y"])])
            pnt.description = f"Original N: {row['original_y']}\nOriginal E: {row['original_x']}\nCota: {row['cota']}\nDescrição: {row['descricao']}"
        else:
            pnt = kml.newpoint(name="Ponto", coords=[(row["converted_x"], row["converted_y"])])
            pnt.description = f"Original X: {row['original_x']}\nOriginal Y: {row['original_y']}"
    
    # Salvar KML em um buffer de memória
    kml_buffer = io.BytesIO()
    kml.save(kml_buffer)
    kml_buffer.seek(0)
    return kml_buffer.getvalue()

def export_to_dxf(data, input_file_format):
    doc = ezdxf.new("R2010")  # Criar um novo documento DXF (versão AutoCAD 2010)
    msp = doc.modelspace()

    for row in data:
        if input_file_format == "pnec":
            # Adicionar um ponto
            msp.add_point((row["converted_x"], row["converted_y"], float(row["cota"]) if row["cota"] else 0))
            # Adicionar texto para o ponto/descrição
            msp.add_text(f"{row['ponto']} - {row['descricao']}",
                         dxfattribs={
                             "height": 0.5,
                             "insert": (row["converted_x"] + 0.5, row["converted_y"] + 0.5, float(row["cota"]) if row["cota"] else 0)
                         })
        else:
            msp.add_point((row["converted_x"], row["converted_y"], 0))
            msp.add_text(f"X:{row['converted_x']:.3f} Y:{row['converted_y']:.3f}",
                         dxfattribs={
                             "height": 0.5,
                             "insert": (row["converted_x"] + 0.5, row["converted_y"] + 0.5, 0)
                         })
    
    # Salvar DXF em um buffer de memória
    dxf_buffer = io.BytesIO()
    doc.saveas(dxf_buffer)
    dxf_buffer.seek(0)
    return dxf_buffer.getvalue()
