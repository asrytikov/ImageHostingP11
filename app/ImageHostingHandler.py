import os
from urllib.parse import parse_qs
from uuid import uuid4

from loguru import logger

from AdvancedHandler import AdvancedHTTPRequestHandler
from DBManager import DBManager
from settings import IMAGES_PATH, \
    ALLOWED_EXTENSIONS, MAX_FILE_SIZE, ERROR_FILE


class ImageHostingHandler(AdvancedHTTPRequestHandler):
    server_version = 'Image Hosting Server v0.2'

    def __init__(self, request, client_address, server):
        self.db = DBManager()
        super().__init__(request, client_address, server)

    def do_GET(self):
        path = self.path.rstrip('/')  # Нормализация пути
        logger.debug(f"Processing GET: {path}")

        if path == '/api/images':
            return self.get_images()

        logger.warning(f"No GET handler for path: {path}")
        super().do_GET()

    def do_POST(self):
        path = self.path.rstrip('/')  # Нормализация пути
        logger.debug(f"Processing POST: {path}")

        if path == '/upload':
            return self.post_upload()

        logger.warning(f"No POST handler for path: {path}")
        super().do_POST()

    def do_DELETE(self):
        path = self.path.rstrip('/')  # Нормализация пути
        logger.debug(f"Processing DELETE: {path}")

        if path.startswith('/api/images/'):
            image_id = path.split('/')[-1]  # Извлекаем ID изображения из URL
            return self.delete_image(image_id)

        logger.warning(f"No DELETE handler for path: {path}")
        self.send_html(ERROR_FILE, 405)  # Method Not Allowed

    def get_images(self) -> None:
        try:
            logger.info(f"Fetching images, query: {self.headers.get('Query-String')}")
            query_components = parse_qs(self.headers.get('Query-String', ''))
            page = int(query_components.get('page', ['1'])[0])
            if page < 1:
                page = 1
                logger.debug(f"Adjusted page number to: {page}")

            images = self.db.get_images(page)
            images_json = []
            for image in images:
                image_data = {
                    'filename': image[1],
                    'original_name': image[2],
                    'size': image[3],
                    'upload_date': image[4].strftime('%Y-%m-%d %H:%M:%S'),
                    'file_type': image[5]
                }
                images_json.append(image_data)

            logger.success(f"Returning {len(images_json)} images for page {page}")
            self.send_json({'images': images_json})

        except Exception as e:
            logger.error(f"Failed to fetch images: {e}")
            self.send_html(ERROR_FILE, 500)

    def post_upload(self) -> None:
        try:
            length = int(self.headers.get('Content-Length', 0))
            logger.info(f"Upload request started (size: {length} bytes)")

            if length > MAX_FILE_SIZE:
                logger.error(f"File too large ({length} > {MAX_FILE_SIZE})")
                self.send_html(ERROR_FILE, 413)
                return

            filename_header = self.headers.get('Filename')
            if not filename_header:
                logger.error("Missing 'Filename' header")
                self.send_html(ERROR_FILE, 400)
                return

            orig_name, ext = os.path.splitext(filename_header)
            if ext not in ALLOWED_EXTENSIONS:
                logger.error(f"Invalid file extension: {ext}")
                self.send_html(ERROR_FILE, 400)
                return

            data = self.rfile.read(length)
            filename = uuid4()
            file_size_kb = round(length / 1024)

            self.db.add_image(filename, orig_name, file_size_kb, ext)
            with open(os.path.join(IMAGES_PATH, f'{filename}{ext}'), 'wb') as file:
                file.write(data)

            logger.success(f"Upload completed: {filename}{ext} (size: {file_size_kb} KB)")
            self.send_html('upload_success.html', headers={
                'Location': f'http://localhost/{IMAGES_PATH}{filename}{ext}'
            })

        except Exception as e:
            logger.critical(f"Upload failed: {e}")
            self.send_html(ERROR_FILE, 500)

    def delete_image(self, image_id: str) -> None:
        try:
            logger.info(f"Attempting to delete image {image_id}")
            filename, ext = os.path.splitext(image_id)

            if not filename:
                logger.error("Empty filename in delete request")
                self.send_html(ERROR_FILE, 400)
                return

            image_path = os.path.join(IMAGES_PATH, f'{filename}{ext}')
            if not os.path.exists(image_path):
                logger.error(f"Image not found: {image_path}")
                self.send_html(ERROR_FILE, 404)
                return

            self.db.delete_image(filename)
            os.remove(image_path)
            logger.success(f"Deleted image {image_id} successfully")
            self.send_json({'status': 'success'})

        except Exception as e:
            logger.error(f"Delete failed for {image_id}: {e}")
            self.send_html(ERROR_FILE, 500)


# Настройка логирования
logger.add("logs/image_hosting.log",
           rotation="10 MB",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
           level="DEBUG")