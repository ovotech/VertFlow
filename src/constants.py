# A cache of all Cloud Run regions and their location. Cached, rather than fetched dynamically at runtime, to improve performance.
from typing import List, Dict, Union

# https://www.cloudcarbonfootprint.org/docs/methodology
PUE = 1.1
MIN_WATTS: float = 0.71
MAX_WATTS: float = 4.26
AVG_VCPU_UTILISATION: float = 0.5
AVERAGE_WATTS: float = (MIN_WATTS + AVG_VCPU_UTILISATION * (MAX_WATTS - MIN_WATTS)) * PUE

ALL_CLOUD_RUN_REGIONS: List[Dict[str, Union[str, float]]] = [
    {"id": "asia-east1", "name": "Taiwan", "lat": 23.9739374, "lon": 120.9820179},
    {"id": "asia-east2", "name": "Hong Kong", "lat": 22.2793278, "lon": 114.1628131},
    {"id": "asia-northeast1", "name": "Tokyo", "lat": 35.6828387, "lon": 139.7594549},
    {"id": "asia-northeast2", "name": "Osaka", "lat": 34.6198813, "lon": 135.490357},
    {"id": "asia-northeast3", "name": "Seoul", "lat": 37.5666791, "lon": 126.9782914},
    {"id": "asia-south1", "name": "Mumbai", "lat": 19.0785451, "lon": 72.878176},
    {"id": "asia-south2", "name": "Delhi", "lat": 28.6517178, "lon": 77.2219388},
    {"id": "asia-southeast1", "name": "Singapore", "lat": 1.357107, "lon": 103.8194992},
    {"id": "asia-southeast2", "name": "Jakarta", "lat": -6.1753942, "lon": 106.827183},
    {
        "id": "australia-southeast1",
        "name": "Sydney",
        "lat": -33.8698439,
        "lon": 151.2082848,
    },
    {
        "id": "australia-southeast2",
        "name": "Melbourne",
        "lat": -37.8142176,
        "lon": 144.9631608,
    },
    {
        "id": "europe-central2",
        "name": "Warsaw",
        "lat": 52.2337172,
        "lon": 21.071432235636493,
    },
    {"id": "europe-north1", "name": "Finland", "lat": 63.2467777, "lon": 25.9209164},
    {"id": "europe-southwest1", "name": "Madrid", "lat": 40.4167047, "lon": -3.7035825},
    {"id": "europe-west1", "name": "Belgium", "lat": 50.6402809, "lon": 4.6667145},
    {"id": "europe-west2", "name": "London", "lat": 51.5073219, "lon": -0.1276474},
    {"id": "europe-west3", "name": "Frankfurt", "lat": 50.1106444, "lon": 8.6820917},
    {"id": "europe-west4", "name": "Netherlands", "lat": 52.2434979, "lon": 5.6343227},
    {"id": "europe-west6", "name": "Zurich", "lat": 47.3744489, "lon": 8.5410422},
    {"id": "europe-west8", "name": "Milan", "lat": 45.4641943, "lon": 9.1896346},
    {
        "id": "europe-west9",
        "name": "Paris",
        "lat": 48.8588897,
        "lon": 2.3200410217200766,
    },
    {"id": "europe-west12", "name": "Turin", "lat": 45.0703, "lon": 7.6869},
    {"id": "me-central1", "name": "Doha", "lat": 25.2854, "lon": 51.5310},
    {"id": "me-west1", "name": "Tel Aviv", "lat": 32.0852997, "lon": 34.7818064},
    {
        "id": "northamerica-northeast1",
        "name": "Montréal",
        "lat": 45.5031824,
        "lon": -73.5698065,
    },
    {
        "id": "northamerica-northeast2",
        "name": "Toronto",
        "lat": 43.6534817,
        "lon": -79.3839347,
    },
    {
        "id": "southamerica-east1",
        "name": "São Paulo",
        "lat": -23.5506507,
        "lon": -46.6333824,
    },
    {
        "id": "southamerica-west1",
        "name": "Santiago",
        "lat": 9.8694792,
        "lon": -83.7980749,
    },
    {"id": "us-central1", "name": "Iowa", "lat": 41.9216734, "lon": -93.3122705},
    {"id": "us-east1", "name": "South Carolina", "lat": 33.6874388, "lon": -80.4363743},
    {
        "id": "us-east4",
        "name": "Northern Virginia",
        "lat": -12.548285,
        "lon": 131.017405,
    },
    {"id": "us-east5", "name": "Columbus", "lat": 39.9622601, "lon": -83.0007065},
    {"id": "us-south1", "name": "Dallas", "lat": 32.7762719, "lon": -96.7968559},
    {"id": "us-west1", "name": "Oregon", "lat": 43.9792797, "lon": -120.737257},
    {"id": "us-west2", "name": "Los Angeles", "lat": 34.0536909, "lon": -118.242766},
    {
        "id": "us-west3",
        "name": "Salt Lake City",
        "lat": 40.7596198,
        "lon": -111.8867975,
    },
    {"id": "us-west4", "name": "Las Vegas", "lat": 36.1672559, "lon": -115.148516},
]
