# Markdown-Environments

Replicating amsthm features and syntax in Markdown so you can publish mathematical papers in HTML—because what mathematician *hasn't* tried to publish to the very reputable journal called *Their Janky Flask Personal Site That No One Will Ever See*?

This [Python-Markdown](https://github.com/Python-Markdown/markdown) extension uses LaTeX-like syntax
```
\begin{...}
...
\end{...}
```
to create environments such as captioned figures, general-purpose `<div>`s, dropdowns, and user-defined LaTeX-style theorems that can be styled with attached HTML `class`es.

## Installation

```
pip install markdown-environments
```

## Available Environments

- `\begin{captioned_figure}`: figures with captions
- `\begin{cited_blockquote}`: blockquotes with quote attribution
- User-defined environments wrapped in general-purpose `<div>`s to style to your heart's content
- User-defined environments formatted as `<details>` and `<summary>` dropdowns
- User-defined LaTeX theorem environments with customizable:
    - Theorem counters
    - Heading punctuation
    - Linkable `id`s by theorem name

## Documentation

Full documentation/API reference can be found [here](https://python-markdown-environments.readthedocs.io).

<!-- example usage -->

# Example Usage

## Backend:

```py
import markdown
from markdown_environments import ThmsExtension

input_text = ...
output_text = markdown.markdown(input_text, extensions=[
    ThmsExtension(
        div_config={
            "types": {
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
            "html_class": "md-div"
        },
        dropdown_config={
            "types": {
                "exer": {
                    "thm_type": "Exercise",
                    "html_class": "md-exer",
                    "thm_counter_incr": "0,0,1"
                },
                "pf": {
                    "thm_type": "Proof",
                    "thm_counter_incr": "0,0,0,1",
                    "thm_name_overrides_thm_heading": True
                }
            },
            "html_class": "md-dropdown",
            "summary_html_class": "md-dropdown__summary mb-0"
        },
        thm_heading_config={
            "html_class": "md-thm-heading",
            "emph_html_class": "md-thm-heading__emph"
        }
    )
])
```

## Markdown input:

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
All dropdowns initialized in `ThmsExtension()` have a default `summary` value of `thm_type`,
so using dropdowns like `pf` and `exer` here without a `summary` block is also fine.
\end{exer}
```

## HTML output (prettified):

```html
<h1>Section 1: this is theorem counter syntax from ThmsExtension()</h1>
<h2>Subsection 1.1: Bees</h2>
<p>Here we begin our study of bees.</p>



<div class="md-div md-thm">
  <p>
    <span class="md-thm-heading" id="the-bee-theorem">
      <span class="md-thm-heading__emph">Theorem 1.1.1</span> (the bee theorem)<span class="md-thm-heading__emph">.</span>
    </span>
    According to all known laws of aviation, there is no way that a bee should be able to fly.
  </p>
</div>

<details class="md-dropdown">
  <summary class="md-dropdown__summary mb-0">
    <span class="md-thm-heading">
      <span class="md-thm-heading__emph">Proof 1.1.1.1</span><span class="md-thm-heading__emph">.</span>
    </span>
  </summary>

  <div>
    <p>Its wings are too small to get its fat little body off the ground.</p>
  </div>
</details>



<div class="md-div md-thm">
  <p>
    <span class="md-thm-heading" id="hidden-thm-name-used-as-id-not-real-latex-syntax">
      <span class="md-thm-heading__emph">Theorem</span><span class="md-thm-heading__emph">.</span>
    </span>
    Bees, of course, fly anyways.
  </p>
</div>

<details class="md-dropdown">
  <summary class="md-dropdown__summary mb-0">
    <span class="md-thm-heading" id="proofs-are-configured-to-have-titles-override-the-heading">
      <span class="md-thm-heading__emph">Proofs are configured to have titles override the heading</span><span class="md-thm-heading__emph">.</span>
    </span>
  </summary>

  <div>
    <p>Because bees don't care what humans think is impossible.</p>
  </div>
</details>



<details class="md-dropdown md-exer">
  <summary class="md-dropdown__summary mb-0">
    <p>
      <span class="md-thm-heading">
        <span class="md-thm-heading__emph">Exercise 1.1.2</span><span class="md-thm-heading__emph">.</span>
      </span>
      Prove that this <code>summary</code> environment is common to all dropdown-based environments.
    </p>
  </summary>

  <div>
    <p>Solution: by reading the documentation, of course!</p>
  </div>
</details>



<details class="md-dropdown md-exer">
  <summary class="md-dropdown__summary mb-0">
    <span class="md-thm-heading">
      <span class="md-thm-heading__emph">Exercise 1.1.3</span><span class="md-thm-heading__emph">.</span>
    </span>
  </summary>

  <div>
    <p>
      All dropdowns initialized in <code>ThmsExtension()</code> have a default <code>summary</code> value of <code>thm_type</code>,
      so using dropdowns like <code>pf</code> and <code>exer</code> here without a <code>summary</code> block is also fine.
    </p>
  </div>
</details>
```

## HTML example render:

### Closed dropdowns:

![example render (closed dropdowns)](https://github.com/user-attachments/assets/d1faaf34-e703-495a-99c6-29ef98af9869)

### Open dropdowns:

![example render (open dropdowns)](https://github.com/user-attachments/assets/754bacc8-a767-4990-b6fe-c00f3cf78b6c)
