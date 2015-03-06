import arrow
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
    
    # Turn the generated time into Eastern
    generated_at_dt = arrow.get(data['generated']).to('US/Eastern')
    generated_at = generated_at_dt.format('M/d/YYYY HH:mm:ssa') + ' ET'
        
    # Write the template
    delays = []
    
    for item in data['airports']:
        if item['delay']['type'] is not None:
            delays.append(item)
    
    html_output = index_template.render({
        'delays': delays,
        'generated_at': generated_at,
    })
    
    with open('index.html', 'w') as f:
        f.write(html_output)
    
