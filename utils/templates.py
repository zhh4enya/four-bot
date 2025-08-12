import os

def load_template(template_name, variables=None):
    try:
        template_path = os.path.join('templates', template_name)
        
        if not os.path.exists(template_path):
            print(f"[!] template {template_name} not found")
            return "[!] template not found"
        
        with open(template_path, 'r', encoding='utf-8') as file:
            template_content = file.read()
        
        if variables:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                template_content = template_content.replace(placeholder, str(value))
        
        return template_content
        
    except Exception as e:
        print(f"[!] error during loading template {template_name}: {e}")
        return "[!] error during loading"