from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
import pandas as pd
from django.db import connection
from django.views.decorators.http import require_http_methods
from .models import UploadedFile
import json
import requests
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


def home_view(request):
    recent_files = UploadedFile.objects.all().order_by('-uploaded_at')[:6]
    return render(request, 'geoapi/home.html', {'recent_files': recent_files})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home_view')
        else:
            messages.error(request, 'Error creating account. Please check the form.')
    else:
        form = UserCreationForm()
    return render(request, 'geoapi/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Logged in successfully!')
            return redirect('home_view')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'geoapi/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home_view')

# @login_required
def upload_view(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        title = request.POST.get('title', file.name)
        description = request.POST.get('description', '')

        if not file:
            messages.error(request, 'No file uploaded.')
            return redirect('upload_view')

        UploadedFile.objects.create(
            title=title,
            description=description,
            file=file,
            uploaded_by=request.user
        )
        messages.success(request, 'File uploaded successfully!')
        return redirect('home_view')

    return render(request, 'geoapi/upload.html')

def get_table_names():
    with connection.cursor() as cursor:
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        return [row[0] for row in cursor.fetchall()]

def load_table_as_df(table_name):
    return pd.read_sql(f'SELECT * FROM \"{table_name}\"', connection)

@require_http_methods(["GET", "POST"])
@login_required
def visualise_data(request):
    df = None
    stats = {}
    stat_headers = []
    plot_data = {}
    column_names = []
    table_names = get_table_names()
    table_selected = request.GET.get("table")
    csv_uploaded = False

    # CSV Upload
    if request.method == 'POST' and 'csv_file' in request.FILES:
        uploaded_file = request.FILES["csv_file"]
        try:
            df = pd.read_csv(uploaded_file)
            # Clean string-formatted numbers
            df = df.apply(lambda col: col.str.replace(',', '').str.strip() if col.dtypes == 'object' else col)
            df = df.apply(pd.to_numeric, errors='coerce')
            if 'Year' in df.columns:
                df['Year'] = df['Year'].astype(str)
            print("🔍 Cleaned Column types:", df.dtypes)
            csv_uploaded = True
            request.session['csv_data'] = df.to_json()
        except Exception as e:
            print("CSV Upload Error:", e)

    # Load CSV from session
    if df is None and 'csv_data' in request.session:
        try:
            df = pd.read_json(request.session['csv_data'])
            # Same cleaning
            df = df.apply(lambda col: col.str.replace(',', '').str.strip() if col.dtypes == 'object' else col)
            df = df.apply(pd.to_numeric, errors='coerce')
            if 'Year' in df.columns:
                df['Year'] = df['Year'].astype(str)
            print("🔍 Cleaned Column types:", df.dtypes)
            csv_uploaded = True
        except Exception as e:
            print("CSV Session Load Error:", e)
            request.session.pop('csv_data', None)

    # Table Selection
    elif table_selected:
        try:
            df = load_table_as_df(table_selected)
            # Clean table data similarly
            df = df.apply(lambda col: col.str.replace(',', '').str.strip() if col.dtypes == 'object' else col)
            df = df.apply(pd.to_numeric, errors='coerce')
            if 'Year' in df.columns:
                df['Year'] = df['Year'].astype(str)
            print("🔍 Cleaned Column types:", df.dtypes)
        except Exception as e:
            print("DB Table Load Error:", e)

    # Process Data
    if df is not None and not df.empty:
        column_names = df.columns.tolist()
        stats = df.describe(include='all').fillna("N/A").to_dict()
        stat_headers = list(df.describe().index)

        for col in column_names:
            if pd.api.types.is_numeric_dtype(df[col]):
                plot_data[col] = {
                    "x": list(df.index),
                    "y": df[col].dropna().tolist()
                }
        print("📊 Final plot_data:", plot_data)

    return render(request, "geoapi/visualise.html", {
        "table_names": table_names,
        "table_selected": table_selected,
        "csv_uploaded": csv_uploaded,
        "plot_data": json.dumps(plot_data),
        "column_names": column_names,
        "stats": stats,
        "stat_headers": stat_headers
    })

GEOSERVER_BASE = "http://localhost:9090/geoserver"
WORKSPACE = "ne"
AUTH = ('admin', 'geoserver')


@login_required
def dataset_explorer(request):
    url = f"{GEOSERVER_BASE}/rest/layers"
    headers = {'Accept': 'application/json'}
    datasets = []

    try:
        response = requests.get(url, headers=headers, auth=AUTH)
        response.raise_for_status()
        layers = response.json().get('layers', {}).get('layer', [])

        for layer in layers:
            layer_name = layer['name']
            if layer_name.startswith(f"{WORKSPACE}:"):
                name_only = layer_name.split(":")[1]
                datasets.append({
                    'name': name_only,
                    'owner': 'admin',
                    'updated': 'N/A',
                    'view_url': f'/datasets/view/{name_only}/',
                    'metadata_url': f'/datasets/metadata/{name_only}/'
                })

    except Exception as e:
        print("❌ Error fetching published layers:", e)

    return render(request, 'geoapi/dataset.html', {'datasets': datasets})


@login_required
def view_dataset(request, layer_name):
    wms_url = f"{GEOSERVER_BASE}/{WORKSPACE}/wms"
    layer_full_name = f"{WORKSPACE}:{layer_name}"

    # Prepare WFS URL to get sample features
    features_url = (
        f"{GEOSERVER_BASE}/{WORKSPACE}/wfs"
        f"?service=WFS&version=1.0.0&request=GetFeature"
        f"&typeName={WORKSPACE}:{layer_name}&outputFormat=application/json&maxFeatures=10"
    )

    columns = []
    data = []

    try:
        response = requests.get(features_url, auth=AUTH)
        response.raise_for_status()
        geojson = response.json()

        features = geojson.get("features", [])
        if features:
            # Extract column headers from first feature
            columns = list(features[0]['properties'].keys())

            # Extract each row of values
            for feature in features:
                row = [feature['properties'].get(col) for col in columns]
                data.append(row)

    except Exception as e:
        print("❌ Error fetching WFS feature data:", e)

    return render(request, 'geoapi/view_dataset.html', {
        'dataset': {
            'name': layer_name,
            'workspace': WORKSPACE
        },
        'geoserver_url': GEOSERVER_BASE,
        'wms_url': wms_url,
        'layer_full_name': layer_full_name,
        'columns': columns,
        'data': data
    })


@login_required
def view_metadata(request, layer_name):
    describe_url = (
        f"{GEOSERVER_BASE}/{WORKSPACE}/wfs"
        f"?service=WFS&version=1.1.0&request=DescribeFeatureType"
        f"&typeName={WORKSPACE}:{layer_name}&outputFormat=application/json"
    )

    metadata = {
        'name': layer_name,
        'owner': 'admin',
        'updated': 'N/A',
        'abstract': 'No abstract available',
        'keywords': 'N/A',
        'bbox': 'N/A',
        'crs': 'EPSG:4326',
        'format': 'WMS',
    }

    try:
        response = requests.get(describe_url, auth=AUTH)
        response.raise_for_status()
        desc = response.json()

        if 'featureTypes' in desc:
            ft = desc['featureTypes'][0]
            metadata['abstract'] = ft.get('title', 'No abstract')
            metadata['keywords'] = ', '.join(ft.get('keywords', [])) if ft.get('keywords') else 'N/A'
            metadata['crs'] = ft.get('srs', 'EPSG:4326')
            metadata['bbox'] = str(ft.get('boundingBox', 'N/A'))

    except Exception as e:
        print("❌ Error fetching metadata:", e)

    return render(request, 'geoapi/view_metadata.html', {
        'dataset': metadata
    })

@csrf_exempt
def geo_llm_chat(request):
    if request.method != "POST":
        return JsonResponse({"reply": "⚠️ Only POST allowed"})

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "⚠️ Please enter a message."})

        def stream():
            with requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma:2b",
                    "prompt": user_message,
                    "stream": True
                },
                stream=True,
                headers={"Content-Type": "application/json"},
            ) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            partial = json.loads(line.decode("utf-8"))
                            token = partial.get("response", "")
                            yield f"data: {token}\n\n"
                        except json.JSONDecodeError:
                            continue

        return StreamingHttpResponse(stream(), content_type="text/event-stream")

    except Exception as e:
        return JsonResponse({"reply": f"⚠️ Error: {str(e)}"})