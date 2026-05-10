import json, csv, io
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

class ExportStrategy(ABC):
    @abstractmethod
    def export(self, flowers):
        pass

class JsonExport(ExportStrategy):
    def export(self, flowers):
        return json.dumps([f.__dict__ for f in flowers], indent=4)

class CsvExport(ExportStrategy):
    def export(self, flowers):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Color', 'Price', 'Stock'])
        for f in flowers:
            writer.writerow([f.id, f.name, f.color, f.price, f.stock])
        return output.getvalue()

class XmlExport(ExportStrategy):
    def export(self, flowers):
        root = ET.Element("Flowers")
        for f in flowers:
            flower_el = ET.SubElement(root, "Flower")
            for k, v in f.__dict__.items():
                child = ET.SubElement(flower_el, k)
                child.text = str(v)
        return ET.tostring(root, encoding='unicode')