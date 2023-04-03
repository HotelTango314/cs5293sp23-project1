import spacy
import io
import sys
import os
import argparse
import glob
import sqlite3
import en_core_web_md
from spacy.matcher import Matcher
from spacy.util import filter_spans

person =[{'POS':'PROPN','OP':'?'},{'POS':'PROPN','ENT_TYPE':'PERSON'},{'POS':'PROPN','ENT_TYPE':'PERSON','OP':'*'}] 

date = [{'ENT_TYPE':'DATE', 'OP':'+'}]

telephone = [{'ORTH':'(','OP':'?'},{'IS_DIGIT':True,'LENGTH':3},{'IS_PUNCT':True,'OP':'?'},{'IS_DIGIT':True,'LENGTH':3},{'IS_PUNCT':True,'OP':'?'},{'IS_DIGIT':True,'LENGTH':4}]

filial = [{'LOWER':{'IN':['grandfather','grandmother','father','mother','aunt','uncle','brother','sister','husband','wife','son','daughter','neice','nephew','granddaughter','grandson','boy','boys,','girl','girls','man','men','woman','women','he','him','his','she','her']}}]

postal = [{'IS_DIGIT':True,'OP':'+'},{'POS':'PROPN','OP':'+'},{'IS_PUNCT':True,'OP':'?'},{'POS':'PROPN','OP':'*'},{'IS_DIGIT':True,'OP':'*'},{'POS':'PROPN'},{'IS_PUNCT':True,'OP':'?'},{'POS':'PROPN'},{'IS_DIGIT':True,'OP':'*'}]

#postal = [{'ORTH':'105 Daventy Lane, Suite 300 Louisville, Kentucy 40223'}]

def sharpie(text, start_redact, end_redact):
    newtext = text[:start_redact]+("\u2588"*((end_redact - start_redact)+1))+text[end_redact+1:]
    return newtext

def extractor(filename):
    with open(filename,'r') as f:
        return f.read()

def make_database(data):
    conn = sqlite3.connect('stats.db')
    curs = conn.cursor()
    curs.execute("DROP TABLE IF EXISTS STATS")
    curs.execute("""
    CREATE TABLE STATS(
    redacted_word TEXT
    ,file_redacted TEXT
    ,start_index INT
    ,end_index INT
    );
    """)
    for x in data:
        t = (x[0],x[1],x[2],x[3])
        curs.execute("INSERT INTO STATS VALUES (?,?,?,?)",t)
        conn.commit()
    conn.close()

def pull_data(destination):
    conn = sqlite3.connect('stats.db')
    curs = conn.cursor()
    select_all = "SELECT * FROM STATS"
    overall_span_count =    ("SELECT redacted_word, COUNT(redacted_word) "
                            "FROM stats "
                            "GROUP BY 1 "
                            "ORDER BY COUNT(redacted_word) DESC ")
    filename_span_count =   ("SELECT redacted_word, file_redacted, COUNT(redacted_word)"
                            "FROM stats "
                            "GROUP BY 1,2 " 
                            "ORDER BY file_redacted, COUNT(redacted_word) DESC ")
    num_redact_by_doc =     ("SELECT file_redacted, count(redacted_word)"
                            "FROM stats GROUP BY 1 ORDER BY 1")
    rep1 = curs.execute(num_redact_by_doc).fetchall()
    rep2 = curs.execute(overall_span_count).fetchall()
    rep3 = curs.execute(filename_span_count).fetchall()
    rep_dict = {"total number of redactions by document":rep1,
            "overall count of redactions by word":rep2,
            "by file count of redactions by word":rep3} 
    final_report = prep_report(rep_dict)
    if destination == 'stderr':
        for x in final_report:
            print(x,file=sys.stderr)
    elif destination == 'stdout':
        for x in final_report:
            print(x)
    else:
        with open(destination,'w') as f:
            for x in final_report:
                f.write(x)
                f.write('\n')

def prep_report(data_dict):
    report_lines = []
    report_lines.append("TOTAL NUMBER OF REDACTIONS BY DOCUMENT")
    report_lines.append("--------------------------------------")
    report_lines.append("FILE NAME       | COUNT ")
    for x in data_dict["total number of redactions by document"]:
        report_lines.append(f"{x[0]}"+" "*(16-len(x[0]))+f"| {x[1]}")
    
    report_lines.append(" ")
    
    report_lines.append("OVERALL COUNT OF REDACTIONS BY WORD")
    report_lines.append("-----------------------------------")
    report_lines.append("REDACTED WORD             | COUNT ")
    for x in data_dict["overall count of redactions by word"]:
        report_lines.append(f"{x[0]}"+" "*(26-len(x[0]))+f"| {x[1]}")
    
    report_lines.append(" ")
    
    report_lines.append("COUNT OF REDACTIONS BY WORD BY FILE")
    report_lines.append("-----------------------------------")
    report_lines.append("REDACTED WORD          | FILE          | COUNT ")
    for x in data_dict["by file count of redactions by word"]:
        report_lines.append(f"{x[0]}"+" "*(23-len(x[0]))+f"| {x[1]} "+" "*(10-len(x[1]))+f"| {x[2]}")
    
    return report_lines

def save_file(text, filename, output):
    no_slash = filename[filename.find('/')+1:-4]
    new_path = f'{output}{no_slash}.redacted'
    with open(new_path, 'w') as f:
        f.write(text)

def main(file,names,dates,phones,genders,address,output,stats):
    #CREATE SPACY OBJECT LOADED WITH MODEL, AND MATCHER
    nlp = en_core_web_md.load()
    matcher = Matcher(nlp.vocab)
    agg_stat = []

    #LOAD RULES TO MATCHER
    if(names):
        matcher.add('PERSON',[person])
    if(dates):
        matcher.add("DATE",[date])
    if(phones):
        matcher.add("PHONE",[telephone])
    if(genders):
        matcher.add("FAMILY",[filial])
    if(address):
        matcher.add("POSTAL",[postal])

    #ITERATE OVER THE FILES FROM THE GLOB
    for filename in glob.glob(file):
        text = extractor(filename)
        text2 = extractor(filename) ##
        doc = nlp(text)
        matches = matcher(doc)
        spans = []
        for match_id, start, end in matches:
            matched_span = doc[start:end]
            spans.append(matched_span)
        filtered_spans = filter_spans(spans)
        for span in filtered_spans:
            index_start = span.start_char
            index_end = span.end_char
            agg_stat.append([text2[index_start:index_end],filename,index_start,index_end])
            text = sharpie(text, index_start, index_end)
        save_file(text,filename,output) 
    make_database(agg_stat)
    pull_data(stats)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input',required=True,help="provide text content")
    parser.add_argument('--names', action='store_true')
    parser.add_argument('--dates', action='store_true')
    parser.add_argument('--phones', action='store_true')
    parser.add_argument('--genders', action='store_true')
    parser.add_argument('--address', action='store_true')
    parser.add_argument('--output', required=True,help="save location of redacted files")
    parser.add_argument('--stats', required=True,help="preferred file name for stats report")
    
    args = parser.parse_args()
    main(args.input,args.names,args.dates,args.phones,args.genders,args.address,args.output,args.stats)


