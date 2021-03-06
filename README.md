# SMS Parser to HTML for Titanium Backup SMS file

A **Python 3** based script that parses an SMS backup file generated by [Titanium Backup](https://play.google.com/store/apps/details?id=com.keramidas.TitaniumBackup&hl=en) app. The generated output includes `data.json` file that organizes all SMS by number and, if provided with `contacts.db` file (from Titanium Backup Contacts backup or equivalent), also adds the name of the number. The output can be easily accessed and read by `index.html` page.

The parser accepts **unlimited** number of backup **XML files**. It does also check and merge same number threads, however, it makes no assumption about thread contents and may contain duplicate messages.


## Idea

As various instant messengers are evolving into our daily lives and have almost replaced SMS - the idea is to **save** old **SMS messages** that may contain conversations one would like to keep and have them accessible in an easy human-readable way.

While the **SMS** can be saved by **Titanium Backup app**, the backup file is not much of use yet but rather has data stored in a complicated XML format.

The **Python script** was written with a goal to **export** the messy **XML file to** a more structured and broader file format **JSON**. So the message threads could later be easily imported to any language of choice. 

**Index.html** is built to read the `data.json` and **display messages** in a modern (uses CSS Grid and is responsive) independent way. Basically, every device has a browser, and that is all needed to wander through conversations. 


## Requirements

- [Python 3+](https://www.python.org/) compiler with following dependencies:
    - [Beautiful Soup 4 + ](https://www.crummy.com/software/BeautifulSoup/) library.
    - An [lxml](http://lxml.de/) parser.
    - [Dateutil](https://dateutil.readthedocs.io/en/stable/) extension.
- Titanium Backup generated (or equivalent) .xml file (-es).
- TB generated (or equivalent) `contacts.db` file. If provided add contact's full name to output. Optional.


## Setup & Run

Python script depends on the `` and `` libraries.
1. Install dependencies: 
    
    ``` pip install lxml beautifulsoup4 python-dateutil ```
    
    Depending on the system setup you may need to use `pip3` instead.
    
    ``` pip3 install lxml beautifulsoup4 python-dateutil ```
    
2. Place backup file or files into script root folder and run the parser:
    
    ``` python3 parse.py ``` 
    
3. Enjoy generated `data.json` output. You may explore messages by using minimal interface on the index.html page.

> Please note that due to some security policies not all browsers may load file. For instance, Google Chrome does NOT but Edge does it fine.


## Disclaimer

The parser, a Python-based script was built to merely export an XML based backup to JSON, and therefore, may not perform perfectly in every environment. So as the index.html page, who is equipped with minimal and not neccessarily best practice JavaScript functionality and CSS Grid-based styling to merely make contents easily accessible and readable in a browser. It is open for improvements but no active maintenance should be expected.

Enjoy!













