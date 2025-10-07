import os
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from query import query_resume



class PreprocessResume:

    def __init__(self, name):
        self.name = name

    def pull_resume(self):
        resume = query_resume(self.name)
        return resume
    
    def clean_characters(self, resume):
        new_resume = []
        for section in resume:
            if not section:
                continue
            cleaned_section = re.sub(r"\n", "", str(section))
            new_resume.append(cleaned_section)

        return new_resume
    
if __name__ == '__main__':
    process = PreprocessResume('michael gurka')
    resume = process.pull_resume()
    new_resume = process.clean_characters(resume)
    print(new_resume[-1])