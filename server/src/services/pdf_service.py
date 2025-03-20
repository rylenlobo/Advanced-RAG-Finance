from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from src.config import GOOGLE_API_KEY
import time


class PDFToMarkDownTextProcessor:
    """Service for converting PDF files to Markdown text"""

    def __init__(self):
        self.config = {
            "output_format": "markdown",
            "use_llm": True,
            "disable_image_extraction": True,
            "paginate_output": True,
            "output_dir": 'output',
            "use_fast": True,
            "gemini_api_key": GOOGLE_API_KEY,
        }

        self.config_parser = ConfigParser(self.config)

        self.converter = PdfConverter(
            config=self.config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=self.config_parser.get_processors(),
            renderer=self.config_parser.get_renderer()
        )

    def process(self, file_path):
        """Process a PDF file and convert it to markdown"""
        rendered = self.converter(file_path)
        return rendered.markdown

    def process_with_timeout(self, file_path, result_queue, timeout=300):
        """Run the process with a timeout, allowing for interruption"""
        try:
            print(f"PDF processor: Starting conversion of {file_path}")
            result = self.process(file_path)
            print(f"PDF processor: Finished conversion, putting result in queue")
            result_queue.put(result)
        except Exception as e:
            print(f"PDF processor error: {str(e)}")
            result_queue.put(f"ERROR: {str(e)}")
        finally:
            # Ensure queue has something even if there's an unexpected error
            if result_queue.empty():
                result_queue.put("ERROR: Unknown error in PDF processing")
