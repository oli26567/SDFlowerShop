from abc import ABC, abstractmethod
import json, csv, io

class FlowerExporter(ABC):
    def export(self, flowers):
        data = [f.__dict__ for f in flowers]
        formatted = self.transform(data)
        return formatted

    @abstractmethod
    def transform(self, data):
        pass

class JsonExport(FlowerExporter):
    def transform(self, data):
        return json.dumps(data, indent=4)

class CsvExport(FlowerExporter):
    def transform(self, data):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['id', 'name', 'color', 'price', 'stock'])
        for f in data:
            writer.writerow([f['id'], f['name'], f['color'], f['price'], f['stock']])
        return output.getvalue()