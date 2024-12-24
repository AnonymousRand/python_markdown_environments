import markdown

from markdown_environments.thms import *


def test_counter():
    fixture = (
        "Section {{1}}"
        "Subsection {{0,1,0}} (displays as many sections as given)"
        "Lemma {{0,0,0,1}}"
        "Theorem {{0,0,1}} (the fourth counter section is reset here). Let \(s\) be a lorem ipsum."
        "Reevaluating Life Choices {{0,0,0,3}}"
        "What even is this {{1,2,0,3,9}} (first counter section resets next ones, and so on)"
    )

    print(markdown.markdown(fixture, extensions=[ThmsExtension()]))
