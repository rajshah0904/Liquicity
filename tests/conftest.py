import os
import sys

# Ensure project root is on the Python path for imports in tests
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root) 
import sys

# Ensure project root is on the Python path for imports in tests
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root not in sys.path:
    sys.path.insert(0, root) 