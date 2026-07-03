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

# The exercise heading (e.g. "অনুশীলনী-10.5") belongs only in the page header
# (`preview.html`'s `.doc-header-chapter`) — extraction sometimes echoes it inline
# in the body text too, so strip that occurrence from the content. Leading
# whitespace/newline is consumed so a label on its own line doesn't leave a blank
# line behind; trailing whitespace is left alone to avoid eating the following word.
_EXERCISE_LABEL = re.compile(r"\s*অনুশীলনী\s*[-–—]?\s*[০-৯0-9]+(?:\.[০-৯0-9]+)?")


def _strip_ref_tags(content: str) -> str:
    def repl(m: re.Match) -> str:
        units = re.findall(r"\[[^\[\]]*\]", m.group(0))
        if any(_REF_MARKER.search(u) for u in units):
            return ""
        return m.group(0)

    return _BRACKET_RUN.sub(repl, content)


def format_content(content: str) -> Markup:
    content = _strip_ref_tags(content)
    content = _EXERCISE_LABEL.sub("", content)
    groups: list[list[str]] = []
    for line in content.split("\n"):
        if not groups or _GROUP_START.match(line):
            groups.append([line])
        else:
            groups[-1].append(line)
    # A group left entirely blank (e.g. a stripped label that had its own line)
    # would otherwise pick up the "between groups" 9mm top margin as if it were
    # real content — drop it so that spacing only applies between actual groups.
    joined = ["\n".join(g) for g in groups]
    joined = [g for g in joined if g.strip()]
    return Markup("\n").join(
        Markup('<div class="content-group">{}</div>').format(escape(g)) for g in joined
    )
