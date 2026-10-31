import zipfile
import os

class ZipUtils:
    @staticmethod
    def pack(files, zip_path):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in files:
                if os.path.exists(f):
                    z.write(f, os.path.basename(f))
        return zip_path
