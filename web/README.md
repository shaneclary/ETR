# ETR Web Interface

A modern web application for uploading and processing point clouds through the **ETR (Entangled Triangle Rendering)** system.

![ETR Web Interface](https://img.shields.io/badge/Status-Ready-green) ![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey)

## Features

### 🎯 Core Capabilities

- **Drag & Drop Upload**: Upload point cloud files with intuitive drag-and-drop interface
- **Multi-Format Support**: Works with PLY, PCD, PTS, XYZ, and LAS/LAZ formats
- **ETR Processing**: Transform triangles using Robert Edward Grant's theory
- **Real-Time Visualization**: Interactive charts and data tables
- **Demo Mode**: Try ETR without uploading files
- **System Status**: Monitor available features and dependencies

### 📊 Visualization

- **Charts**: Line charts showing scaling factors across fractal levels
- **3D View**: Three.js-based 3D visualization (ready for expansion)
- **Data Tables**: Detailed numerical data for analysis

### 🎨 User Experience

- **Modern Dark UI**: Beautiful gradient-based interface
- **Responsive Design**: Works on desktop and mobile devices
- **Toast Notifications**: User-friendly feedback messages
- **Loading States**: Clear indicators during processing
- **Tab-Based Navigation**: Organized results display

## Quick Start

### Installation

1. **Navigate to web directory:**
```bash
cd web
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

4. **Open in browser:**
```
http://localhost:5000
```

### With Full ETR Support

To enable full point cloud processing and ETR transformations, install additional dependencies:

```bash
# Install from main requirements
cd ..
micromamba create -f requirements.yaml
micromamba activate triangle_splatting

# Or install with pip
pip install numpy torch plyfile open3d
```

## Usage Guide

### 1. Demo Mode (No Upload Required)

The **ETR Demo** section lets you try the transformation without uploading files:

1. Enter triangle parameters:
   - Base (default: 3)
   - Height (default: 4)
   - Hypotenuse (default: 5)
   - Levels (default: 5)

2. Click **"Run Demo"**

3. View results in the Results panel:
   - Right triangle transformations
   - Left triangle (entangled) values
   - Scaling factors
   - Pythagorean validation

### 2. Upload & Process Files

For processing actual point cloud files:

1. **Upload File:**
   - Drag and drop a file onto the upload area
   - OR click "Browse Files" to select a file
   - Supported formats: PLY, PCD, PTS, XYZ, LAS/LAZ

2. **View File Information:**
   - File name, size, and format
   - Upload timestamp

3. **Process with ETR:**
   - Click **"Process with ETR"** button
   - Wait for processing to complete
   - View results showing:
     - Number of points
     - Color/normal availability
     - ETR processing status

### 3. Explore Results

Switch between different views using tabs:

- **Chart**: Visual representation of scaling factors
- **3D View**: Three.js visualization area (expandable)
- **Data**: Detailed table with all numerical values

## API Endpoints

The Flask backend provides a REST API:

### `GET /`
Serves the main web interface

### `POST /api/upload`
Upload a point cloud file

**Request:** `multipart/form-data` with `file` field

**Response:**
```json
{
  "success": true,
  "file": {
    "id": "20251031_123456_model.ply",
    "name": "model.ply",
    "size": 12345678,
    "size_mb": 11.77,
    "extension": ".ply"
  }
}
```

### `POST /api/process`
Process uploaded file through ETR

**Request:**
```json
{
  "file_id": "20251031_123456_model.ply",
  "options": {}
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "num_points": 50000,
    "has_colors": true,
    "has_normals": true,
    "etr_processed": true
  }
}
```

### `POST /api/demo/etr`
Run ETR demo with custom triangle

**Request:**
```json
{
  "base": 3,
  "height": 4,
  "hypotenuse": 5,
  "levels": 5
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "level": 0,
      "right_triangle": {
        "base": 3,
        "height": 4,
        "hypotenuse": 5,
        "scaling_factor": 20,
        "valid": true
      },
      "left_triangle": {
        "base": 0.15,
        "height": 0.2,
        "hypotenuse": 0.25,
        "valid": true
      }
    }
  ]
}
```

### `GET /api/formats`
Get information about supported formats

### `GET /api/status`
Get system status and available features

**Response:**
```json
{
  "status": "running",
  "dependencies": {
    "numpy": true,
    "torch": true,
    "point_cloud_loader": true,
    "etr_core": true
  },
  "features": {
    "file_upload": true,
    "point_cloud_loading": true,
    "etr_processing": true,
    "demo_mode": true
  }
}
```

### `POST /api/clear`
Clear all uploaded files and results

## Architecture

```
web/
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Application styles
│   └── js/
│       └── app.js        # Frontend JavaScript
└── uploads/              # Temporary upload directory (auto-created)
```

### Technology Stack

**Backend:**
- Flask 3.0 - Web framework
- Flask-CORS - Cross-origin resource sharing
- Werkzeug - WSGI utilities

**Frontend:**
- Vanilla JavaScript (ES6+)
- Chart.js - Data visualization
- Three.js - 3D rendering
- CSS3 with CSS Grid & Flexbox

**Integration:**
- ETR Core (`etr/core/entangled_triangles.py`)
- Point Cloud Loader (`utils/point_cloud_io.py`)
- Pure Python fallback for demo mode

## Configuration

### File Upload Limits

Default maximum file size: **500 MB**

To change, edit `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # bytes
```

### Port Configuration

Default port: **5000**

To change, edit the last line of `app.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Upload Directory

Files are temporarily stored in:
- Uploads: `/tmp/etr_uploads/`
- Results: `/tmp/etr_results/`

To change, edit `app.py`:
```python
UPLOAD_FOLDER = Path('/your/custom/path/uploads')
RESULTS_FOLDER = Path('/your/custom/path/results')
```

## Development

### Running in Development Mode

```bash
# With debug mode (auto-reload on changes)
python app.py

# Or with Flask CLI
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### Testing the API

Using `curl`:

```bash
# Check status
curl http://localhost:5000/api/status

# Upload file
curl -X POST -F "file=@path/to/model.ply" http://localhost:5000/api/upload

# Run demo
curl -X POST http://localhost:5000/api/demo/etr \
  -H "Content-Type: application/json" \
  -d '{"base": 3, "height": 4, "hypotenuse": 5, "levels": 5}'
```

### Adding New Features

To add new functionality:

1. **Backend:** Add route in `app.py`
2. **Frontend:** Add function in `app.js`
3. **UI:** Update `index.html` and `style.css`

Example - Adding a new API endpoint:

```python
# In app.py
@app.route('/api/my-feature', methods=['POST'])
def my_feature():
    data = request.json
    # Your logic here
    return jsonify({'success': True, 'result': data})
```

```javascript
// In app.js
async function callMyFeature(params) {
    const response = await fetch('/api/my-feature', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    });
    return response.json();
}
```

## Deployment

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t etr-web .
docker run -p 5000:5000 etr-web
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Issue: "Module not found" errors

**Solution:** Install the web requirements:
```bash
pip install -r web/requirements.txt
```

### Issue: ETR processing fails

**Solution:** This is expected if NumPy/PyTorch aren't installed. The demo mode will still work. To enable full processing:
```bash
pip install numpy torch
```

### Issue: Upload fails with large files

**Solution:** Increase the maximum file size in `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 1GB
```

### Issue: Port 5000 already in use

**Solution:** Change the port in `app.py` or kill the process using port 5000:
```bash
# Find process
lsof -i :5000

# Kill it
kill -9 <PID>
```

## Browser Compatibility

Tested and working on:
- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Security Considerations

### For Production:

1. **Enable HTTPS**: Use SSL/TLS certificates
2. **Add Authentication**: Implement user authentication
3. **Rate Limiting**: Prevent abuse with Flask-Limiter
4. **File Validation**: Enhanced file type checking
5. **CSRF Protection**: Add Flask-WTF
6. **Input Sanitization**: Validate all user inputs

Example rate limiting:

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/upload', methods=['POST'])
@limiter.limit("10 per minute")
def upload_file():
    # ...
```

## Performance

### Optimization Tips:

1. **Enable Caching**: Use Flask-Caching for repeated requests
2. **Async Processing**: Use Celery for long-running tasks
3. **CDN**: Serve static files from CDN
4. **Compression**: Enable Gzip compression
5. **Database**: Use PostgreSQL for persistent storage

## Contributing

To contribute to the web interface:

1. Follow the existing code style
2. Test all changes locally
3. Update documentation
4. Add comments for complex logic

## License

Same as the main ETR project. See parent directory LICENSE file.

## Support

For issues specific to the web interface:
- Check this README first
- Review the API documentation
- Check browser console for errors
- Enable Flask debug mode for detailed errors

## Related Documentation

- [Main ETR README](../etr/README.md)
- [Point Cloud Formats](../docs/POINT_CLOUD_FORMATS.md)
- [Integration Guide](../etr/docs/INTEGRATION_GUIDE.md)
- [Project Status](../PROJECT_STATUS.md)

---

**Version:** 1.0.0
**Last Updated:** 2025-10-31
**Author:** ETR Development Team
