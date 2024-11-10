from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import pymupdf4llm
import google.generativeai as genai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}


genai.configure(api_key=os.environ["GEMINI_API_KEY"])
gemini = genai.GenerativeModel("gemini-1.5-flash")



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File successfully uploaded"}), 200
    else:
        return jsonify({"error": "File type not allowed"}), 400




def pdf_page_to_image(page):
     img_page = page.get_pixmap()
     img_page_no = page.number
     return img_page,img_page_no

def extract_text():
    md_text = pymupdf4llm.to_markdown("input.pdf")
    return md_text


def extract_tables(img_page,img_page_no = 0):
    table_extraction_prompt = f"You’re an AI model designed to analyze images and locate all tables, including those without visible borders. For each detected table, you identify rows, columns, and cells with high precision, regardless of visual separators, capturing finer details such as text style, alignment, symbols, and any other attributes within each cell. You extract all data while preserving the exact structure seen in the image, ensuring that the output table has the same number of rows and columns. The position of attributes, values, and any text or symbols within cells should match their original positions in the image and appear the same in markdown format. Column attributes are displayed accurately at the top of each column, directly above the respective values, if present. If no column attributes are found, avoid adding any default row or column headers. If a header row is present, use it to identify column names.
                                You maintain the original layout and structure as closely as possible to match the source table in the image. Following extraction, you generate a detailed summary that highlights essential figures, names, or notable patterns. You also verify if the total or any value depends on the entire column (e.g., sums, averages, or derived values) and ensure that the output reflects this correctly. Present the output in markdown format, keeping both the table structure and summary concise, and ensuring that all elements retain their original positions from the image. If no table is found in the image, return 'Table not found.' You perform these tasks without asking further questions, ensuring precision and consistency. Also you have the option to calculate total of values of a column if necessary based on the context in the image"
    result = gemini.generate_content([table_extraction_prompt, img_page])





if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
