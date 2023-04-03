# PROJECT 1 README

## HENRY THOMAS [[[]]] CS5293 SP23

### 1. HOW TO INSTALL

The project can be installed by running the following code:

pipenv install project1

---

### 2. HOW TO RUN

To run from the root directory of the pip environment (~/cs5293sp23-project1) it is recommended that the following command be used to run the redactor tool:

```
 pipenv run python project1/redactor.py \
 --input 'docs/\*.txt' \
 --names --dates --phones --genders --address \
 --output 'docs/' \
 --stats stdout | less
```
project1/redactor.py is the location of the python source file which does the redacting.

The string after --input should be a file name (globs are acceptable)
--names, --dates, --phones, --genders, --address indicate that these items should be redacted
by omitting any of these 4 items, that omitted item will not be redacted from the final product.

--output indicates the location where the newly created redacted files should be saved.
In this case it is indicated that the output should be saved in the 'docs' folder.

--stats indicates the location to which the --stats data should be sent or saved.
The options are:

	- stdout - prints the stats output to stdout
	- stderr - prints the stats output to stderr 
	- \<filename\> - saves the stats in a file named \<filename\>

Visit this link for a video example of how to run:
[youtube.com](https://www.youtube.com/watch?v=_hD78v58CwE)

### 3. Bugs

The only bugs are things that the rules-based matcher may be missing items which should have been redacted, or vice versa. The rules applied to each flag are discussed in the next section.

### 4. Rules

--names
The intent was to filter out only people names. The match pattern for this flag was
- 0-1 proper nounds (Mr., Mrs. Dr., etc.)
- Precisely 1 proper noun of entity type "PERSON"
- Followed by 0 or more proper nouns of entity type "PERSON"

For the most part we get people names. It also picks up several company names so it is not working perfectly.

--genders
The intent is to filter out any word that could be connected with gender. The match pattern is just a list of words I could think of that would meet this criteria. This is a hard one, I tried several things looking for pronouns with certain characteristics that would always be gender related but was unable to do it. I settled on just a list of words that are gender specific that the rule looks for (grandather, mother, aunt, uncle, brother, sister, etc...)

--dates
The intent for dates was to filter out anything that could be a date. The criteria for this rule was
- 1 or more tokens that the model considers to be of entity type date.

Using just this one token we pick up all the dates and many other things that are much more vague dates (i.e. "the early 70's).

--phones
The phone number match rule consists of the following:
- 0-1 '('
- 3 digits
- 0-1 punctuation marks
- 3 digits
- 0-1 punctuation marks
- 4 digits

This works quite pretty well howver, it struggles with phone numbers that are formatted with '.' between the segment of numbers.

--address
The phone number match rule consists of the following:
- 1 or more digits (this would be the street number)
- 1 or more proper nouns (this would be the street name)
- 0-1 punctuation marks (this would be a comma)
- 0 or more proper nouns (this might be the word Suite or Apartment)
- 0 or more digits (this would be the suite or apartment number)
- precisely 1 proper noun (this would be the city name)
- 0-1 punctuation marks (this would be a possible comma between city and state)
- precisely one proper noun (this would be the state name)
- 0 or more digits (this would be the zip code)

The address does work, it picks up at least one address. However, most of the addresses in emails appear at the bottom of the email, and somethign about being at the bottom of the email throws off the model and it doesn't realize that it is an address. Perhaps the parts of speech tagging doesn't work as well for these signature lines because they are not part of a full sentence.

### 5. TESTS

No package is complete without some tests to verify operability.

First we test the "Sharpie" method. The "Sharpie" method is what actually replaces the identified sensitive info in the string with the 'full block character'. As if you took a 'sharpie' and marked the word out. To test the sharpie method, we pass it a string ,"Hello World" and have the sharpie method black out the whole thing, and then the test is verifying that the length of the blotted out string is the same as the length of the original string.

Next we test the "extractor" method which pulls the text out of the files for analysis. The test consists of writing a file with known content and then using the extractor method to "extract" that content from the file. We then verify that the extracted content matches what we know it actually is (because we had just created it)

Then we test the "make\_data\_base()" function which first deletes any existing database file that may exist to ensure that we are only seeing the database created by the test. Then we insert a single record into the newly created database and we test to see if the path for the new database exists.

Then we test the "pull\_data()" and "prep\_report()" functions at the same time. We pull the data from the database created in the previous test. The "pull\_data()" function calls the "prep\_report()" function in its operation. We know that with only one line in the database, the "prepped report" will consist of 14 lines. So we just count up the number of lines to verify that the report was properly created.

We test the "save\_file()" function which ensures that a file with with the .txt extension will be saved with the '.redacted' extension.

Finally and perhaps most importantly, we test the whole system together on a test string that contains all of the things that were are trying to redact. The test string is

> John Smith was born 8/8/1975. He lived at 123 Main St. Krum, Texas. His phone number is 123-345-9743. [^1]

We know that after redaction, the sentence should look like this:

> ███████████was born █████████ ███lived at █████████████████████████ ████phone number is █████████████

During the test, the `main()` function is called and the product of this function is compared to the redacted sentence given above. The 'true-ness' of the match is asserted in the test and if they do match then the test is passed.

This test creates several stray files in the process of running. To keep things tidy all files created in the process of running this test are deleted at the end automatically.


[^1]: This sentence is made up. Any similarity to any actual person living or dead is coincidental.

### 6. OTHER NOTES

The reporting feature of this python package runs off of sqlite3. The redaction data is loaded into the database and then queried to create the report.

One important piece of this project is the use of one of the SpaCy utilities called filter\_spans(). The filter\_spans() utility combines overlapping spans and makes it easier to report on the spans that were redacted.
