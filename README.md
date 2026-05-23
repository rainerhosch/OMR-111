# OMR REST API Microservice

Microservice berbasis **FastAPI** dan **OpenCV** untuk sistem Optical Mark Recognition (OMR). Service ini bertugas untuk menerima gambar pindaian/foto potongan Lembar Jawaban Komputer (LJK) bagian **jawaban (1-100)**, mendeteksi bulatan mana yang telah dihitamkan, lalu mengembalikan hasilnya dalam format JSON.

Sistem ini didesain agar Frontend (atau backend utama seperti CodeIgniter) melakukan *cropping* terlebih dahulu terhadap area jawaban pada LJK, sehingga API ini dapat bekerja dengan sangat cepat dan presisi menggunakan algoritma **Ratio-Gap v5**.

## Fitur Utama
- Deteksi jawaban 1-100 (A, B, C, D, E) dengan tingkat akurasi tinggi.
- Otomatis melakukan deteksi *Double-filled* (jawaban ganda akan mereturn `"INVALID"`).
- Resizing otomatis gambar *input* menjadi standar grid internal (713x418).
- Output JSON yang mudah digunakan oleh aplikasi web lain.
- Siap di-deploy menggunakan **Docker**.

---

## 🚀 Cara Menjalankan Service

### Opsi A: Menggunakan Docker (Direkomendasikan untuk Production)

Cara termudah dan paling aman untuk menjalankan service ini di server (VPS/Cloud) adalah menggunakan Docker, karena semua masalah *environment* dan instalasi OpenCV terisolasi dengan aman.

1. **Build Image Docker:**
   ```bash
   docker build -t omr-microservice .
   ```

2. **Jalankan Container:**
   ```bash
   docker run -d -p 8000:8000 --name omr-api omr-microservice
   ```
   *Service sekarang berjalan di `http://localhost:8000`*

### Opsi B: Menjalankan Secara Lokal (Untuk Development)

Jika Anda ingin menjalankan atau memodifikasi script secara lokal di Windows/Mac/Linux:

1. Buat dan aktifkan virtual environment (contoh menggunakan Conda):
   ```bash
   conda create -n omr-fastapi python=3.10
   conda activate omr-fastapi
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server Uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## 📖 Dokumentasi API

Anda bisa mengakses halaman UI interaktif (Swagger UI) untuk melakukan pengujian langsung dengan membuka browser ke:
👉 **http://localhost:8000/docs**

### Endpoint: Scan LJK

- **URL:** `/api/v1/scan-ljk`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`

#### Parameter Input (Form-Data)

| Nama Parameter  | Tipe   | Keterangan |
| :--- | :--- | :--- |
| `file`          | File   | **(Wajib)** Gambar/foto LJK yang **sudah di-crop (dipotong)** khusus pada bagian kotak jawaban soal nomor 1-100. |
| `id_peserta`    | String | (Opsional) Nomor urut / ID peserta. |
| `program_studi` | String | (Opsional) Nama Program Studi. |
| `waktu_kuliah`  | String | (Opsional) Keterangan Waktu Kuliah (Pagi/Sore). |

#### Contoh Response (JSON)

Jika proses ekstraksi berhasil, API akan mengembalikan HTTP Status `200 OK` dengan format berikut:

```json
{
  "status": "success",
  "data_peserta": {
    "nomor_peserta": "123456789",
    "program_studi": "Teknik Informatika",
    "waktu_kuliah": "Pagi"
  },
  "jawaban": {
    "1": "",
    "2": "",
    "3": "A",
    "4": "",
    "5": "E",
    "27": "B",
    "51": "INVALID",
    "100": "E"
  }
}
```

*Keterangan Hasil Jawaban:*
- `""` (String kosong): Berarti soal tersebut kosong atau tidak diisi.
- `"A"`, `"B"`, dst: Jawaban yang dihitamkan.
- `"INVALID"`: Peserta menghitamkan 2 atau lebih pilihan ganda pada satu nomor soal yang sama, atau ada coretan tebal yang ambigu.

---

## 🛠️ Tech Stack
- **Python 3.10**
- **FastAPI** (Web Framework)
- **OpenCV** (`opencv-python-headless`) (Computer Vision)
- **Uvicorn** (ASGI Server)
