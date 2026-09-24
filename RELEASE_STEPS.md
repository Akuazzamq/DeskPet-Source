# 🚀 Panduan Rilis DeskPet ke GitHub (Closed-Source Freeware)

Dokumen ini memandu kamu untuk merilis DeskPet secara gratis di GitHub tanpa membocorkan atau mempublikasikan kode sumber Python (`.py`).

---

## 📁 1. Struktur Rilis yang Sudah Disiapkan

Folder **`release_bundle/`** telah dibuat secara otomatis dan berisi:
* **`README.md`**: Halaman utama yang keren dan profesional dengan logo, badge, showcase animasi, dan panduan instalasi.
* **`LICENSE`**: Lisensi Freeware EULA resmi (Aplikasi gratis digunakan, hak cipta penuh milik AzzamQ).
* **`install.ps1`**: Skrip installer 1-baris otomatis via PowerShell.
* **`artifacts/` & `assets/`**: Gambar preview dan logo aplikasi.
* **`binaries/`**: File hasil kompilasi yang akan diupload ke GitHub Releases:
  - `DeskPet-Setup.exe` (Installer Windows resmi)
  - `DeskPet-Windows.zip` (Versi portable)
  - `install.ps1`
  - `SHA256SUMS.txt` (Checksum keamanan)

*(⚠️ Tidak ada satu pun file `.py` di dalam folder ini!)*

---

## 🌐 2. Langkah-Langkah Publikasi di GitHub

### Langkah A: Buat Repositori GitHub Baru
1. Buka [GitHub New Repository](https://github.com/new).
2. Isi nama repositori: **`DeskPet`** (atau sesuai keinginan).
3. Set visibilitas ke **Public**.
4. Biarkan opsi lain (Add README, .gitignore, License) kosong (karena sudah kita siapkan).
5. Klik **Create repository**.

### Langkah B: Upload File Publik ke Repositori
Jalankan perintah berikut di PowerShell atau upload folder `release_bundle`:

```powershell
cd release_bundle
git init
git add README.md LICENSE install.ps1 artifacts/ assets/
git commit -m "DeskPet Initial Release v0.1.0-beta"
git branch -M main
git remote add origin https://github.com/Akuazzamq/DeskPet.git
git push -u origin main
```

*(Catatan: Folder `binaries/` jangan di-commit ke git repo langsung, melainkan diunggah ke menu Releases di Langkah C di bawah).*

---

### Langkah C: Buat GitHub Release & Upload Aplikasi
1. Buka repositori `https://github.com/Akuazzamq/DeskPet`.
2. Di sebelah kanan, klik **Releases** > **Create a new release** (atau *Draft a new release*).
3. Isi kolom:
   - **Tag version**: `v0.1.0-beta` (atau `v1.0.0`)
   - **Release title**: `DeskPet v0.1.0-beta - Pixel Desktop Companion`
   - **Description**: 
     ```markdown
     ## ✨ DeskPet v0.1.0 Beta
     A pixel-art desktop companion for Windows featuring 10 species, 21 skins, and Pomodoro time tools!
     
     ### ⬇️ Downloads
     * **Installer Wizard:** `DeskPet-Setup.exe`
     * **Portable ZIP:** `DeskPet-Windows.zip`
     ```
4. Drag-and-drop 4 file dari folder `release_bundle/binaries/`:
   - `DeskPet-Setup.exe`
   - `DeskPet-Windows.zip`
   - `install.ps1`
   - `SHA256SUMS.txt`
5. Centang **Set as latest release** dan klik **Publish release**! 🎉

---

## ⚡ Hasil Akhir untuk Pengguna / Teman Kamu

Setelah dipublikasikan, siapa pun bisa langsung menginstal DeskPet hanya dengan mengetik 1 baris di PowerShell mereka:

```powershell
irm https://raw.githubusercontent.com/Akuazzamq/DeskPet/main/install.ps1 | iex
```
Atau langsung mengunduh `DeskPet-Setup.exe` dari halaman Releases kamu!

