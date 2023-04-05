from project1 import redactor
import os
import sqlite3
import glob

def test_sharpie():
    text = 'hello world'
    tester = redactor.sharpie(text, 0, len(text)-1)
    assert tester == "\u2588"*len(text)


def test_extractor():
    sample_text = 'hello world!'
    sample_file = 'sample'
    with open(sample_file,'w') as f:
        f.write(sample_text)
    test = redactor.extractor(sample_file)
    os.unlink(sample_file)
    assert test == sample_text

def test_make_database():
    if(os.path.exists('stat.db')):
        os.unlink('stats.db')
    test_data = [['hello world!', 'myfile',0,11]]
    redactor.make_database(test_data)
    test = os.path.exists('stats.db')
    assert test

def test_pull_data_prep_report():
    redactor.pull_data('sample')
    num_lines = 0
    with open('sample','r') as f:
        for lines in f:
            num_lines = num_lines + 1
    test = num_lines == 14
    os.unlink('sample')
    os.unlink('stats.db')
    assert test

def test_save_file():
    text = "hello world!"
    filename = '/sample.txt'
    output = ''
    redactor.save_file(text,filename,output)
    with open('sample.txt.redacted','r') as f:
        result = f.read()
    test = (result == text)
    os.unlink('sample.txt.redacted')
    assert test

def test_functionality():
    text = "John Smith was born 8/8/1975. He lived at 123 Main St. Krum, Texas. His phone number is 123-456-9743."
    filename = 'docs/sample.txt'
    with open(filename,'w') as f:
        f.write(text)
    redactor.main(filename, True, True, True, True, True, 'docs/','test_stats')
    redact_text = ("███████████was born █████████ ███lived at █████████████████████████ ████phone number is █████████████")
    
    with open('docs/sample.txt.redacted') as f:
        test = f.read()
    result = redact_text == test
    for file in glob.glob('docs/sample.*'):
        os.unlink(file)
    os.unlink('stats.db')
    os.unlink('test_stats')
    assert(result)


