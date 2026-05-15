import os

def create_structure():
    # Define the professional folder structure
    project_structure = [
        "data/",
        "chroma_db/",
        "src/__init__.py",
        "src/engine.py",
        "src/utils.py",
        "app.py",
        ".env",
        "requirements.txt"
    ]

    print("🏗️ Creating project structure...")

    for path in project_structure:
        if path.endswith("/"):
            # It's a directory
            os.makedirs(path, exist_ok=True)
            print(f"Created Directory: {path}")
        else:
            # It's a file
            dir_name = os.path.dirname(path)
            if dir_name: # Only create if there's a sub-directory
                os.makedirs(dir_name, exist_ok=True)
            
            if not os.path.exists(path):
                with open(path, "w") as f:
                    pass
                print(f"Created File:      {path}")

    print("\n✅ Setup complete! Your professional project is ready.")

if __name__ == "__main__":
    create_structure()