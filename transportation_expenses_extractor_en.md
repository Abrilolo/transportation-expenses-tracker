# Transportation Expenses Extractor

---

## Quest Description

- Software Development Project

### Project Name

Pythonアプリ開発 - 交通費抽出アプリ
Transportation Expenses Extractor

### Objects

- Extract transportation expenses recorded in the physical Suica/Pasmo card through NFC reader and organize it into a Excel file.
- Document the development process appropriately.
  - Git
  - Journal

### Required qualifications

- Programming Language
  - Python
- Knowledge of
  - NFC
- Experience in
  - Writing 100+ lines of functional codes.
  - Documentation.
- Miscellaneous
  - Communication skills with those who speal little or no English.
  - Problem-solving skills, with the ability to lead operational and strategic initiatives.

---

## Technical difficulty level

|Level|Description|
|--|--|
|0|No experience|
|1|Basic programming knowledge and functional code experience|
|2|Basic programming skills and practical experience in a specific technology or framework|
|3|Intermediate programming skills and experience in a specific area|
|4|Advanced programming skills and expertise in a specific domain|
|5|This is a project for advanced users who have deep specialized knowledge and extensive practical experience and can complete the project by themselves.|

> Difficulty level: [0-5] (1 is for beginners, 5 is for advanced users)

- Difficulty: 1

---

## Project Details

### Project milestones

1. Research on NFC cards.
2. Read on [NFCPy](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html) and see what you can do with this library to extract records from a NFC card.
3. Set up a NFC Reader.
4. Write a Python program that opens the reader.
5. Write a Python program that reads the tag of a NFC card via the reader.
6. Write a Python program that reads a record from a NFC card via the reader.
7. Do research on Japanese station codes and interpret the record in a meaningful manner.
8. (Optional) Make documentation necessary to start a project to develop a software for a customer.
   1. Make a requirement list. See [resources](https://gitlab03.irvine.jp/irvine/internship/internship_quests/-/tree/main/en/orientasion/resources?ref_type=heads).
   2. Make a inception deck. See [resources](https://gitlab03.irvine.jp/irvine/internship/internship_quests/-/tree/main/en/orientasion/resources?ref_type=heads) and [reference](https://agilewarrior.wordpress.com/2010/11/06/the-agile-inception-deck/).
9. Write a Python program that reads all the transportation record from a NFC card and output them to an Excel file. The sample outfile is [here](./transportation_expenses/Reimursement_Sample.xlsx). Unfortunately, a physical Suica card stores only 20 records.
   1. (Optional) As you write the program, create sequence diagrams that depicts the interaction between the objects in a sequential order.

### How to proceed

- Agile + Scrum
- GitLab
- Redmine
- Any text editor, IDE
- Sequence diagrams in Markdown and Mermaid
  - [Sample](https://www.geeksforgeeks.org/unified-modeling-language-uml-sequence-diagrams/)
- [NFCPy](https://nfcpy.readthedocs.io/en/latest/topics/get-started.html)
- [RC-S380/S - USB NFC Reader](https://www.sony.net/Products/felica/business/products/RC-S380.html)
  - This does not work on Mac OS ([source](https://www.sony.co.jp/Products/felica/business/support/faq/detail/268.html)).

### Deliverables

- Functional Pyton program
- (Optional) Requirements sheet
- (Optional) Inception deck
- (Optional) Sequence diagrams

---

## Rewards from this project

### Technical skills

- Programming in Python.
- Documentation.

### Experiences

- Develop an app for a service that you're not familiar with, mainly documented in languages except English.
- Project management.

### Miscellaneous

- Research skills.
- Probrem solving skills.
- Communication skills.

### Challenge rewards

- Understanding of the challenges and joys of software development
- Experience in software development processes from development to deployment
- Experience in Scrum software processes
- Fundamentals of technical documentation writing
- Experience in Python

---

## (SPOILER)

This quest requires you to read a lot of documentation in Japanese.
Refer to the following resources if you get lost.

1. [Station code table](https://github.com/furugori/ekicode)
2. [Works done by the former internship students](https://gitlab03.irvine.jp/irvine/internship/internship_quest_submission/-/tree/main/2024/Together?ref_type=heads)
3. [Sample program 1](https://yamori-tech.hatenablog.com/entry/suica-data-readout)
4. [Sample program 2](https://qiita.com/sengoku/items/f12c85093e8726410393)
5. [May be helpful if SONY RC-S380 does not work.](https://con3.com/sc2scratch/?p=276)
