# Script accepts XML files as backups of SMS provided by Titanium Backup
# Script also takes contacts.db file as a source for contacts name.
# Ideally it is also extracted from Titanium Backup of Contacts.
print("\n Booting...\n \n")

# Import modules
import os
import json
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import datetime, time
import dateutil.parser

# Use phone contacts, based on contacts.db provided by TitaniumBackup
def parse_contacts_db(db_file):
	try:
		conn = sqlite3.connect(db_file)
		print(" (successfully read)")
		return conn
	except Error as e:
		print(" (" + str(e) + ")\n")
	return None
 
def initDB():
	for file in os.listdir( os.getcwd() ):
		if file.endswith('.db'):
			db = file
			break
	
	if not 'db' in locals():
		print(" No contacts database file found \n")
		return None

	print(" Found contacts database:", db, end="")
 
	# try database connection
	global conn
	conn = parse_contacts_db(db)

# Time converter
def parseTime(t):
	pass
	return int( time.mktime( dateutil.parser.parse(t).timetuple() ) )

# The core of the script. simply wrapped up in a function due cleaner code
def parseXML():
	# Find available XML files
	files = []

	for file in os.listdir(os.getcwd()):
		if file.endswith(".xml"):
			files.append(file)

	print("\n", len(files), "XML files have been found.")

	# Init variables
	global messages, messagesOut, filesCounter, totalCounter, skipCounter, sizeXML, numbersCounter
	messages = []
	messagesOut = []
	filesCounter, totalCounter, skipCounter, sizeXML, numbersCounter = (0,) * 5

	# Parse each file
	for file in files:

		# Increment counter
		filesCounter += 1
		msgTmp = []

		# Read the file
		try:
			theFile = open(file, 'r', encoding="utf8")
			tmp = BeautifulSoup(theFile, 'xml')
		except UnicodeDecodeError as e:
			print(" There is a problem with file encoding")
			print(" Error:", e)
			exit()

		sizeXML += os.path.getsize(file)

		# Find all threads
		threads = tmp.find_all("thread")
		print("\n Parsing XML #" + str(filesCounter), " Length:", len(threads), "")	

		# Parse each thread
		for index, thread in enumerate(threads[25:]):
			
			# Temporary var for parsing thread
			display_name, raw_contact_id = '', ''
			
			number = thread['address'].strip().replace(' ', '')
			# Min match is the last 7 digits of the number in reversed sequenced, 
			# it is used as more reliable way to find numbers in Android db.
			# It will also be used here to filter for contact name in db and later for duplicates.
			min_match = str(number[::-1][:7])

			# Cancel if not a proper person number (to clean some of the service/operator info threads)
			if len(number) < 9:
				skipCounter += 1
				continue

			msg = {
				'name'	: '',
				'number': number,
				'min_match' : min_match,
			 	'conversations': []
			}

			# Try to find a name for a contact
			if 'conn' in globals():
				# print(' Looking for contact name')

				try:
					cur = conn.cursor()
					# Using full match
					# query = "SELECT raw_contact_id FROM phone_lookup WHERE normalized_number = '" + str(number) + "'"

					# Using min match,( uses Reversed last 7 digits of the number)
					query = "SELECT raw_contact_id FROM phone_lookup WHERE min_match = '" + min_match + "'"
					# print(" Querying:", query)
					cur.execute(query)
					raw_contact_id = cur.fetchall()
				except Error as e:
					print("\n An Error Has Occurred during first phone lookup:", e,)


				if 'raw_contact_id' in locals() and raw_contact_id:

					try:
						query = "SELECT display_name FROM raw_contacts WHERE _id = '" + str( raw_contact_id[0][0] ) + "'"
						# print(" Querying:", query)
						cur.execute(query)

						display_name = cur.fetchall()[0][0]
						msg['name'] = display_name

						numbersCounter += 1

					except Error as e:
						print("\n An Error Has Occurred during second phone lookup:", e, "\n")

				else:
					# print(' No contact name found')
					pass

			# print(" Currently parsing SMS for", str(display_name), "(" + str(number) + ")")

			# Find all SMS within current thread
			smsList = thread.find_all('sms')

			# Cancel if there is no SMS
			if len(smsList) > 0:
			
				# Iterate through sms and store in thread var
				for index, sms in enumerate(smsList):

					totalCounter += 1

					msg['conversations'].append({
						'type': 		sms['msgBox'],
						'body': 		sms.contents[0],
						'encoding':		sms['encoding'],
						'timestamp': 	int(parseTime(sms['date']))
					})
				
				# Done parsing thread, sort and push to temp file var
				# msg['conversations'] = sorted( msg['conversations'], key=lambda k: k['date'] )
				msgTmp.append( msg )
			else:
				# Track empty threads
				skipCounter += 1

		# Store parsed file to global messages
		messages.append(msgTmp)

		# Close working file
		theFile.close()

# Search function
def search(key, value, dicts):
	# return next( (item for item in dicts if item[key] == value), False )
	for index, element in enumerate(dicts):
		if element[key] == value:
			return index
		else:
			continue
	return False

# Clean duplicates
def merge(input, output):

	# Another stats var to track merged threads
	global nameMatch
	nameMatch = 0

	print("\n Merging... \n")

	for index, colection in enumerate(input):

		print(" XML #" + str(index+1), end=" | ")

		for thread in colection:
			# Search for threads with the same number
			checkNum = search("number", thread['number'], output)
			
			# Search for threads with the same contact name, avoid empty ones
			if len(thread['name']) == 0:
				checkName = False
			else:
				checkName = search("name", thread['name'], output)

			# Conditionally treat search results
			if checkNum is not False:
				# Number match found
				nameMatch += 1
				# Add current thread conversations to a found one
				for sms in thread['conversations']:
					# But avoid messages that are already in there, by timestamp
					tmpTry = search("timestamp", sms['timestamp'], output[checkNum]['conversations'])
					if tmpTry is False:
						output[checkNum]['conversations'].append(sms)

			elif checkName is not False:
				# Contact name match found
				nameMatch += 1
				# Add current thread conversations to a found one
				for sms in thread['conversations']:
					# But avoid messages that are already in there, by timestamp
					tmpTry = search("timestamp", sms['timestamp'], output[checkName]['conversations'])
					if tmpTry is False:
						output[checkName]['conversations'].append(sms)
			else:
				output.append(thread)

		# Just in case, sort it
		output[checkName]['conversations'].sort(key=lambda item:item['timestamp'], reverse=True)

	print('Done')

def hr():

	print(" \n ______________________________________________________________ \n")

# Look for contacts
initDB()
hr()
# Look and parse XML SMSs
parseXML()
hr()
# Merge all parsed threads and possible duplicates
merge(messages, messagesOut)
hr()


# Write info as JSON to a data.json file
dataFile = open("data.json", "w")
dataFile.write(json.dumps(messagesOut))
# dataFile.write(json.dumps(messagesOut, indent=2))
dataFile.close()

# Calc file size stats
sizeData = os.path.getsize("data.json")
diff = sizeXML/sizeData

print("\n Successfully exported to 'data.json' (" + str(round(sizeData/1024/1024, 2)) + " MB) \n")

# Finish up N show some stats
print(" Fun fact, your output is", round(diff, 1), "times smaller!")

hr()

print("\n", len(messages), "files have been parsed containing", totalCounter, "messages \n")

print("", skipCounter, "empty threads have been skipped. \n")

print("", numbersCounter, "numbers recognized \'N", nameMatch, "contacts merged.")

hr()

print("\n Wrapping up with", len(messagesOut), "nicely formated threads. Done! \n\n")
