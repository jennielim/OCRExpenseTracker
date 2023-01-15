# OCRExpenseTracker
User has the option to scan or download previously scanned expense reports that have been uploaded to AWS S3. Scanning is done with Microsoft Azure Form Recognizer REST API and is verified by the user though a GUI. The scans are automatically uploaded to AWS S3 and the important information is collected and sorted. The user can view the data by opening a csv file and download files from AWS to clear space locally.

# To run:  
- Clone  
- Go to directory
- Install requirements with `pip3 install -r requirements.txt`
- Create and empty folder called 'properties' in the root directory  
- Put images in 'images' folder. There are sample ones in there  
- Put personal Azure and AWS information in 'secrets.py'  
- Create AppleScript in Automator by entering this code and entering the correct path
```
on run {input, parameters}
	
	tell application "Terminal"
		activate
		do script "path/to/OCRExpenseTracker && python3 main.py"
	end tell
	
	return input
end run
```

# To use:  
- Double click on icon created above to run the program
- Scan receipts first, place in 'images' folder and follow along with the prompts
- View the entered and scanned information in the properties folder
- To download the receipts, click on the download receipts button and enter AWS Key found in the csv file
