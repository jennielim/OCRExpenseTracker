# OCRExpenseTracker
User has the option to scan or download previously scanned expense reports that have been uploaded to AWS S3. Scanning is done with Microsoft Azure Form Recognizer REST API and is verified by the user though a GUI. The scans are automatically uploaded to AWS S3 and the important information is collected and sorted. The user can view the data by opening a csv file of their choice.

# To run:  
- Clone  
- Create and empty folder called 'properties' in the root directory  
- Put images in 'images' folder. There are sample ones in there  
- Download any necessary dependencies  
- Put personal Azure and AWS information in 'secrets.py'  
- Double click on 'main.command' and the application will start up. 

https://towardsdatascience.com/how-to-upload-and-download-files-from-aws-s3-using-python-2022-4c9b787b15f2
