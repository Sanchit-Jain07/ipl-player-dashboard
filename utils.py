import os, json
json_files = []
directory = './match_data'

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        json_files.append(filename)

def unique_venues():
    venues = set()
    for filename in json_files:
        with open(f'./match_data/{filename}') as file:
            data = json.load(file)
            venue = data['info']['venue']
            venues.add(venue)
    return venues

def wicket_kind():
    wickets = set()
    for filename in json_files:
        with open(f'./match_data/{filename}') as file:
            data = json.load(file)
            for inning in data['innings']:
                for overs in inning['overs']:
                    for delivery in overs['deliveries']:
                        if 'wickets' in delivery:
                            wickets.add(delivery['wickets'][0]['kind'])
    return wickets

VENUE_MAP = {
    'Green Park': 'Green Park Stadium, Kanpur',
    'Shaheed Veer Narayan Singh International Stadium': 'Shaheed Veer Narayan Singh International Cricket Stadium, Raipur',
    'Barabati Stadium': 'Barabati Stadium, Cuttack',
    'Maharashtra Cricket Association Stadium': 'Maharashtra Cricket Association Stadium, Pune',
    'JSCA International Stadium Complex': 'JSCA International Stadium Complex, Ranchi',
    'Subrata Roy Sahara Stadium': 'Maharashtra Cricket Association Stadium, Pune',
    'Rajiv Gandhi International Stadium': 'Rajiv Gandhi International Cricket Stadium, Hyderabad',
    'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Cricket Stadium, Hyderabad',
    'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Cricket Stadium, Hyderabad',
    'Feroz Shah Kotla': 'Arun Jaitley Stadium, Delhi',
    'Himachal Pradesh Cricket Association Stadium': 'Himachal Pradesh Cricket Association Stadium, Dharamsala',
    'M Chinnaswamy Stadium': 'M. Chinnaswamy Stadium, Bengaluru',
    "St George's Park": "St George's Park, Port Elizabeth",
    'Eden Gardens': 'Eden Gardens, Kolkata',
    'De Beers Diamond Oval': 'De Beers Diamond Oval, Kimberley',
    'Arun Jaitley Stadium': 'Arun Jaitley Stadium, Delhi',
    'OUTsurance Oval': 'OUTsurance Oval, Bloemfontein',
    'Sawai Mansingh Stadium': 'Sawai Mansingh Stadium, Jaipur',
    'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium, Ahmedabad',
    'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium': 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam',
    'Sharjah Cricket Stadium': 'Sharjah Cricket Stadium, Sharjah',
    'Holkar Cricket Stadium': 'Holkar Cricket Stadium, Indore',
    'Saurashtra Cricket Association Stadium': 'Saurashtra Cricket Association Stadium, Rajkot',
    'SuperSport Park': 'SuperSport Park, Centurion',
    'Wankhede Stadium': 'Wankhede Stadium, Mumbai',
    'MA Chidambaram Stadium': 'M. A. Chidambaram Stadium, Chennai',
    'MA Chidambaram Stadium, Chepauk, Chennai': 'M. A. Chidambaram Stadium, Chennai',
    'Sheikh Zayed Stadium': 'Sheikh Zayed Stadium, Abu Dhabi',
    'MA Chidambaram Stadium, Chepauk': 'M. A. Chidambaram Stadium, Chennai',
    'Dr DY Patil Sports Academy': 'Dr DY Patil Sports Academy, Mumbai',
    'New Wanderers Stadium': 'New Wanderers Stadium, Johannesburg',
    'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'Buffalo Park': 'Buffalo Park, East London',
    'Newlands': 'Newlands, Cape Town',
    'Punjab Cricket Association Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'Kingsmead': 'Kingsmead, Durban',
    'Nehru Stadium': 'Nehru Stadium, Kochi',
    'Brabourne Stadium': 'Brabourne Stadium, Mumbai',
}
        