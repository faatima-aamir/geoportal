🛰️ Web-Based Geoportal for Spatial Data Sharing
A full-stack spatial data sharing platform built with Django, OpenLayers, GeoServer, and PostGIS. This geoportal allows users to upload, visualize, and analyze spatial datasets through an interactive web map.

🔧 Technologies Used
Frontend: HTML5, CSS3, JavaScript, OpenLayers

Backend: Django (Python)

Spatial Server: GeoServer (WMS/WFS)

Database: PostgreSQL + PostGIS

Environment: Anaconda (Python 3.10)

✨ Features
Upload shapefiles or GeoJSON files

Visualize uploaded layers using OpenLayers

View attribute tables and spatial metadata

Connect to GeoServer for WMS/WFS services

Perform basic spatial queries (e.g., buffer)

Display charts or summary statistics of datasets

🧩 Project Setup
1. Clone the Repository
git clone https://github.com/faatima-aamir/web-gis-geoportal.git
cd web-gis-geoportal

2. Create and Activate a Virtual Environment (Anaconda)
conda create -n geoportal_env python=3.10
conda activate geoportal_env

3. Install Dependencies
pip install -r requirements.txt

4. Run the Django Server
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

Open your browser and go to: http://127.0.0.1:8000

🌍 GeoServer Configuration
GeoServer must be running at: http://localhost:8080/geoserver

WMS and WFS layers must be published and accessible

Layers are connected to the OpenLayers map via service URLs

🖼️ Screenshots
(Optional — but recommended for visual context)
To add screenshots, place them inside an /images folder in your repo and link them like this:
![Homepage](images/homepage.png)
![Upload Interface](images/upload.png)
![Attribute Table](images/attribute-table.png)

📁 Directory Structure
/geoportal-backend/
├── templates/ → HTML + JS (OpenLayers UI)
├── static/ → CSS, JS assets
├── geoportal/ → Django app files
├── manage.py → Django project runner
└── db.sqlite3 → (or PostGIS DB connection)

📄 License
MIT License — Free to use, adapt, and share.

🙋‍♀️ Author
Faatima Aamir
www.linkedin.com/in/faatima-aamir-723a8b292
