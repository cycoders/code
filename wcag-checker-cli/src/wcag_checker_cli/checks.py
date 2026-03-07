from typing import List
import re
from bs4 import ResultSet, Tag
from ..auditor import Auditor
from ..types import Issue

SUSPICIOUS_LINKS = {'click here', 'here', 'read more', 'more info', 'link', 'go to'}

CHECKS = {
    'doctype': check_doctype,
    'lang': check_lang,
    'title': check_title,
    'viewport': check_viewport,
    'headings': check_headings,
    'images': check_images,
    'links': check_links,
    'forms': check_forms,
    'tables': check_tables,
    'empty_headings': check_empty_headings,
    'lang_consistent': check_lang_consistency,
}


def check_doctype(auditor: Auditor) -> None:
    if not re.search(r'<!DOCTYPE\s+html', auditor.original_html, re.I):
        auditor._add_issue(Issue(
            id='missing-doctype',
            wcag='4.1.1',
            principle='Robust',
            level='A',
            severity='warning',
            description='Missing or invalid DOCTYPE.',
            impact='Medium - Parsing issues in old browsers.',
            help='Use <!DOCTYPE html> as first line.',
        ))


def check_lang(auditor: Auditor) -> None:
    html_tag = auditor.soup.html
    if not html_tag or not html_tag.get('lang'):
        auditor._add_issue(Issue(
            id='missing-lang',
            wcag='3.1.1',
            principle='Understandable',
            level='A',
            severity='error',
            description='HTML root missing lang attribute.',
            impact='High - Screen readers assume wrong language.',
            help='Add <html lang="en">',
            examples=['<html>'],
        ))


def check_title(auditor: Auditor) -> None:
    title = auditor.soup.title
    if not title or not title.string or len(title.string.strip()) == 0 or len(title.string) > 70:
        auditor._add_issue(Issue(
            id='invalid-title',
            wcag='2.4.2',
            principle='Operable',
            level='A',
            severity='warning',
            description='Missing or overly long title.',
            impact='Medium',
            help='Use concise, descriptive <title> (40-60 chars).',
            examples=[title.string[:50] if title else 'None'],
        ))


def check_viewport(auditor: Auditor) -> None:
    viewport = auditor.soup.find('meta', attrs={'name': 'viewport'})
    if not viewport:
        auditor._add_issue(Issue(
            id='missing-viewport',
            wcag='1.4.10',
            principle='Perceivable',
            level='AAA',
            severity='info',
            description='Missing viewport meta for responsive design.',
            impact='Low',
            help='<meta name="viewport" content="width=device-width, initial-scale=1">',
        ))


def check_headings(auditor: Auditor) -> None:
    headings: List[Tag] = auditor.soup.find_all(re.compile(r'^h[1-6]$'))
    if not headings:
        auditor._add_issue(Issue(id='no-headings', wcag='1.3.1', principle='Perceivable', level='A', severity='warning',
                                 description='No headings found.', impact='Medium',
                                 help='Use semantic <h1>-<h6> for structure.'))
        return
    prev = 0
    for h in headings:
        lvl = int(h.name[1:])
        if lvl > prev + 1:
            auditor._add_issue(Issue(id='heading-skip', wcag='1.3.1', principle='Perceivable', level='AA', severity='warning',
                                     description=f'Heading level skip: h{prev} → h{lvl}.', impact='Medium',
                                     help='Use sequential levels.', examples=[h.get_text(strip=True)[:30]]))
        prev = lvl


def check_images(auditor: Auditor) -> None:
    imgs: ResultSet[Tag] = auditor.soup.find_all('img')
    for img in imgs:
        alt = img.get('alt', '').strip()
        if not alt:
            auditor._add_issue(Issue(id='img-no-alt', wcag='1.1.1', principle='Perceivable', level='A', severity='error',
                                     description='Image missing alt text.', impact='High',
                                     help='Add meaningful alt="" or alt="decorative".',
                                     examples=[img.get('src', 'N/A')]))
        elif alt == img.get('src', '') or len(alt) < 4:
            auditor._add_issue(Issue(id='poor-alt', wcag='1.1.1', principle='Perceivable', level='A', severity='warning',
                                     description='Poor alt text (decorative or generic).', impact='Medium',
                                     help='Use descriptive alt for content images.'))


def check_links(auditor: Auditor) -> None:
    for a in auditor.soup.find_all('a', href=True):
        text = a.get_text(strip=True).lower()
        if any(s in text for s in SUSPICIOUS_LINKS) and len(text.split()) < 3:
            auditor._add_issue(Issue(id='non-descriptive-link', wcag='2.4.4', principle='Operable', level='A', severity='warning',
                                     description='Non-descriptive link text.', impact='Medium',
                                     help='Use context-specific text like "View July report".',
                                     examples=[f'{text} → {a["href"]}']))


def check_forms(auditor: Auditor) -> None:
    controls = auditor.soup.find_all(['input', 'select', 'textarea'])
    for ctrl in controls:
        if ctrl.name in ['input'] and ctrl.get('type') in ['hidden', 'submit', 'button']:
            continue
        has_label = bool(
            ctrl.get('aria-label') or
            ctrl.parent and ctrl.parent.name == 'label' or
            auditor.soup.find('label', {'for': ctrl.get('id')})
        )
        if not has_label:
            auditor._add_issue(Issue(id='unlabeled-control', wcag='1.3.1', principle='Perceivable', level='A', severity='error',
                                     description='Form control lacks label.', impact='High',
                                     help='Use <label for="id"> or aria-label.'))


def check_tables(auditor: Auditor) -> None:
    for table in auditor.soup.find_all('table'):
        headers = table.find_all('th')
        scoped = [td for td in table.find_all('td') if td.get('scope')]
        if not headers and not scoped:
            auditor._add_issue(Issue(id='table-no-header', wcag='1.3.1', principle='Perceivable', level='AA', severity='warning',
                                     description='Data table lacks headers.', impact='Medium',
                                     help='Add <th> or scope="row/col" on <td>.'))


def check_empty_headings(auditor: Auditor) -> None:
    for h in auditor.soup.find_all(re.compile(r'^h[1-6]$')):
        text = h.get_text(strip=True)
        if not text:
            auditor._add_issue(Issue(id='empty-heading', wcag='1.3.1', principle='Perceivable', level='A', severity='error',
                                     description='Empty heading.', impact='High',
                                     help='Add text or remove heading.'))


def check_lang_consistency(auditor: Auditor) -> None:
    html_lang = auditor.soup.html.get('lang', '')
    if html_lang:
        # Simple check for lang mismatches in content (basic)
        pass  # Expandable with langdetect
