from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import os, subprocess, sys, secret, boto3, logging, secrets, webbrowser
from tkinter import *
from tkinter import messagebox
from datetime import date
from botocore.exceptions import ClientError

class ParseReceipt:

    def __init__(self, imageFile):
        self.info = {'TransactionDate' : '', 'MerchantName' : '', 'Total' : '', 'Property': '', 'ExpenseType': '', 'ImageFile' : imageFile, 'ConfidenceLow' : []}
        self.imageFile = imageFile
        FORMRECOGNIZER_ENDPOINT = secret.getEndpoint()
        FORMRECOGNIZER_KEY = secret.getKey()
        self.client = FormRecognizerClient(FORMRECOGNIZER_ENDPOINT, AzureKeyCredential(FORMRECOGNIZER_KEY))

    def parse(self):
        if os.path.isfile(self.imageFile):
            with open(self.imageFile, 'rb') as f:
                data = f.read()
            # Send request to Form Recognizer service to process data
            print('scannning. please wait')
            task = self.client.begin_recognize_receipts(data)    
            analyzed_result = task.result()
            for receipt in analyzed_result:
                for name, field in receipt.fields.items():
                    if name in ["MerchantName", "Total", "TransactionDate"]:
                        self.info[name] = str(field.value)
                        if field.confidence < 0.9:
                            self.info['ConfidenceLow'].append(name)
            return self.info

class RootWindow:

    def __init__(self, window):
        self.window = window
        self.window.withdraw()

        new_window = Toplevel(root)
        screen_width = new_window.winfo_screenwidth()
        screen_height = new_window.winfo_screenheight()
        window_height = 300
        window_width = 720
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        new_window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        new_window.title('Select an Option')
        bumperRow = Frame(new_window)
        bumpterLabel = Label(bumperRow,text="", width=20,font=("bold",15))
        bumperRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        bumpterLabel.pack()

        headerRow = Frame(new_window)
        headerLabel = Label(headerRow,text="Select an Option", width=20,font=("bold",30))
        headerRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        headerLabel.pack()

        def scan():
            new_window.destroy()
            allinfo = []
            # allinfo = [{'TransactionDate': '2022-12-07', 'MerchantName': 'SHERWIN-WILLIAMS.', 'Total': '434.88', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.17PM.png', 'ConfidenceLow': []}, {'TransactionDate': '2022-12-23', 'MerchantName': '', 'Total': '52.35', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.40PM.png', 'ConfidenceLow': []}, {'TransactionDate': '2023-01-02', 'MerchantName': 'COSTCO WHOLESALE', 'Total': '47.6', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.17.59PM.png', 'ConfidenceLow': []}, {'TransactionDate': '2022-12-05', 'MerchantName': '', 'Total': '', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.46PM.png', 'ConfidenceLow': []}, {'TransactionDate': '2022-12-27', 'MerchantName': 'MENARDS', 'Total': '253.95', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.04PM.png', 'ConfidenceLow': []}, {'TransactionDate': '2023-01-07', 'MerchantName': 'THE How doers HOMI DEPOT', 'Total': '57.95', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.12PM.png', 'ConfidenceLow': ['MerchantName']}, {'TransactionDate': '2023-01-02', 'MerchantName': 'COSTCO WHOLESALE', 'Total': '23.19', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.28PM.png', 'ConfidenceLow': []}, {'TransactionDate': '2023-01-03', 'MerchantName': 'MENARDS', 'Total': '31.91', 'Property': '', 'ExpenseType': '', 'ImageFile': 'images/ScreenShot2023-01-08at8.18.24PM.png', 'ConfidenceLow': ['MerchantName']}]
            for filename in os.listdir('images'):
                if filename != '.DS_Store':
                    IMAGE_FILE = os.path.join('images', filename)
                    NEW_IMAGE_FILE = IMAGE_FILE.replace(' ', '')
                    os.rename(IMAGE_FILE, NEW_IMAGE_FILE)
                    transaction = ParseReceipt(NEW_IMAGE_FILE)
                    info = transaction.parse()
                    if info:
                        allinfo.append(info)
            print('scan finished')
            # print(allinfo)
            for i in allinfo:
                self.create(i)
            self.window.destroy()

        def download():
            new_window.destroy()
            download_window = Toplevel(root)

            screen_width = download_window.winfo_screenwidth()
            screen_height = download_window.winfo_screenheight()
            window_height = 300
            window_width = 720
            x_cordinate = int((screen_width/2) - (window_width/2))
            y_cordinate = int((screen_height/2) - (window_height/2))
            download_window.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

            bumperRow = Frame(download_window)
            bumpterLabel = Label(bumperRow,text="", width=20,font=("bold",15))
            bumperRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
            bumpterLabel.pack()

            download_window.title('Download Reciept')
            headerRow = Frame(download_window)
            headerLabel = Label(headerRow,text="Download Reciept", width=20,font=("bold",30))
            headerRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
            headerLabel.pack()

            bumperRow = Frame(download_window)
            bumpterLabel = Label(bumperRow,text="", width=20,font=("bold",20))
            bumperRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
            bumpterLabel.pack()

            inputRow = Frame(download_window)
            inputLabel = Label(inputRow,text="Key", width=20,font=("bold",20))
            input = Entry(inputRow)
            inputRow.pack(side = TOP, fill = X, padx = 20, pady = 20)
            inputLabel.pack(side = LEFT)
            input.pack(side = RIGHT, expand = YES, fill = X)

            bumperRow = Frame(download_window)
            bumpterLabel = Label(bumperRow,text="", width=10,font=("bold",10))
            bumperRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
            bumpterLabel.pack()

            def downloadSubmit(event=None):
                s3 = boto3.client("s3", region_name=secret.getRegionName(), aws_access_key_id=secret.getAccessKey(), aws_secret_access_key=secret.getSecretKey(), endpoint_url='https://s3.' + secret.getRegionName() + '.amazonaws.com')
                url = s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': secret.getBucket(), 'Key': input.get(),},
                    ExpiresIn=60,
                )

                webbrowser.open_new(url)
                # comment the 2 lines below if you want to continuously download receipts
                download_window.destroy()
                self.window.destroy()

            submitRow = Frame(download_window)
            download_window.bind('<Return>', downloadSubmit)
            b1 = Button(submitRow, text='Submit', width=20, height=2, command=downloadSubmit, font=("bold",15))
            submitRow.pack(side = TOP, fill = X, padx = 5, pady = 5)
            b1.pack()

        button1=Button(new_window,text='Scan Reciepts',width=20,height=5,font=("bold",20), command=scan)
        button1.pack(side='left', anchor='e', expand=True)
        button2=Button(new_window,text='Download Reciept',width=20,height=5,font=("bold",20), command=download)
        button2.pack(side='right', anchor='w', expand=True)
    

    def create(self, info):
        new_window = Toplevel(self.window)
        entry_window = PopupWindow(new_window, info)
        subprocess.Popen(["open", info['ImageFile']])
        entry_window.b1.wait_variable(entry_window.bvar)

class PopupWindow():
    def __init__(self, window, info):
        self.info = info
        self.window = window
        self.window.geometry("-0+0")
        self.window.title('Receipt Information')
        self.expenseTypes = ['Repair', 'Maintenance', 'Other']
        receiptInformationRow = Frame(self.window)
        receiptInformationLabel = Label(receiptInformationRow,text="Receipt Information", width=40,font=("bold",25))
        receiptInformationRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        receiptInformationLabel.pack()

        transactionDateRow = Frame(self.window)
        if 'TransactionDate' in self.info['ConfidenceLow'] or not self.info['TransactionDate']:
            transactionDateLabel = Label(transactionDateRow,text="Transaction Date", width=20,fg='#f00',font=("bold",15))
        else:
            transactionDateLabel = Label(transactionDateRow,text="Transaction Date", width=20,font=("bold",15))
        self.transactionDate = Entry(transactionDateRow)
        if not self.info['TransactionDate']:
            self.transactionDate.insert(0, 'YEAR-MONTH-DATE')
        else:
            self.transactionDate.insert(0, self.info['TransactionDate'])
        transactionDateRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        transactionDateLabel.pack(side = LEFT)
        self.transactionDate.pack(side = RIGHT, expand = YES, fill = X)

        merchantNameRow = Frame(self.window)
        self.stores = ['Home Depot', 'Menards', 'Walmart', 'Other']
        if 'MerchantName' in self.info['ConfidenceLow'] or not self.info['MerchantName']:
            merchantNameLabel = Label(merchantNameRow,text="Merchant Name", width=20,fg='#f00',font=("bold",15))
        else:
            merchantNameLabel = Label(merchantNameRow,text="Merchant Name",width=20,font=("bold",15))
        if self.info['MerchantName'] and self.info['MerchantName'].lower() not in self.stores:
            self.stores.append(self.info['MerchantName'])
        self.merchantName = StringVar()
        self.merchantName.set(self.info['MerchantName'])
        self.otherMerchant = StringVar()

        def chooseOtherMerchant(e=None):
            if self.merchantName.get() == 'Other':
                merchantNameLabel.destroy()
                self.otherMerchant = Entry(merchantNameRow)
                otherMerchantLabel = Label(merchantNameRow,text="Other Merchant", width=20,font=("bold",15))
                otherMerchantLabel.pack(side = LEFT)
                self.otherMerchant.pack(side = RIGHT, expand = YES, fill = X)

        merchantDroplist = OptionMenu(merchantNameRow, self.merchantName, *self.stores, command=chooseOtherMerchant)
        merchantDroplist.config(width=15)
        merchantNameRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        merchantNameLabel.pack(side = LEFT)
        merchantDroplist.pack(side = RIGHT, expand = YES, fill = X)

        totalRow = Frame(self.window)
        if 'Total' in self.info['ConfidenceLow'] or not self.info['Total']:
            totalLabel = Label(totalRow,text="Total", width=20,fg='#f00',font=("bold",15))
        else:
            totalLabel = Label(totalRow,text="Total", width=20,font=("bold",15))
        self.total = Entry(totalRow)
        self.total.insert(0, self.info['Total'])
        totalRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        totalLabel.pack(side = LEFT)
        self.total.pack(side = RIGHT, expand = YES, fill = X)

        expenseTypeRow = Frame(self.window)
        expenseTypeLabel = Label(expenseTypeRow,text="Expense Type", width=20,font=("bold",15))
        self.expenseType = StringVar()
        self.expenseType.set('Select')
        self.other = StringVar()

        def chooseOtherExpense(e=None):
            if self.expenseType.get() == 'Other':
                expenseTypeLabel.destroy()
                self.other = Entry(expenseTypeRow)
                otherLabel = Label(expenseTypeRow,text="Other Expense", width=20,font=("bold",15))
                otherLabel.pack(side = LEFT)
                self.other.pack(side = RIGHT, expand = YES, fill = X)

        expenseDroplist = OptionMenu(expenseTypeRow, self.expenseType, *self.expenseTypes, command=chooseOtherExpense)
        expenseDroplist.config(width=15)
        expenseTypeRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        expenseTypeLabel.pack(side = LEFT)
        expenseDroplist.pack(side = RIGHT, expand = YES, fill = X)

        propertyRow = Frame(self.window)
        propertyLabel = Label(propertyRow,text="Property",width=20,font=("bold",15))
        properties = ['p1', 'p2']
        self.property = StringVar()
        droplist = OptionMenu(propertyRow, self.property, *properties)
        droplist.config(width=15)
        self.property.set('Select')
        propertyRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        propertyLabel.pack(side = LEFT)
        droplist.pack(side = RIGHT, expand = YES, fill = X)

        submitRow = Frame(self.window)
        self.bvar = IntVar()
        self.b1 = Button(submitRow, text='Submit', width=20, command=self.clicked)
        submitRow.pack(side = TOP, fill = X, padx = 5, pady = 5)
        self.b1.pack()

    def clicked(self):
        self.info['TransactionDate'] = self.transactionDate.get()
        self.info['MerchantName'] = self.merchantName.get() if self.otherMerchant.get() == '' else self.otherMerchant.get()
        if 'home' in self.info['MerchantName'].lower() and self.info['MerchantName'] not in self.stores:
            self.info['MerchantName'] = 'Home Depot'
        self.info['Total'] = self.total.get()
        self.info['ExpenseType'] = self.expenseType.get() if self.other.get() == '' else self.other.get()
        self.info['Property'] = self.property.get()
        errors = []
        for entry in self.info:
            if self.info[entry] in ['', 'Select', '0', 'YEAR-MONTH-DATE']:
                errors.append(entry)
        if errors:
            s = errors[0]
            if len(errors) > 1:
                s = ", ".join(errors[:-1]) + ', ' + errors[-1]
            mes = s + ' is empty'
            messagebox.showerror('Error', mes)
        else:
            subprocess.Popen(["pkill", "-x", "Preview" ])
            print(self.info)
            self.bookkeeping()
            self.bvar.set(1)
            self.window.withdraw()

    def bookkeeping(self):
        file = './properties/' + self.info['Property'] + '.csv'
        src_folder = r"./images/"
        file_name = self.info['ImageFile'].split('/')[-1]
        key_len = 13
        encrypted_key = secrets.token_urlsafe(key_len) + file_name
        today = str(date.today())
        s3 = boto3.client("s3", region_name=secret.getRegionName(), aws_access_key_id=secret.getAccessKey(), aws_secret_access_key=secret.getSecretKey(), endpoint_url='https://s3.' + secret.getRegionName() + '.amazonaws.com')
        bucket = secret.getBucket()
        key = today + '/' + encrypted_key

        # uploading files
        try:
            s3.upload_file (
                Filename = src_folder + file_name,
                Bucket = bucket,
                Key = key,
            )   
        except ClientError as e:
            logging.error(e)
            print('error uploading file')
            return False
        
        # checking file is uploaded correctly
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except ClientError as e:
            print('error uploading file')
            return int(e.response['Error']['Code']) != 404
        print('upload successful')

        # deleting image
        # os.remove(src_folder + file_name)

        # writing to file
        with open(file, 'a') as f:
            s = self.info['TransactionDate'] + ',' + self.info['MerchantName'] + ',' + self.info['Total'] + ',' + self.info['ExpenseType'] + ',' + bucket + ',' + key + '\n'
            f.write(s)

        return True

if __name__ == "__main__":
    root = Tk()
    window = RootWindow(root)
    root.mainloop()
 