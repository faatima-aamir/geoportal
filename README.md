# 🛰️ Web-Based Geoportal for Spatial Data Sharing
## A full-stack spatial data sharing platform built with Django, Leaflet, GeoServer, and PostGIS. This geoportal allows users to upload, visualize, and analyze spatial datasets through an interactive web map.

#🔧 Technologies Used
Frontend: HTML5, CSS3, JavaScript, Leaflet

Backend: Django (Python)

Spatial Server: GeoServer (WMS/WFS)

Database: PostgreSQL + PostGIS

Environment: Anaconda (Python 3.10)

#✨ Features
Upload shapefiles or GeoJSON files

Visualize uploaded layers using OpenLayers

View attribute tables and spatial metadata

Connect to GeoServer for WMS/WFS services

Perform basic spatial queries (e.g., buffer)

Display charts or summary statistics of datasets

Has LLM integration to ask any questions

#🧩 Project Setup
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
Homepage:
<img width="1919" height="864" alt="image" src="https://github.com/user-attachments/assets/d6329c81-b71c-4d31-a32e-45a28965505e" />
Login:
<img width="1919" height="863" alt="image" src="https://github.com/user-attachments/assets/4d4dac1f-e67e-45d6-811c-f503bac7bb72" />
Signup:
<img width="1919" height="868" alt="image" src="https://github.com/user-attachments/assets/fb0a18e7-6efc-4532-b004-aabc478bc38b" />
Shapefile and Geojson Viewer:
<img width="1919" height="671" alt="image" src="https://github.com/user-attachments/assets/e040b1c0-e7f5-4a1f-8b0c-add4a42bae19" />
<img width="1919" height="843" alt="image" src="https://github.com/user-attachments/assets/3247f4b9-896b-4584-861e-b19808111288" />
Geodataset Explorer:
<img width="1919" height="868" alt="image" src="https://github.com/user-attachments/assets/7d34aed5-3828-49db-a350-6832a602d068" />
<img width="1919" height="861" alt="image" src="https://github.com/user-attachments/assets/d95b737b-71c0-490d-893f-bd313743baa7" />
Visualize datasets:
<img width="1919" height="863" alt="image" src="https://github.com/user-attachments/assets/273edb98-73ba-4f7c-b7c5-32b091c0dcf9" />
<img width="1919" height="869" alt="image" src="https://github.com/user-attachments/assets/0f3f049c-9022-44e3-9669-5f7907fea0b6" />
<img width="1919" height="865" alt="image" src="https://github.com/user-attachments/assets/d55a847c-dba7-492b-8be2-d8e2c6ccbeec" />
<img width="1919" height="194" alt="image" src="https://github.com/user-attachments/assets/ace07a55-78a6-482c-8c34-16e26150c662" />


📁 Directory Structure
/geoportal-backend/
├── templates/ → HTML + JS (Leaflet UI)
├── static/ → CSS, JS assets
├── geoportal/ → Django app files
├── manage.py → Django project runner
└── db.sqlite3 → (or PostGIS DB connection)

📄 License
MIT License — Free to use, adapt, and share.

🙋‍♀️ Author
Faatima Aamir
www.linkedin.com/in/faatima-aamir-723a8b292
