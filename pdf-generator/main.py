import sys
import os
import sys
import time
import hashlib
import pdfrw
from dotenv import load_dotenv
load_dotenv()

from create_redirect import create_redirect

# run: python main.py "{NAME_OF_CV_RECEIVER}"

BASE_PDF = os.environ['BASE_PDF']
CV_VERSION  = os.environ['CV_VERSION']
FINAL_PDF = os.environ['FINAL_PDF']
pdf = pdfrw.PdfReader(BASE_PDF)
new_pdf = pdfrw.PdfWriter()

if len(sys.argv) == 1:
  print("Please add an name as an Identifier as 2nd arg")
  exit()

cv_receiver = sys.argv[1]
cv_receiver_hash = hashlib.md5(cv_receiver.encode()).hexdigest()
params = {
  'cv_receiver': cv_receiver,
  'cv_receiver_hash': cv_receiver_hash,
  'version': CV_VERSION,
  'utm':{
  'utm_source': 'cv',
  'utm_medium': 'cv-v' + CV_VERSION,
  'utm_campaign': cv_receiver_hash,
}
}

for page in pdf.pages:
    # Links are in Annots, but some pages don't have links so Annots returns None
    for annot in page.Annots or []:
        old_url = annot.A.URI[1:-1]
        redirect_url = create_redirect(old_url, params)
        annot.A.URI = pdfrw.objects.pdfstring.PdfString("(" + redirect_url + ")")

    new_pdf.addpage(page)    

new_pdf.write(FINAL_PDF)



