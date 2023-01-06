from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import os, subprocess, sys, shutil
from datetime import date

FORMRECOGNIZER_ENDPOINT = "https://lgaptrent-expenses.cognitiveservices.azure.com/"
FORMRECOGNIZER_KEY = "843b91bdc6c847da8d313487e1829130"
# Initiate client with given endpoint and credential
client = FormRecognizerClient(FORMRECOGNIZER_ENDPOINT, AzureKeyCredential(FORMRECOGNIZER_KEY))

# loop through all receipts in image folder
directory = 'images'
properties = ['p1', 'p2']
expenseTypes = ['repair', 'maintenance', 'other']
 
for filename in os.listdir(directory):
    if filename != '.DS_Store':
        check = []
        IMAGE_FILE = os.path.join(directory, filename)
        if os.path.isfile(IMAGE_FILE):
            info = {'TransactionDate' : '', 'MerchantName' : '', 'Total' : '', 'Property': '', 'ExpenseType': ''}
            with open(IMAGE_FILE, 'rb') as f:
                data = f.read()

            # opening image to user
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            p = subprocess.call([opener, f.name])

            # Send request to Form Recognizer service to process data
            print('scannning. please wait')
            task = client.begin_recognize_receipts(data)    
            analyzed_result = task.result()
            for receipt in analyzed_result:
                for name, field in receipt.fields.items():
                    if name in ["MerchantName", "Total", "TransactionDate"]:
                        # updating info
                        info[name] = str(field.value)
                        # print("{}: {} has confidence {}".format(name, field.value, field.confidence))
                        if field.confidence < .9:
                            check.append(name)

            # correcting mistakes
            if info['MerchantName'] == '':
                print()
                print('merchant name not caught, please enter: ')
                name = input()
                info['MerchantName'] = name
            if info['Total'] == '':
                print()
                print('total not caught, please enter: ')
                total = input()
                info['Total'] = total
            if info['TransactionDate'] == '':
                print()
                print('transaction date not caught, please enter like 2022-12-27,: ')
                date = input()
                info['TransactionDate'] = date

            # let user select a property
            print()
            print('please select a property: ')
            for i in range(len(properties)):
                num = str(i + 1) + '.'
                print(num, properties[i])
            property = int(input())
            info['Property'] = properties[property - 1]
            print()

            # let user select expense
            print('please select an expense type: ')
            for i in range(len(expenseTypes)):
                print(i + 1, expenseTypes[i])
            expense = int(input())
            if expense == 3:
                expense = input('please specify expense: ')
                info['ExpenseType'] = expense
            else:
                info['ExpenseType'] = expenseTypes[expense - 1]
            print()

            print("Here is the retieved data:")
            for n in info:
                print(n + ':', info[n])
            print()
            if check:
                print("warning - please double check the following")
                for i in check:
                    print(i)

            print()
            print("please press any of the following letters to edit information, otherwise press enter: ")
            print('d for date')
            print('n for name')
            print('t for total')
            print('p for property')
            print('e for expense type')
            print()
            review = 'not yet'
            while review != '':
                if review != 'not yet':
                    review = input("please press any of the following letters to edit information, otherwise press enter: ")
                else:
                    review = input()
                if review == '':
                    print('writing to file')
                elif review == 'd':
                    info['TransactionDate'] = input('please update date: ')
                elif review == 'n':
                    info['MerchantName'] = input('please update name. if home depot press enter: ')
                    if info['MerchantName'] == '':
                        info['MerchantName'] = 'Home Depot'
                elif review == 't':
                    info['Total'] = input('please update total: ')
                elif review == 'p':
                    num = int(input('please update property: '))
                    info['Property'] = properties[num - 1]
                elif review == 'e':
                    num = int(input('please update expense type: '))
                    if num == 3:
                        num = input('please specify expense: ')
                        info['ExpenseType'] = num
                    else:
                        info['ExpenseType'] = expenseTypes[num - 1]
                if review != '':
                    print()
                    print('updated info')
                    for n in info:
                        print(n + ':', info[n])
                    print()
            print('-----------------------------------------')

            # updating books
            file = './properties/' + info['Property'] + '.csv'
            with open(file, 'a') as f:
                s = info['TransactionDate'] + ',' + info['MerchantName'] + ',' + info['Total'] + ',' + info['ExpenseType'] + '\n'
                f.write(s)

            # moving image
            today = str(date.today())
            src_folder = r"./images/"
            dst_folder = r"./prev/"
            file_name = IMAGE_FILE.split('/')[-1]

            # checks if folder exists
            if not os.path.exists(dst_folder + today):
                os.mkdir(dst_folder + today)

            # check if file exist in destination
            if not os.path.exists(dst_folder + today + '/' + file_name):
                shutil.move(src_folder + file_name, dst_folder + today + '/' + file_name)

