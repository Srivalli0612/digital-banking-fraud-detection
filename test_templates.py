import sys
from flask import Flask
from jinja2 import Environment, FileSystemLoader, TemplateAssertionError

# Create a minimal Flask app to test templates
app = Flask(__name__, template_folder='templates')

# Try to load and compile each template
templates_to_test = ['welcome.html', 'base.html', 'login.html', 'dashboard.html']

env = Environment(loader=FileSystemLoader('templates'))

print("Testing Jinja2 template compilation...")
print("-" * 50)

errors_found = False
for template_name in templates_to_test:
    try:
        template = env.get_template(template_name)
        print(f"✓ {template_name}: OK")
    except TemplateAssertionError as e:
        print(f"✗ {template_name}: ERROR - {str(e)}")
        errors_found = True
    except Exception as e:
        print(f"✗ {template_name}: ERROR - {type(e).__name__}: {str(e)}")
        errors_found = True

print("-" * 50)
if not errors_found:
    print("All templates compiled successfully!")
else:
    print("Some templates have errors.")
    sys.exit(1)
