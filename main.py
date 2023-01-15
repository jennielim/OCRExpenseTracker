from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import FormRecognizerClient
import os, subprocess, secret, boto3, logging, secrets, webbrowser
from tkinter import *
from tkinter import messagebox
from botocore.exceptions import ClientError

class ParseReceipt:

    def __init__(self, imageFile):
        self.info = {'TransactionDate' : '', 'MerchantName' : '', 'Total' : '', 'Property': '', 'ExpenseType': '', 'Items': [], 'Payment Method' : '', 'ImageFile' : imageFile, 'ConfidenceLow' : []}
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
                    if name == "Items":
                        i = []
                        for idx, items in enumerate(field.value):
                            for item_name, item in items.value.items():
                                iv = item.value
                                niv = iv.replace(',', '')
                                i.append(niv)
                                break
                        self.info[name] = i
                        if field.confidence < 0.9:
                            self.info['ConfidenceLow'].append(name)
                    elif name in ["MerchantName", "Total", "TransactionDate"]:
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
            allinfo = [{'TransactionDate': '2022-12-28', 'MerchantName': 'MENARDS', 'Total': '682.76', 'Property': '', 'ExpenseType': '', 'Items': ["1X2-8' #2 QUALITY BOARD", 'BRITE WH 6PNL 30LH', '1/2 × 2×4 OSB NOM.', 'CRFT CASE WM473 BWHTWD', 'RNCH BASE LWM724 GLDOAK', 'BRITE WH 6PNL 30RH', '6\'9" METAL 1-1/4\'', '"BEDDAR WOOD SHIMS -12P', 'SC PRIVACY TULIP KNOB', 'EZ HANG DOOR HANGER'], 'Payment Method': '', 'ImageFile': 'images/menards.jpg', 'ConfidenceLow': ['MerchantName']}, {'TransactionDate': '2019-06-10', 'MerchantName': 'Contoso', 'Total': '1203.39', 'Property': '', 'ExpenseType': '', 'Items': ['Surface Pro 6', 'SurfacePen'], 'Payment Method': '', 'ImageFile': 'images/sample-receipt.png', 'ConfidenceLow': []}]
            # allinfo = []
            # for filename in os.listdir('images'):
            #     if filename != '.DS_Store':
            #         IMAGE_FILE = os.path.join('images', filename)
            #         NEW_IMAGE_FILE = IMAGE_FILE.replace(' ', '')
            #         os.rename(IMAGE_FILE, NEW_IMAGE_FILE)
            #         transaction = ParseReceipt(NEW_IMAGE_FILE)
            #         info = transaction.parse()
            #         if info:
            #             allinfo.append(info)
            # print(allinfo)
            print('scan finished')
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
                # download_window.destroy()
                # self.window.destroy()

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
        self.expenseTypes = secret.getExpenseTypes()
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
        self.merchantNameLabel = None
        self.stores = secret.getStores()
        if 'MerchantName' in self.info['ConfidenceLow'] or not self.info['MerchantName']:
            self.merchantNameLabel = Label(merchantNameRow,text="Merchant Name", width=20,fg='#f00',font=("bold",15))
        else:
            self.merchantNameLabel = Label(merchantNameRow,text="Merchant Name",width=20,font=("bold",15))
        if self.info['MerchantName'] and self.info['MerchantName'].lower() not in self.stores:
            self.stores.append(self.info['MerchantName'])
        self.otherMerchantLabel = None
        self.merchantName = StringVar()
        self.merchantName.set(self.info['MerchantName'])
        self.otherMerchant = StringVar()
        self.otherMerchantOpen = False

        def chooseOtherMerchant(e=None):
            if self.merchantName.get() == 'Other' and not self.otherMerchantOpen:
                self.merchantNameLabel.destroy()
                self.otherMerchant = Entry(merchantNameRow)
                self.otherMerchantLabel = Label(merchantNameRow,text="Other Merchant", width=20,font=("bold",15))
                self.otherMerchantLabel.pack(side = LEFT)
                self.otherMerchant.pack(side = RIGHT, expand = YES, fill = X)
                self.otherMerchantOpen = True
            elif self.merchantName.get() != 'Other' and self.otherMerchantOpen:
                self.otherMerchant.destroy()
                self.otherMerchant = StringVar()
                self.otherMerchantLabel.destroy()
                self.merchantNameLabel = Label(merchantNameRow,text="Other Merchant", width=20,font=("bold",15))
                self.merchantNameLabel.pack(side = LEFT)
                self.otherMerchantOpen = False


        merchantEntry = Entry(merchantNameRow)
        merchantEntry['textvariable'] = self.merchantName

        merchantDroplist = OptionMenu(merchantNameRow, self.merchantName, *self.stores, command=chooseOtherMerchant)
        merchantDroplist.config(width=15)
        merchantNameRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        self.merchantNameLabel.pack(side = LEFT)
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
        self.expenseTypeLabel = Label(expenseTypeRow,text="Expense Type", width=20,font=("bold",15))
        self.expenseType = StringVar()
        self.expenseType.set('Select')
        self.otherLabel = None
        self.other = StringVar()
        self.otherOpen = False

        def chooseOtherExpense(e=None):
            if self.expenseType.get() == 'Other' and not self.otherOpen:
                self.expenseTypeLabel.destroy()
                self.other = Entry(expenseTypeRow)
                self.otherLabel = Label(expenseTypeRow,text="Other Expense", width=20,font=("bold",15))
                self.otherLabel.pack(side = LEFT)
                self.other.pack(side = RIGHT, expand = YES, fill = X)
                self.otherOpen  = True
            elif self.expenseType.get() != 'Other' and self.otherOpen:
                self.other.destroy()
                self.other = StringVar()
                self.otherLabel.destroy()
                self.expenseTypeLabel = Label(expenseTypeRow,text="Expense Type", width=20,font=("bold",15))
                self.expenseTypeLabel.pack(side = LEFT)
                self.otherOpen  = False

        expenseEntry = Entry(expenseTypeRow)
        expenseEntry['textvariable'] = self.expenseType

        expenseDroplist = OptionMenu(expenseTypeRow, self.expenseType, *self.expenseTypes, command=chooseOtherExpense)
        expenseDroplist.config(width=15)
        expenseTypeRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        self.expenseTypeLabel.pack(side = LEFT)
        expenseDroplist.pack(side = RIGHT, expand = YES, fill = X)

        propertyRow = Frame(self.window)
        properties = secret.getProperties()
        self.propertyLabel = Label(propertyRow,text="Property", width=20,font=("bold",15))
        self.property = StringVar()
        self.property.set('Select')
        self.otherPropLabel = None
        self.otherProp = StringVar()
        self.propOpen = False

        def chooseOtherProperty(e=None):
            if self.property.get() == 'Other' and not self.propOpen:
                self.propertyLabel.destroy()
                self.otherProp = Entry(propertyRow)
                self.otherPropLabel = Label(propertyRow,text="Other Property", width=20,font=("bold",15))
                self.otherPropLabel.pack(side = LEFT)
                self.otherProp.pack(side = RIGHT, expand = YES, fill = X)
                self.propOpen  = True
            elif self.property.get() != 'Other' and self.propOpen:
                self.otherProp.destroy()
                self.otherProp = StringVar()
                self.otherPropLabel.destroy()
                self.propertyLabel = Label(propertyRow,text="Property", width=20,font=("bold",15))
                self.propertyLabel.pack(side = LEFT)
                self.propOpen  = False

        propertyEntry = Entry(propertyRow)
        propertyEntry['textvariable'] = self.property

        propertyList = OptionMenu(propertyRow, self.property, *properties, command=chooseOtherProperty)
        propertyList.config(width=15)
        propertyRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        self.propertyLabel.pack(side = LEFT)
        propertyList.pack(side = RIGHT, expand = YES, fill = X)

        paymentRow = Frame(self.window)
        payments = secret.getPaymentMethods()
        self.paymentLabel = Label(paymentRow,text="Payment Method", width=20,font=("bold",15))
        self.payment = StringVar()
        self.payment.set('Select')
        self.otherPaymentLabel = None
        self.otherPayment = StringVar()
        self.payOpen = False

        def chooseOtherPayment(e=None):
            if self.payment.get() == 'Other' and not self.payOpen:
                self.paymentLabel.destroy()
                self.otherPayment = Entry(paymentRow)
                self.otherPaymentLabel = Label(paymentRow,text="Other Payment Method", width=20,font=("bold",15))
                self.otherPaymentLabel.pack(side = LEFT)
                self.otherPayment.pack(side = RIGHT, expand = YES, fill = X)
                self.payOpen  = True
            elif self.payment.get() == 'Check' and not self.payOpen:
                self.paymentLabel.destroy()
                self.otherPayment = Entry(paymentRow)
                self.otherPaymentLabel = Label(paymentRow,text="Check Number", width=20,font=("bold",15))
                self.otherPaymentLabel.pack(side = LEFT)
                self.otherPayment.pack(side = RIGHT, expand = YES, fill = X)
                self.payOpen  = True
            elif self.payment.get() != 'Other' and self.payment.get() != 'Check' and self.propOpen:
                self.otherPayment.destroy()
                self.otherPayment = StringVar()
                self.otherPaymentLabel.destroy()
                self.paymentLabel = Label(paymentRow,text="Payment Method", width=20,font=("bold",15))
                self.paymentLabel.pack(side = LEFT)
                self.payOpen  = False

        paymentEntry = Entry(paymentRow)
        paymentEntry['textvariable'] = self.payment

        paymentList = OptionMenu(paymentRow, self.payment, *payments, command=chooseOtherPayment)
        paymentList.config(width=15)
        paymentRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        self.paymentLabel.pack(side = LEFT)
        paymentList.pack(side = RIGHT, expand = YES, fill = X)

        itemsRow = Frame(self.window)
        if 'Items' in self.info['ConfidenceLow'] or not self.info['Items']:
            itemsLabel = Label(itemsRow,text="Items", width=20,fg='#f00',font=("bold",15))
        else:
            itemsLabel = Label(itemsRow,text="Items", width=20,font=("bold",15))
        self.items = Entry(itemsRow)
        str_items = ""
        for i in range(len(self.info['Items'])):
            str_items += self.info['Items'][i]
            if i < len(self.info['Items']) - 1:
                str_items += ' | '
        self.items.insert(0, str_items)
        itemsRow.pack(side = TOP, fill = X, padx = 5 , pady = 5)
        itemsLabel.pack(side = LEFT)
        self.items.pack(side = RIGHT, expand = YES, fill = X)

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
        self.info['Property'] = self.property.get() if self.otherProp.get() == '' else self.otherProp.get()
        self.info['Items'] = self.items.get()
        if self.payment.get() == 'Check':
            self.info['Payment Method'] = 'Check ' + self.otherPayment.get()
        else:
            self.info['Payment Method'] = self.payment.get() if self.otherPayment.get() == '' else self.otherPayment.get()
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

    def uploadFileAWS(self, s3, bucket, key, path):
        try:
            s3.upload_file (Filename = path, Bucket = bucket, Key = key)   
        except ClientError as e:
            logging.error(e)
            print('error uploading file')
            return False
        return True

    def deleteFileAWS(self, s3, bucket, key):
        try:
            s3.delete_object(Bucket = bucket, Key = key)
        except ClientError as e:
            logging.error(e)
            print('error deleting file')
            return False
        return True
    
    def fileExistsAWS(self, s3, bucket, key, csv=None):
        try:
            s3.head_object(Bucket=bucket, Key=key)
        except ClientError as e:
            if csv == '.csv':
                print('new folder created')
            else:
                logging.error(e)
                print('file does not exist')
            return False
        print('picture upload successful') if csv == None else print('csv upload successful')
        return True

    def writeToFile(self, file, bucket, key):
        if not os.path.exists(file):
            with open(file, 'a') as f:
                header = "Transation Date,Total,Items,Expense Type,Merchant Name,Payment Method,AWS Key\n"
                f.write(header)
                s = self.info['TransactionDate'] + ',' + self.info['Total'] + ',' + self.info['Items'] + ',' + self.info['ExpenseType'] + ',' + self.info['MerchantName'] + ','  + self.info['Payment Method'] + ',' + key + '\n'
                f.write(s)
        else:
            addNewLine = False
            with open(file, 'rb') as f:
                try:  
                    f.seek(-2, os.SEEK_END)
                    while f.read(1) != b'\n':
                        f.seek(-2, os.SEEK_CUR)
                except OSError:
                    f.seek(0)
                last_line = f.readline().decode()
                if last_line[-1] != '\n':
                    addNewLine = True
            with open(file, 'a') as f:
                s = self.info['TransactionDate'] + ',' + self.info['Total'] + ',' + self.info['Items'] + ',' + self.info['ExpenseType'] + ',' + self.info['MerchantName'] + ','  + self.info['Payment Method'] + ',' + key + '\n'
                if addNewLine:
                    s = '\n' + s
                f.write(s)

    def bookkeeping(self):
        file = './properties/' + self.info['Property'] + '.csv'
        src_folder = r"./images/"
        file_name = self.info['ImageFile'].split('/')[-1]
        key_len = 13
        encrypted_key = secrets.token_urlsafe(key_len) + file_name
        s3 = boto3.client("s3", region_name=secret.getRegionName(), aws_access_key_id=secret.getAccessKey(), aws_secret_access_key=secret.getSecretKey(), endpoint_url='https://s3.' + secret.getRegionName() + '.amazonaws.com')
        bucket = secret.getBucket()
        key = self.info['Property'] + '/' + encrypted_key

        if not self.uploadFileAWS(s3, bucket, key, src_folder + file_name):
            return False
        if not self.fileExistsAWS(s3, bucket, key):
            return False
        os.remove(src_folder + file_name)

        self.writeToFile(file, bucket, key)
        if self.fileExistsAWS(s3, bucket, self.info['Property'] + '/' + self.info['Property'] + '.csv', '.csv'):
            if not self.deleteFileAWS(s3, bucket, self.info['Property'] + '/'):
                return False
        if not self.uploadFileAWS(s3, bucket, self.info['Property'] + '/' + self.info['Property'] + '.csv', file):
            return False

if __name__ == "__main__":
    root = Tk()
    window = RootWindow(root)
    root.mainloop()
 
