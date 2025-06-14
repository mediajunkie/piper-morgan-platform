# 1. Map the current codebase structure
find . -name "*.py" | head -20
ls -la services/ 2>/dev/null || echo "No services dir"

# 2. Identify the main entry points
grep -r "if __name__" . --include="*.py"
grep -r "FastAPI\|app\|uvicorn" . --include="*.py"

# 3. Find the broken functionality
grep -r "def.*intent\|def.*workflow\|def.*github" . --include="*.py"
