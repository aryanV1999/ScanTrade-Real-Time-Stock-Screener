import os
import sys
import subprocess

def main():
    # ✅ Handle PyInstaller's temporary directory extraction
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS  # PyInstaller extracts files here
    else:
        base_path = os.path.dirname(__file__)

    # ✅ Get the absolute path of `main.py`
    app_path = os.path.join(base_path, 'main.py')

    if not os.path.exists(app_path):
        print(f"❌ Error: {app_path} not found!")
        sys.exit(1)

    print(f"✅ Running: {app_path}")
    
    # ✅ Run Streamlit from the embedded script
    subprocess.run(["streamlit", "run", app_path])

if __name__ == "__main__":
    main()
