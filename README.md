# Python-Markdown-Environments

Replicating `amsthm` features and syntax in Markdown so you can publish mathematical papers in HTML—because what mathematician *hasn't* tried to publish to the very reputable journal called *Their Janky Flask Personal Site That No One Will Ever See*?

This Python-Markdown extension uses LaTeX-like syntax
```
\begin{...}
...
\end{...}
```
to create enviroments such as captioned figures, general-purpose `<div>`s, dropdowns, and user-defined LaTeX-style theorems that can be styled with attached HTML `class`es.

## Installation

```
pip install markdown-environments
```

## Available Environments

- `\begin{captioned_figure}`: rigures with captions
- `\begin{cited_blockquote}`: blockquotes with quote attribution
- User-defined environments wrapped in general-purpose `<div>`s to style to your heart's content
- User-defined environments formatted as `<details>` and `<summary>` dropdowns
- User-defined LaTeX theorem environments with customizable:
    - Theorem counters
    - Heading punctuation
    - Linkable `id`s by theorem name

## Example Usage

### Backend:

```py
import markdown
from markdown_environments.thms import ThmsExtension

input_text = ...
output_text = markdown.markdown(input_text, extensions=[
    ThmsExtension(
        div_html_class="md-div",
        div_types={
            "thm": {
                "thm_type": "Theorem",
                "html_class": "md-thm",
                "thm_counter_incr": "0,0,1"
            },
            r"thm\\\*": {
                "thm_type": "Theorem",
                "html_class": "md-thm"
            }
        },
        dropdown_html_class="md-dropdown",
        dropdown_summary_html_class="md-dropdown__summary mb-0",
        dropdown_types={
            "exer": {
                "thm_type": "Exercise",
                "html_class": "md-exer",
                "thm_counter_incr": "0,0,1",
                "thm_heading_punct": ":",
                "use_punct_if_nothing_after": False
            },
            "pf": {
                "thm_type": "Proof",
                "thm_counter_incr": "0,0,0,1",
                "thm_name_overrides_thm_heading": True
            }
        },
        thm_heading_html_class="md-thm-heading",
        thm_type_html_class="md-thm-heading__thm-type"
    )
])
```

### Markdown input:

```md
# Section {{1}}: this is theorem counter syntax from ThmsExtension()

## Subsection {{0,1}}: Bees

Here we begin our study of bees.

\begin{thm}[the bee theorem]
According to all known laws of aviation, there is no way that a bee should be able to fly.
\end{thm}

\begin{pf}
Its wings are too small to get its fat little body off the ground.
\end{pf}

\begin{thm\*}{hidden thm name used as `id`; not real LaTeX syntax}
Bees, of course, fly anyways.
\end{thm\*}

\begin{pf}[Proofs are configured to have titles override the heading]{hidden names are useless when there's already a name}
Because bees don't care what humans think is impossible.
\end{pf}

\begin{exer}

\begin{summary}
Prove that this `summary` environment is common to all dropdown-based environments.
\end{summary}

Solution: by reading the documentation, of course!
\end{exer}

\begin{exer}
All dropdowns initialized in `ThmsExtension()` have a default `summary` value of `thm_type`, so using dropdowns like `pf` and `exer` here without a `summary` block is also fine.

Also, since there's no extra summary after the theorem heading of "Exercise", there is no punctuation (the colon; default punctuation is a period) since we set `"use_punct_if_nothing_after": False`.
\end{exer}
```

### HTML output (prettified):

```html
<h1>Section 1: this is theorem counter syntax from ThmsExtension()</h1>
<h2>Subsection 1.1: Bees</h2>

<p>Here we begin our study of bees.</p>

<div class="md-div md-thm">
  <p><span class="md-thm-heading" id="the-bee-theorem"><span class="md-thm-heading__thm-type">Theorem 1.1.1</span> (the bee theorem)</span>. According to all known laws of aviation, there is no way that a bee should be able to fly.</p>
</div>

<details class="md-dropdown">
  <summary class="md-dropdown__summary mb-0">
    <span class="md-thm-heading"><span class="md-thm-heading__thm-type">Proof 1.1.1.1</span></span>.
  </summary>
  <div>
    <p>Its wings are too small to get its fat little body off the ground.</p>
  </div>
</details>

<div class="md-div md-thm">
  <p><span class="md-thm-heading" id="hidden-thm-name-used-as-klzzwxh0011-not-real-latex-syntax"><span class="md-thm-heading__thm-type">Theorem</span></span>. Bees, of course, fly anyways.</p>
</div>

<details class="md-dropdown">
  <summary class="md-dropdown__summary mb-0">
    <span class="md-thm-heading" id="proofs-are-configured-to-have-titles-override-the-heading"><span class="md-thm-heading__thm-type">Proofs are configured to have titles override the heading</span></span>.
  </summary>
  <div>
    <p>Because bees don't care what humans think is impossible.</p>
  </div>
</details>

<details class="md-dropdown md-exer">
  <summary class="md-dropdown__summary mb-0">
    <p><span class="md-thm-heading"><span class="md-thm-heading__thm-type">Exercise 1.1.2</span></span>: Prove that this <code>summary</code> environment is common to all dropdown-based environments.</p>
  </summary>
  <div>
    <p>Solution: by reading the documentation, of course!</p>
  </div>
</details>

<details class="md-dropdown md-exer">
  <summary class="md-dropdown__summary mb-0">
    <span class="md-thm-heading"><span class="md-thm-heading__thm-type">Exercise 1.1.3</span></span>
  </summary>
  <div>
    <p>All dropdowns initialized in <code>ThmsExtension()</code> have a default <code>summary</code> value of <code>thm_type</code>, so using dropdowns like <code>pf</code> and <code>exer</code> here without a <code>summary</code> block is also fine.</p>
    <p>Also, since there's no extra summary after the theorem heading of "Exercise", there is no punctuation (the colon; default punctuation is a period) since we set <code>"use_punct_if_nothing_after": False</code>.</p>
  </div>
</details>
```

### HTML render (example from my site):

<img src="https://github.com/user-attachments/assets/6ed34a55-ba7f-48c0-9c82-10efd7cb53d2" alt="example_render_closed_dropdowns" width=67% style="display: inline;">
<img src="https://github.com/user-attachments/assets/92410977-a048-4e4d-b425-84b550d6699b" alt="example_render_open_dropdowns" width=67% style="display: inline;">

## Further Reading

Full documentation and detailed usage examples can be found [here](https://www.youtube.com/watch?v=xvFZjo5PgG0).

## Contributing

I don't expect this project to be huge, so feel free to drop an issue or pull request on [GitHub](https://github.com/AnonymousRand/python-markdown-environments) to report bugs or suggest features.
