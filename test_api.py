import requests
import json

url = "http://127.0.0.1:8000/api/v1/scan-ljk"
image_path = "data_image_test/isi.jpeg"

data = {
    "id_peserta": "123456789",
    "program_studi": "Teknik Informatika",
    "waktu_kuliah": "Pagi"
}

print(f"Testing API {url} with image {image_path}")

try:
    with open(image_path, "rb") as img_file:
        files = {"file": ("isi-crop-jwb.jpeg", img_file, "image/jpeg")}
        response = requests.post(url, data=data, files=files)
        
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
