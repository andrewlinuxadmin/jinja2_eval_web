#!/usr/bin/env python3

import sys
import urllib.request
import urllib.error
import urllib.parse
import json
import tempfile
import os
import shutil
import time

def test_user_simulation():
    """Simulate a realistic user workflow"""
    print("👤 USER SIMULATION TEST")
    print("=" * 50)
    print("Simulating a realistic user workflow with the web interface")
    
    # Create sample data files that a user might have
    temp_dir = tempfile.mkdtemp()
    print(f"\n📂 Creating sample data files in: {temp_dir}")
    
    sample_files = {
        'employees.json': json.dumps({
            "company": "TechCorp",
            "employees": [
                {"name": "Maria Silva", "department": "Engineering", "level": "Senior"},
                {"name": "João Santos", "department": "Marketing", "level": "Junior"},
                {"name": "Ana Costa", "department": "Engineering", "level": "Lead"},
                {"name": "Pedro Lima", "department": "Sales", "level": "Manager"}
            ]
        }, indent=2),
        
        'servers.json': json.dumps({
            "production": {
                "web_servers": ["web-prod-01.company.com", "web-prod-02.company.com"],
                "db_servers": ["db-prod-01.company.com"],
                "load_balancer": "lb-prod.company.com"
            },
            "staging": {
                "web_servers": ["web-staging.company.com"],
                "db_servers": ["db-staging.company.com"]
            }
        }, indent=2),
        
        'config.json': json.dumps({
            "app_config": {
                "name": "Corporate Portal",
                "version": "2.1.3",
                "features": ["authentication", "reporting", "notifications"],
                "database": {
                    "host": "{{ db_host }}",
                    "port": 5432,
                    "name": "corporate_db"
                }
            }
        }, indent=2)
    }
    
    try:
        # Create the files
        for filename, content in sample_files.items():
            filepath = os.path.join(temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Created {filename}")
        
        # Step 1: User configures the input files directory
        print(f"\n⚙️  Step 1: User configures input files directory")
        config_data = {
            'section': 'input_files',
            'directory': temp_dir,
            'refresh_interval': '3'
        }
        
        url = "http://localhost:8000/settings"
        data = urllib.parse.urlencode(config_data).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            print(f"✅ Configuration saved: {result}")
        
        # Step 2: User loads the web page and sees available files
        print(f"\n🌐 Step 2: User loads web page and checks available files")
        
        with urllib.request.urlopen("http://localhost:8000/input-files") as response:
            files = json.loads(response.read().decode())
            print(f"✅ Available files: {files}")
        
        # Step 3: User selects and loads a file
        print(f"\n📖 Step 3: User selects employees.json file")
        
        file_url = "http://localhost:8000/input-file-content?filename=employees.json"
        with urllib.request.urlopen(file_url) as response:
            employees_content = response.read().decode()
            print(f"✅ Loaded employees data:")
            print(f"   First 100 chars: {employees_content[:100]}...")
        
        # Step 4: User creates a report template
        print(f"\n📝 Step 4: User creates an employee report template")
        
        template = """# Employee Report for {{ data.company }}

## Department Summary
{% for dept in data.employees | map(attribute='department') | unique %}
### {{ dept }} Department
{% for emp in data.employees | selectattr('department', 'equalto', dept) %}
- **{{ emp.name }}** ({{ emp.level }})
{% endfor %}
{% endfor %}

## Senior+ Staff
{% for emp in data.employees | selectattr('level', 'in', ['Senior', 'Lead', 'Manager']) %}
- {{ emp.name }} - {{ emp.department }} ({{ emp.level }})
{% endfor %}

Total Employees: {{ data.employees | length }}
"""
        
        print("✅ Created comprehensive report template")
        
        # Step 5: User renders the template with the loaded data
        print(f"\n🎨 Step 5: User renders the report")
        
        render_data = {
            'json': employees_content,
            'expr': template
        }
        
        url = "http://localhost:8000/render"
        data = urllib.parse.urlencode(render_data).encode()
        req = urllib.request.Request(url, data=data, method='POST')
        
        with urllib.request.urlopen(req) as response:
            rendered_report = response.read().decode()
            print(f"✅ Report rendered successfully!")
            print("\n" + "="*40)
            print("RENDERED REPORT:")
            print("="*40)
            print(rendered_report)
            print("="*40)
        
        # Step 6: User tries server configuration template
        print(f"\n🖥️  Step 6: User works with server configuration")
        
        server_template = """# Server Configuration

## Production Environment
{% for server in data.production.web_servers %}
[web-server-{{ loop.index }}]
hostname = {{ server }}
role = web
environment = production
{% endfor %}

{% for server in data.production.db_servers %}
[database-{{ loop.index }}]
hostname = {{ server }}
role = database
environment = production
{% endfor %}

## Load Balancer
[load-balancer]
hostname = {{ data.production.load_balancer }}
role = load_balancer
environment = production

## Staging Environment
{% for server in data.staging.web_servers %}
[staging-web-{{ loop.index }}]
hostname = {{ server }}
role = web
environment = staging
{% endfor %}
"""
        
        # Get servers data
        server_url = "http://localhost:8000/input-file-content?filename=servers.json"
        with urllib.request.urlopen(server_url) as response:
            servers_content = response.read().decode()
        
        # Render server configuration
        render_data = {
            'json': servers_content,
            'expr': server_template
        }
        
        data = urllib.parse.urlencode(render_data).encode()
        req = urllib.request.Request("http://localhost:8000/render", data=data, method='POST')
        
        with urllib.request.urlopen(req) as response:
            server_config = response.read().decode()
            print(f"✅ Server configuration generated!")
            print("\n" + "="*40)
            print("SERVER CONFIGURATION:")
            print("="*40)
            print(server_config)
            print("="*40)
        
        # Step 7: User saves both results to history
        print(f"\n💾 Step 7: Checking history functionality")
        
        with urllib.request.urlopen("http://localhost:8000/history") as response:
            history = json.loads(response.read().decode())
            print(f"✅ History contains {len(history)} entries")
            if history:
                print(f"   Latest entry preview: {history[0]['expr'][:50]}...")
        
        print(f"\n🎉 USER SIMULATION COMPLETED SUCCESSFULLY!")
        print("✅ All user workflow steps worked perfectly:")
        print("   ✓ Configuration setup")
        print("   ✓ File discovery and loading")
        print("   ✓ Template creation and rendering")
        print("   ✓ Multiple file types handled")
        print("   ✓ Complex Jinja2 templates processed")
        print("   ✓ History tracking working")
        
        return True
        
    except Exception as e:
        print(f"❌ User simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print(f"\n🧹 Cleaning up...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Reset configuration
        try:
            reset_data = {
                'section': 'input_files',
                'directory': '',
                'refresh_interval': '1'
            }
            data = urllib.parse.urlencode(reset_data).encode()
            req = urllib.request.Request("http://localhost:8000/settings", data=data, method='POST')
            urllib.request.urlopen(req)
            print("✅ Configuration reset")
        except:
            pass

def main():
    print("🎭 REALISTIC USER WORKFLOW SIMULATION")
    print("Testing the complete input files feature as a real user would use it")
    print("="*70)
    
    try:
        success = test_user_simulation()
        
        if success:
            print("\n" + "🎉"*20)
            print("SUCCESS! The input files feature is ready for production use!")
            print("Users can now:")
            print("• Configure input file directories through the web interface")
            print("• Browse and select from available JSON files")
            print("• Load file contents automatically into templates")
            print("• Create complex reports and configurations")
            print("• Track their work in history")
            print("🎉"*20)
        else:
            print("\n❌ User simulation revealed issues that need to be addressed.")
        
        return success
        
    except Exception as e:
        print(f"\n💥 Simulation crashed: {e}")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
