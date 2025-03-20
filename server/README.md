# File Upload Server

A simple Flask server to handle file uploads and return responses with file name and status.

## Project Structure

```
server/
├── app.py                    # Main entry point with Flask routes
├── uploads/                  # Directory for file uploads
├── requirements.txt          # Python dependencies
└── src/                      # Source code directory
    ├── config.py             # Configuration and environment variables
    ├── models/               # Data models directory
    ├── services/             # Business logic services
    │   ├── document_service.py # Document processing
    │   └── pdf_service.py    # PDF to markdown conversion
    └── utils/                # Utility functions
        └── retriever.py      # Pinecone retriever implementation
```

## Using System Python (Recommended for Quick Setup)

If you want to use your system's Python installation:

```bash
# Install the required packages globally
pip install -r requirements.txt

# Run the server
python app.py
```

The server will start on http://127.0.0.1:5000

## Alternative: Using a Virtual Environment (Optional)

If you prefer to keep dependencies isolated:

### On Windows:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate  # You should see (venv) at the beginning of your command prompt

# Install requirements
pip install -r requirements.txt
```

### On macOS/Linux:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # You should see (venv) at the beginning of your command prompt

# Install requirements
pip install -r requirements.txt
```

To deactivate the virtual environment when done:

```bash
deactivate
```

## API Endpoints

### File Upload

- **URL**: `/upload`
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Form Parameter**: file

#### Response Format

```json
{
  "status": "success",
  "file_name": "example.pdf",
  "message": "File uploaded successfully"
}
```

## Testing the API

### Using curl

You can test the API using curl:

```bash
curl -X POST -F "file=@path/to/your/file.pdf" http://127.0.0.1:5000/upload
```

### Using Postman

1. Open Postman.
2. Create a new `POST` request.
3. Enter the URL: `http://127.0.0.1:5000/upload`.
4. Go to the `Body` tab.
5. Select `form-data`.
6. In the `Key` field, enter `file`.
7. In the `Value` field, click on the `Select Files` button and choose the file you want to upload.
8. Click `Send`.

You should see a response similar to:

```json
{
  "status": "success",
  "file_name": "example.pdf",
  "message": "File uploaded successfully"
}
```
