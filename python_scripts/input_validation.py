import datetime

vars = ['12/31/1993', '12/01/2022', '12/10/2022']
result = 'pass'
for var in vars:
    print("Validating date format of ", var)
    try:
        date = datetime.datetime.strptime(var, "%m/%d/%Y")
        print(date)
        print('pass')
    except ValueError:
        print('failed')