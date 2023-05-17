with open("account.txt", 'r') as file:
    data = file.readline()
    username = data.split(':')[0]
    password = data.split(':')[1]
    print(username, password)
