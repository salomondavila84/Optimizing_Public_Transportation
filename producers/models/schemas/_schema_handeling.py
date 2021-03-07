import requests

r = requests.get('http://127.0.0.1:8081/subjects/')

subjects = r.text

subjects_list = subjects.strip("][\"").split('","')

for subject in subjects_list:
    print(subject)

    #soft_delete = requests.delete('http://127.0.0.1:8081/subjects/{}'.format(str(subject)))
    #print(soft_delete.text)
    #hard_delete = requests.delete('http://127.0.0.1:8081/subjects/{}?permanent = true'.format(subject))

    schema = requests.get('http://127.0.0.1:8081/subjects/{}/versions/latest'.format(subject))
    print(schema.text)