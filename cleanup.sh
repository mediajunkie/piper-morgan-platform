# Nuclear option - recreate the venv completely
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
which python  # Should work now
pip install -r requirements.txt
