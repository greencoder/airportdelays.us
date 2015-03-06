import BeautifulSoup
import json
import requests
import sys

if __name__ == "__main__":

    with open('airports.json', 'r') as f:
        airports_metadata = json.loads(f.read())

    # Only index the airports iwth IATA codes
    airports_by_iata_code = {}
    for airport_metadata in airports_metadata:
        code = airport_metadata['iata-code']
        if code:
            airports_by_iata_code[code] = airport_metadata

    sources = [
        ("Northwestern States", "http://www.fly.faa.gov/flyfaa/nwmap.jsp"),
        ("North Central States", "http://www.fly.faa.gov/flyfaa/ncmap.jsp"),
        ("Northeastern States", "http://www.fly.faa.gov/flyfaa/nemap.jsp"),
        ("Southwestern States", "http://www.fly.faa.gov/flyfaa/swmap.jsp"),
        ("South Central States", "http://www.fly.faa.gov/flyfaa/scmap.jsp"),
        ("Alaska and Hawaii", "http://www.fly.faa.gov/flyfaa/fwmap.jsp"),
    ]

    airports = []

    for source in sources:

        name = source[0]
        map_url = source[1]

        print "Processing Delays for Region: %s" % name
        print " - %s" % map_url

        # Request the URL and turn it into soup
        try:
            map_request = requests.get(map_url, timeout=20)
            soup = BeautifulSoup.BeautifulSoup(map_request.text)
        except requests.Timeout:
            print "Connection timed out."
            continue

        # Find the <dl class="map"> element
        dl_el = soup.find('dl', {'class': 'map'})

        # Loop over the element and find all the <dt> and <dd> elements
        for dt_el in dl_el.findAll('dt'):

            # The airport code is in the <dt element>
            airport_code = dt_el.a['id'].upper()

            # Find the next <dd> element
            dd_el = dt_el.findNext('dd')

            # The element looks like this:
            # <dd>
            #    <div align="center">
            #        <b>Walla Walla City County Airport (ALW)<br />Walla Walla, Washington</b>
            #     </div>
            #    <hr size="1" />
            #    General Arrival/Departure delays are 15 minutes or less.
            # </dd>

            # We can extract the airport name and location
            airport_name = dd_el.div.b.contents[0]
            
            # The airport name includes the code in parens. Strip that out.
            # e.g. Walla Walla City County Airport (ALW)
            airport_name = airport_name[0:-6].strip()
            
            airport_location = dd_el.div.b.contents[-1].strip()
            airport_location_info = {}

            airport_delay_text = dd_el.contents[-1].strip()

            # Construct the URL for the realtime status page
            airport_status_url = "http://www.fly.faa.gov/flyfaa/flyfaaindex.jsp?ARPT=%s&p=0" % airport_code

            airport_location_metadata = {
                'name': airport_location,
                'lat': None,
                'lng': None,
                'altitude': None,
                'city': None,
            }

            # Get the metadata for this airport
            try:
                metadata = airports_by_iata_code[airport_code]
                airport_location_metadata['lat'] = metadata['lat']
                airport_location_metadata['lng'] = metadata['lng']
                airport_location_metadata['altitude'] = metadata['altitude']
                airport_location_metadata['city'] = metadata['city']
            except KeyError:
                print "Missing Metadata for Airport Code: %s" % airport_code

            # By default, an airport has no delay
            delay = { 'type': None, 'details': None }

            # If we find a non-normal delay, then we need to request additional info
            if airport_delay_text != "General Arrival/Departure delays are 15 minutes or less.":
                
                print "Found a delay, requesting extended information for airport %s" % airport_code
                
                try:
                    detail_url = "http://services.faa.gov/airport/status/%s?format=application/json" % airport_code
                    detail_request = requests.get(detail_url, timeout=20)
                    detail_data = detail_request.json()
                except requests.Timeout:
                    print "Request for information timed out."
                    detail_data = {}
                
                # If it times out, we just put "Unknown"
                if detail_data.keys() and detail_data['status']['type'] is not None:
                    delay['details'] = detail_data['status']
                    delay['type'] = detail_data['status']['type']
                else:
                    delay['details'] = {}
                    delay['type'] = "Unknown"

            airports.append({
                'iata-code': airport_code,
                'name': airport_name,
                'location': airport_location_metadata,
                'delay': delay,
                'status-url': airport_status_url,
            })

        with open('delays.json', 'w') as f:
            f.write(json.dumps(airports, indent=4))
