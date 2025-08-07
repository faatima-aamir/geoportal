// Wait for DOM to be ready before creating Vue instance
document.addEventListener('DOMContentLoaded', () => {
    // Create Vue instance
    new Vue({
        el: '#app',
        data: {
            map: null,
            drawnItems: null,
            geoLayer: null,
            bufferLayer: null,
            geojsonData: null,
            uploadedFile: null,
            visible: true,
            message: '',
            bufferDistance: 1.0,
            showTable: false,
            attributeHeaders: [],
            attributeData: [],
            mapInitialized: false
        },
        mounted() {
            // Initialize map after Vue is mounted
            this.initMap();
        },
        methods: {
            initMap() {
                try {
                    // Initialize map
                    this.map = L.map('map').setView([30.0, 70.0], 5);
                    
                    // Add base layer
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap contributors'
                    }).addTo(this.map);
                    
                    // Initialize draw control
                    this.drawnItems = new L.FeatureGroup();
                    this.map.addLayer(this.drawnItems);
                    
                    const drawControl = new L.Control.Draw({
                        draw: {
                            polygon: true,
                            polyline: false,
                            rectangle: false,
                            circle: false,
                            marker: false
                        },
                        edit: {
                            featureGroup: this.drawnItems
                        }
                    });
                    this.map.addControl(drawControl);

                    // Set up draw created event
                    this.map.on('draw:created', (e) => {
                        this.drawnItems.clearLayers();
                        this.drawnItems.addLayer(e.layer);
                        this.message = 'Polygon drawn successfully';
                    });

                    this.mapInitialized = true;
                    this.message = 'Map initialized successfully';
                } catch (error) {
                    console.error('Map initialization error:', error);
                    this.message = 'Error initializing map';
                }
            },
            async handleFileUpload(event) {
                const file = event.target.files[0];
                if (!file) return;

                this.message = 'Reading file...';
                const fileName = file.name.toLowerCase();

                try {
                    if (fileName.endsWith('.geojson') || fileName.endsWith('.json')) {
                        const text = await file.text();
                        const geojson = JSON.parse(text);
                        this.displayGeoJSON(geojson);
                    } else if (fileName.endsWith('.zip')) {
                        const buffer = await file.arrayBuffer();
                        const geojson = await shp(buffer);
                        this.displayGeoJSON(geojson);
                    } else {
                        this.message = 'Please upload a GeoJSON or Shapefile (ZIP)';
                    }
                } catch (error) {
                    console.error('File processing error:', error);
                    this.message = 'Error processing file';
                }
            },
            displayGeoJSON(geojson) {
                if (!this.mapInitialized) {
                    this.message = 'Map not initialized';
                    return;
                }

                try {
                    if (this.geoLayer) {
                        this.map.removeLayer(this.geoLayer);
                    }

                    this.geoLayer = L.geoJSON(geojson, {
                        style: {
                            color: 'green',
                            weight: 2,
                            opacity: 0.8,
                            fillOpacity: 0.3
                        },
                        onEachFeature: (feature, layer) => {
                            if (feature.properties) {
                                const content = Object.entries(feature.properties)
                                    .map(([key, value]) => `<strong>${key}:</strong> ${value}`)
                                    .join('<br>');
                                layer.bindPopup(content);
                            }
                        }
                    });

                    this.map.addLayer(this.geoLayer);
                    this.map.fitBounds(this.geoLayer.getBounds());
                    
                    this.geojsonData = geojson;
                    this.message = 'Layer added successfully';
                    this.showAttributes();
                } catch (error) {
                    console.error('Error displaying GeoJSON:', error);
                    this.message = 'Error displaying data';
                }
            },
            showAttributes() {
                if (!this.geojsonData?.features?.length) {
                    this.message = 'No data to display';
                    return;
                }

                try {
                    const firstFeature = this.geojsonData.features[0];
                    if (firstFeature.properties) {
                        this.attributeHeaders = Object.keys(firstFeature.properties);
                        this.attributeData = this.geojsonData.features.map(f => f.properties);
                        this.showTable = true;
                        this.message = `Showing ${this.geojsonData.features.length} features`;
                    } else {
                        this.message = 'No attributes found';
                    }
                } catch (error) {
                    console.error('Error showing attributes:', error);
                    this.message = 'Error displaying attributes';
                }
            },
            toggleLayer() {
                if (!this.geoLayer) {
                    this.message = 'No layer to toggle';
                    return;
                }

                try {
                    if (this.visible) {
                        this.map.removeLayer(this.geoLayer);
                    } else {
                        this.map.addLayer(this.geoLayer);
                    }
                    this.visible = !this.visible;
                    this.message = this.visible ? 'Layer shown' : 'Layer hidden';
                } catch (error) {
                    console.error('Error toggling layer:', error);
                    this.message = 'Error toggling layer';
                }
            },
            bufferDrawnLayer() {
                if (!this.mapInitialized) {
                    this.message = 'Map not initialized';
                    return;
                }

                try {
                    const layers = this.drawnItems.getLayers();
                    if (!layers.length) {
                        this.message = 'Draw a polygon first';
                        return;
                    }

                    if (!this.bufferDistance || this.bufferDistance <= 0) {
                        this.message = 'Enter a valid buffer distance';
                        return;
                    }

                    const layer = layers[0];
                    const coords = layer.getLatLngs()[0];
                    const points = coords.map(coord => [coord.lng, coord.lat]);
                    points.push(points[0]); // Close the polygon

                    const polygon = turf.polygon([points]);
                    const buffered = turf.buffer(polygon, this.bufferDistance, {
                        units: 'kilometers'
                    });

                    if (this.bufferLayer) {
                        this.map.removeLayer(this.bufferLayer);
                    }

                    this.bufferLayer = L.geoJSON(buffered, {
                        style: {
                            color: 'blue',
                            weight: 2,
                            opacity: 0.8,
                            fillOpacity: 0.2
                        }
                    });

                    this.map.addLayer(this.bufferLayer);
                    this.map.fitBounds(this.bufferLayer.getBounds());
                    this.message = `${this.bufferDistance}km buffer created`;
                } catch (error) {
                    console.error('Error creating buffer:', error);
                    this.message = 'Error creating buffer';
                }
            },
            clearMap() {
                if (!this.mapInitialized) {
                    return;
                }

                try {
                    this.drawnItems.clearLayers();
                    
                    if (this.geoLayer) {
                        this.map.removeLayer(this.geoLayer);
                        this.geoLayer = null;
                    }
                    
                    if (this.bufferLayer) {
                        this.map.removeLayer(this.bufferLayer);
                        this.bufferLayer = null;
                    }

                    this.geojsonData = null;
                    this.showTable = false;
                    this.attributeHeaders = [];
                    this.attributeData = [];
                    this.message = 'Map cleared';
                } catch (error) {
                    console.error('Error clearing map:', error);
                    this.message = 'Error clearing map';
                }
            },
            logout() {
                fetch('/logout/', {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrftoken }
                }).then(() => window.location.href = '/');
            }
        }
    });
});
