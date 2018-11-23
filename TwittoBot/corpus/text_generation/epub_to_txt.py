import os, sys, io, re
from zipfile import BadZipFile
from epub import open_epub, BadEpubFile
from xml_cleaner import to_raw_text

def try_utf8(data):
	try: return data.decode('utf-8')
	except UnicodeDecodeError: return None

def try_decode(ebook, item):
	try: return try_utf8(ebook.read_item(item))
	except KeyError: return None

def open_book(path):
	try: return open_epub(path)
	except (BadEpubFile, BadZipFile, KeyError, IndexError):	return None

def convert_xml_element_to_lines(data, boundary):
	start_boundary = "<%s" % (boundary)
	end_boundary = "</%s>" % (boundary)
	data = data.replace("\xa0", " ")
	multi_line = data.split("\n")
	lines = []
	in_book = False
	for line in multi_line:
		if line.find(start_boundary) != -1:
			in_book = True
			line_end = line.find(">")
			sliced_line = line[line_end+1:]
			if len(sliced_line) > 0: lines.append(sliced_line)
			continue
		if line.endswith(end_boundary):
			in_book = False
			line_end = line.find("<")
			sliced_line = line[:line_end]
			if len(sliced_line) > 0: lines.append(sliced_line)
			continue
		if in_book:
			lines.append(line)
	return lines

def convert_epub_to_lines(ebook):
	lines = []
	for item in ebook.opf.manifest.values():
		data = try_decode(ebook, item)
		if data != None:
			lines.extend(convert_xml_element_to_lines(data, "body"))
	return lines

try:
	book = os.path.abspath("epub/" + sys.argv[1])
	text = to_raw_text(' '.join(convert_epub_to_lines(open_book(book))))
	text = '\n'.join([' '.join(line) for line in text])
	text = re.sub("& *[A-Za-z]+ *;", " ", text) # caractères HTML
	text = re.sub("(StartFragment >)|(EndFragment >)|(endif)|(& gt ; !)|(& lt ; !)|(& # 160 ;)|[\t\r «»]+", " ", text) # caractères Epub
	text = re.sub(" *['’] *", "' ", text) # Collage des apostrophes
	text = re.sub(" +,", ",", text) # Collage des virgules
	text = re.sub(" +\.", ".", text) # Collage des points finaux
	with io.open("txt/" + sys.argv[1][:-4] + "txt", 'w', encoding="utf-8") as txtfile:
		txtfile.write(text)
	print("Conversion epub -> txt : Terminé")

except Exception as e: print("Erreur : " + str(e))
