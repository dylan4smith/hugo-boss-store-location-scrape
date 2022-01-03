import requests
import pandas as pd

# lists of data to extract
country = []
longitude = []
latitude = []
c_type = []
timezone = []
address = []
city = []
postal = []
state = []
phone = []
email = []

# convert curl to python headers and parameters
# https://curlconverter.com/

headers = {
    'authority': 'production-na01-hugoboss.demandware.net',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://www.hugoboss.com',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.hugoboss.com/',
    'accept-language': 'en-US,en;q=0.9',
}

params = (
    ('client_id', '871c988f-3549-4d76-b200-8e33df5b45ba'),
    # lat and long must be between -90 and 90
    ('latitude', '-90'),
    ('longitude', '-90'),
    # how many stores to request up to 200 at a time
    ('count', '200'),
    # start at the first store
    ('start', '0'),
)

# get from network passing in required headers and parameters
response = requests.get('https://production-na01-hugoboss.demandware.net/s/US/dw/shop/v20_10/stores', headers=headers, params=params)

# using recursion scrape all store data with parameters: (get request, number of stores to scrape at a time up to 200)
def scrape(response, count):
    # for each store scraped, append data to corresponding list
    for store in range(count):
        # check to see if the store is in the US
        if response.json()['data'][store]['country_code'] == 'US':
            # data present for every store
            country.append(response.json()['data'][store]['country_code'])
            timezone.append(response.json()['data'][store]['c_timezone'])
            longitude.append(response.json()['data'][store]['longitude'])
            latitude.append(response.json()['data'][store]['latitude'])
            c_type.append(response.json()['data'][store]['c_type'])
            address.append(response.json()['data'][store]['address1'])
            city.append(response.json()['data'][store]['city'])
            postal.append(response.json()['data'][store]['postal_code'])
            state.append(response.json()['data'][store]['state_code'])

            # store data below is optional and not present for some stores
            # try to get data, if no data present, input NA
            try:
                phone.append(response.json()['data'][store]['phone'])
            except:
                phone.append('NA')

            try:
                email.append(response.json()['data'][store]['c_contactEmail'])
            except:
                email.append('NA')

    # if there are more than 200 stores left to scrape
    if response.json()['total'] - (response.json()['start'] + response.json()['count']) >= response.json()['count']:
        # scrape the next 200 stores
        return scrape(requests.get(response.json()['next']), count)

    # if there are less than 200 stores left to scrape
    elif response.json()['total'] - (response.json()['start'] + response.json()['count']) < response.json()['count'] and response.json()['total'] - (response.json()['start'] + response.json()['count']) > 0:
        # change the count parameter in the next get request from 200 to the rest of the stores
        new_next = response.json()['next'].replace('count=200', 'count=' + str(response.json()['total'] - (response.json()['start'] + response.json()['count'])))
        # scrape the remaining of the stores by using the new count parameters
        return scrape(requests.get(new_next), response.json()['total'] - (response.json()['start'] + response.json()['count']))

    # add each list to a dictionary for pandas
    output = {
        'type': c_type,
        'country': country,
        'state': state,
        'city': city,
        'address': address,
        'postal': postal,
        'phone': phone,
        'email': email,
        'timezone': timezone,
        'longitude': longitude,
        'latitude': latitude
    }

    #return the dictionary of of lists with all store data
    return output

# create pandas data frame using the output dictionary from scrape method
df1 = pd.DataFrame(scrape(response, 200))
# create writer for the following file
writer = pd.ExcelWriter('HugoBossStores.xlsx')
# write to sheet named store_data in above file
df1.to_excel(writer, sheet_name='store_data')
# save file
writer.save()