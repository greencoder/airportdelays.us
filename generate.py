import jinja2
import json

if __name__ == "__main__":
    
    # Load the template
    template_loader = jinja2.FileSystemLoader('.')
    template_env = jinja2.Environment(loader=template_loader)
    index_template = template_env.get_template('index.tpl.html')
    
    # Load the delays
    with open('delays.json', 'r') as f:
        data = json.loads(f.read())
        
    # Write the template
    delays = []
    
    for item in data:
        if item['delay']['type'] is not None:
            delays.append(item)
    
    print delays[0]
    
    html_output = index_template.render({
        'delays': delays,
    })
    
    with open('index.html', 'w') as f:
        f.write(html_output)
    