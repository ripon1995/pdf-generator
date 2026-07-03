import re

from markupsafe import Markup, escape

# A top-level group starts with "1.", "2.", ... at the start of a line — distinct
# from sub-item markers like "(i)", "(ii)" which stay inside the same group.
_GROUP_START = re.compile(r"^\s*\d+\.\s")

# Bangladesh board/admission-exam reference tags, e.g. "[রা. বো. ১৪, ০২; ঢা. বো. ১৪]"
# or "[RUET. 07-08]" / "[KUET: 04-05]" — either the Bengali abbreviation "বো"
# ("বোর্ড"/board) or an all-caps institute code (RUET, BUET, KUET, DU, RU, ...)
# followed by a year/number, separated by ".", ":", or "-".
_REF_MARKER = re.compile(r"বো|[A-Z]{2,6}[.:\-]?\s*[০-৯0-9]")
# A run of one or more adjacent bracketed tags, optionally joined by ";"/"," —
# extraction sometimes emits multiple refs as separate brackets rather than one
# combined bracket, e.g. "[ঢা. বো. ১৪]; [RUET. 07-08]". Removing brackets one at a
# time left the connecting ";" orphaned, so the whole run is matched (and its
# joining punctuation with it) and dropped together when any bracket in it is a ref.
_BRACKET_RUN = re.compile(r"(?:\s*[;,]?\s*\[[^\[\]]*\])+[;,]?")


def _strip_ref_tags(content: str) -> str:
    def repl(m: re.Match) -> str:
        units = re.findall(r"\[[^\[\]]*\]", m.group(0))
        if any(_REF_MARKER.search(u) for u in units):
            return ""
        return m.group(0)

    return _BRACKET_RUN.sub(repl, content)


def format_content(content: str) -> Markup:
    content = _strip_ref_tags(content)
    groups: list[list[str]] = []
    for line in content.split("\n"):
        if not groups or _GROUP_START.match(line):
            groups.append([line])
        else:
            groups[-1].append(line)
    return Markup("\n").join(
        Markup('<div class="content-group">{}</div>').format(escape("\n".join(g)))
        for g in groups
    )
