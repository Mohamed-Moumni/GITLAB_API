import requests

url = "https://gitlab.com/api/v4/projects/53631656/jobs/5918122925/trace"
headers = {'PRIVATE-TOKEN': 'glpat-2Jdi539E3QAHEqCWtU7_'}
response = requests.get(url, headers=headers)
print(response.text[response.text.find("Your code has been rated at"):])