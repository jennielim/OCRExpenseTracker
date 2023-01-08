from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import os, subprocess, sys, shutil, secret, boto3, logging, secrets
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

            # opening image to user
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            p = subprocess.call([opener, f.name])

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
        for filename in os.listdir('images'):
            if filename != '.DS_Store':
                IMAGE_FILE = os.path.join('images', filename)
                transaction = ParseReceipt(IMAGE_FILE)
                info = transaction.parse()
                if info:
                    self.create(info)
        self.window.destroy()

    def create(self, info):
        new_window = Toplevel(self.window)
        entry_window = PopupWindow(new_window, info)
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
        if 'MerchantName' in self.info['ConfidenceLow'] or not self.info['MerchantName']:
            merchantNameLabel = Label(merchantNameRow,text="Merchant Name", width=20,fg='#f00',font=("bold",15))
        else:
            merchantNameLabel = Label(merchantNameRow,text="Merchant Name",width=20,font=("bold",15))
        stores = ['Home Depot', 'Menards', 'Walmart', 'Other']
        self.merchantName = StringVar()
        self.merchantName.set(self.info['MerchantName'])
        droplist = OptionMenu(merchantNameRow, self.merchantName, *stores)
        droplist.config(width=15)
        merchantNameRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        merchantNameLabel.pack(side = LEFT)
        droplist.pack(side = RIGHT, expand = YES, fill = X)

        otherMerchantRow = Frame(self.window)
        otherMerchantLabel = Label(otherMerchantRow,text="Other Merchant", width=20,font=("bold",15))
        self.otherMerchant = Entry(otherMerchantRow)
        otherMerchantRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        otherMerchantLabel.pack(side = LEFT)
        self.otherMerchant.pack(side = RIGHT, expand = YES, fill = X)

        totalRow = Frame(self.window)
        if 'Total' in self.info['ConfidenceLow'] or not self.info['Total']:
            totalLabel = Label(transactionDateRow,text="Total", width=20,fg='#f00',font=("bold",15))
        else:
            totalLabel = Label(totalRow,text="Total", width=20,font=("bold",15))
        self.total = Entry(totalRow)
        self.total.insert(0, self.info['Total'])
        totalRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        totalLabel.pack(side = LEFT)
        self.total.pack(side = RIGHT, expand = YES, fill = X)

        expenseTypeRow = Frame(self.window)
        expenseTypeLabel = Label(expenseTypeRow,text="Expense Type", width=20,font=("bold",15))
        self.expenseType = IntVar()
        radioButtons = []
        for i in range(len(self.expenseTypes)):
            radioButtons.append(Radiobutton(self.window,text=self.expenseTypes[i], variable = self.expenseType, value=i + 1))
        expenseTypeLabel.pack(side = LEFT)
        for i in radioButtons:
            i.pack(in_=expenseTypeRow, side="left")
        expenseTypeRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)

        otherLabelRow = Frame(self.window)
        otherLabel = Label(otherLabelRow,text="Other Expense Type", width=20,font=("bold",15))
        self.other = Entry(otherLabelRow)
        otherLabelRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        otherLabel.pack(side = LEFT)
        self.other.pack(side = RIGHT, expand = YES, fill = X)

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
        self.info['Total'] = self.total.get()
        self.info['ExpenseType'] = self.expenseTypes[self.expenseType.get() - 1] if self.other.get() == '' and self.expenseType.get() > 0 else self.other.get()
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
        os.remove(src_folder + file_name)

        # writing to file
        with open(file, 'a') as f:
            s = self.info['TransactionDate'] + ',' + self.info['MerchantName'] + ',' + self.info['Total'] + ',' + self.info['ExpenseType'] + ',' + bucket + ',' + key + '\n'
            f.write(s)

        return True

if __name__ == "__main__":
    root = Tk()
    window = RootWindow(root)
    root.mainloop()
 