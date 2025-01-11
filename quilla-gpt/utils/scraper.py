from utils.extract_tramites_fci import extract_tramites_fci
from utils.extract_tramites_ocr import extract_tramites_ocr
from utils.extract_tramites_sites import extract_tramites_sites

def scraper():
    print("Scraping tramites FCI...")
    extract_tramites_fci()
    print("Scraping tramites OCR...")
    extract_tramites_ocr()
    print("Scraping tramites sites...")
    extract_tramites_sites()