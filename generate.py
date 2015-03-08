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

    # Turn the nested dictionary into an easy-to-parse data structure
    delays = []

    for item in data['airports']:

        if item['delay']['type'] is not None:
            
            # Figure out the details
            if item['delay']['details']['avgDelay']:
                details = item['delay']['details']['avgDelay']
            elif item['delay']['details']['endTime']:
                details = item['delay']['details']['endTime']
            else:
                details = "N/A"
            
            delays.append({
                'airport_name': item['name'],
                'airport_code': item['iata-code'],
                'delay_type': item['delay']['details']['type'],
                'delay_reason': item['delay']['details']['reason'],
                'details': details,
            })

    # Write the template
    html_output = index_template.render({
        'delays': delays,
        'generated_at': generated_at,
    })
    
    with open('index.html', 'w') as f:
        f.write(html_output)
    
