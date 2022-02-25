import requests

api_ver = '3.14'
server_url = 'https://prod-apnortheast-a.online.tableau.com/api/' + api_ver

### AUTHENTHICATE ###
url = server_url + '/auth/signin'
headers = {
            "Content-Type": "application/json",
            "Accept"      : "application/json"
          }
payload = {
            "credentials": {
                              "personalAccessTokenName"   : "<< PAT Name >>",
                              "personalAccessTokenSecret" : "<< PAT Secret >>",
                              "site": {
                                        "contentUrl": "skctableau"
                                      }
                            }
          }

res = requests.post(url, headers=headers, json = payload)
res = res.json()
token = res['credentials']['token']
site_id = res['credentials']['site']['id']

### GET IMAGE FROM VIEW ID ###
url = server_url +  '/sites/' + site_id + '/views/' + '<< View Id >>' + '/image' + '?maxAge=5'+'&resolution=high'
headers = {
            "Content-Type"  : "application/json",
            "Accept"        : "application/json",
            "X-Tableau-Auth": token
          }
res = requests.get(url, headers=headers, json = {})
Headers = {
  'Authorization':'Bearer << Line Notify Token >>'
}
Message = {
  'message':'สวัสดีครับ'
}
files = {'imageFile':res.content}

response = requests.post('https://notify-api.line.me/api/notify',
                         data=Message,
                         headers=Headers,
                         files=files)

print("Status code: ", response.status_code)