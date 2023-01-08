from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import os, subprocess, sys, shutil
from tkinter import *
from tkinter import messagebox
from datetime import date

FORMRECOGNIZER_ENDPOINT = "https://lgaptrent-expenses.cognitiveservices.azure.com/"
FORMRECOGNIZER_KEY = "843b91bdc6c847da8d313487e1829130"
client = FormRecognizerClient(FORMRECOGNIZER_ENDPOINT, AzureKeyCredential(FORMRECOGNIZER_KEY))

directory = 'images'
properties = ['p1', 'p2']
expenseTypes = ['repair', 'maintenance', 'other']

class ParseReceipt:

    def __init__(self, imageFile):
        self.info = {'TransactionDate' : '', 'MerchantName' : '', 'Total' : '', 'Property': '', 'ExpenseType': '', 'ImageFile' : imageFile, 'ConfidenceLow' : []}
        self.imageFile = imageFile

    def parse(self):
        if os.path.isfile(self.imageFile):
            with open(self.imageFile, 'rb') as f:
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
                        self.info[name] = str(field.value)
                        if field.confidence < 0.9:
                            self.info['ConfidenceLow'].append(name)
            return self.info

class RootWindow:

    def __init__(self, window):
        self.window = window
        self.window.withdraw()
        for filename in os.listdir(directory):
            if filename != '.DS_Store':
                IMAGE_FILE = os.path.join(directory, filename)
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
        r1 = Radiobutton(self.window,text="Repair", variable = self.expenseType, value=1)
        r2 = Radiobutton(self.window,text="Maintenance", variable = self.expenseType, value=2)
        r3 = Radiobutton(self.window,text="Other", variable = self.expenseType, value=3)
        expenseTypeLabel.pack(side = LEFT)
        r1.pack(in_=expenseTypeRow, side="left")
        r2.pack(in_=expenseTypeRow, side="left")
        r3.pack(in_=expenseTypeRow, side="left")
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
        self.info['ExpenseType'] = expenseTypes[self.expenseType.get() - 1] if self.other.get() == '' and self.expenseType.get() > 0 else self.other.get()
        self.info['Property'] = self.property.get()
        errors = []
        for entry in self.info:
            if self.info[entry] in ['', 'Select', '0']:
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
        with open(file, 'a') as f:
            s = self.info['TransactionDate'] + ',' + self.info['MerchantName'] + ',' + self.info['Total'] + ',' + self.info['ExpenseType'] + '\n'
            f.write(s)

        # moving image
        today = str(date.today())
        src_folder = r"./images/"
        dst_folder = r"./prev/"
        file_name = self.info['ImageFile'].split('/')[-1]

        # checks if folder exists
        if not os.path.exists(dst_folder + today):
            os.mkdir(dst_folder + today)

        # check if file exist in destination
        if not os.path.exists(dst_folder + today + '/' + file_name):
            shutil.move(src_folder + file_name, dst_folder + today + '/' + file_name)  

root = Tk()
window = RootWindow(root)
root.mainloop()
 