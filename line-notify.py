import requests

Headers = {
  'Authorization':'Bearer << Line Notify Token >>'
}
Message = {
  'message':'สวัสดีครับ'
}
file = open('img_lineup_04.jpg', 'rb')
files = {'imageFile':file}

response = requests.post('https://notify-api.line.me/api/notify',
                         data=Message,
                         headers=Headers,
                         files=files)

print("Status code: ", response.status_code)