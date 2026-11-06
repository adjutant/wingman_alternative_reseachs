# /// script
# requires-python = ">=3.12"
# dependencies = ["Markdown==3.7", "beautifulsoup4==4.12.3"]
# ///
"""Locate prose that needs review. Findings are editorial cues, not compliance failures."""
from pathlib import Path
import json
import re
import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]

def main():
    documents = []
    paths = sorted(ROOT.glob('*/assessment/*.md'))
    paths += [ROOT/'WINGMAN_PURPOSE.md', ROOT/'AGENTS.md']
    paths += sorted(ROOT.glob('generic/assessments/*.md'))
    paths += sorted(ROOT.glob('generic/assessments/_audits/qa*.md'))
    for path in paths:
        soup = BeautifulSoup(markdown.markdown(path.read_text(), extensions=['tables','fenced_code']), 'html.parser')
        for element in soup.select('pre'): element.decompose()
        for element in soup.select('code'): element.string = 'CODE'
        candidates = []
        for element in soup.select('p,li,td'):
            if element.find(['p','li']): continue
            text = element.get_text(' ',strip=True)
            for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Za-z0-9“])',text):
                words = len(sentence.split())
                if words > 35:
                    candidates.append({'word_count':words,'text':sentence})
        documents.append({'path':str(path.relative_to(ROOT)), 'long_sentence_candidates':candidates})
    progress = json.loads((ROOT/'generic/assessments/prose-review-progress.json').read_text())
    result = {'scope':'Editorial queue. Counts include some citations. A short sentence can still be unclear or inaccurate.',
              'detailed_assessment_review':progress['status'],
              'documents':documents}
    (ROOT/'generic/assessments/writing-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'{len(documents)} documents; {sum(len(x["long_sentence_candidates"]) for x in documents)} long-sentence candidates.')

if __name__=='__main__':main()
