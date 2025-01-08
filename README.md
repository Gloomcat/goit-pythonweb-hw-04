# Async File Copy

Project contains the script is an **asynchronous file copying tool** that recursively processes files from a source directory and organizes them into subdirectories in an output directory based on file extensions. It leverages Python's **asyncio** for concurrency and supports real-time progress tracking.

---

## 📋 **Features**
- Asynchronous file processing using **asyncio**.
- Real-time progress tracking.
- Error handling for permission issues and missing files.
- Automatic directory creation based on file extensions.

---

## 🧩 **Prerequisites**
Ensure you have Python **3.9+** installed on your system.

### ✅ **Setting Up a Virtual Environment**
It is recommended to use a virtual environment to manage your dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate.ps1

# On macOS/Linux
source venv/bin/activate
```

### ✅ **Install Dependencies**
Run the following command to install the required packages from the **`requirements.txt`** file:

```bash
pip install -r requirements.txt
```

---

## 🚀 **Usage**
Run the script using the following command:

```bash
python main.py --source <SOURCE_DIR> --out <OUTPUT_DIR>
```

### Example:
```bash
python main.py --source ./input --out ./output
```
This command will copy all files from the `./input` directory to the `./output` directory, organizing them by file extension.

---

## 🧪 **Testing**
You can test the script by creating sample directories and files:

```bash
mkdir input
mkdir input/subdir

echo "Test File 1" > input/file1.txt
echo "Test File 2" > input/subdir/file2.txt
```

Then run:
```bash
python main.py --source ./input --out ./output
```
