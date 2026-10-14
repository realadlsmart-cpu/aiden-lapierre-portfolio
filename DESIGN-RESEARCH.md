# Design research

Research date: 14 October 2026.

The original ZIP held one HTML page. Issues found: dark panels, repeated three-card grids, gradient placeholders, oversized hero typography, generic promotional copy, inconsistent surname capitalisation and an example email button.

## Six references

The following sites were retrieved through web research. Desktop browser snapshots were also inspected. Five yielded visible design references. Matt Stuart's DOM loaded but its screenshot was blank, so that entry is structural evidence only.

### Alec Soth
https://alecsoth.com/photography/projects

Observed: a direct project-title index, bold sans-serif typography, a white page, left alignment and a small navigation set. Large gaps separate the text entries. The project index avoids image-card decoration.

Adopted: a direct technical-project index with actual titles and stage information. Our type and page composition differ.

### David Chipperfield Architects
https://davidchipperfield.com/projects

Observed: modest sans-serif labels, plain navigation, grid/list controls, image ratios that vary by project and generous open space. Captions sit beneath images without enclosing cards.

Adopted: separate index and detail pages, captions outside the visual, native image ratios, metadata as a narrow factual column. No copy of its grid or controls.

### IGNANT
https://www.ignant.com/

Observed: a serif editorial lead paired with a large image, small category navigation, secondary article groups and ample margins. The captured lead title was partway through an animation.

Adopted: a photograph-led homepage paired with contextual text, serif headings and small category labels. Omitted animated headings and newsletter overlays.

### Apartamento
https://www.apartamentomagazine.com/

Observed: a publication masthead, compact navigation, a large media feature, issue/context labels and separate story sections. Its commercial navigation is broader than this portfolio needs.

Adopted: an identifiable masthead and quiet context labels. Omitted video autoplay, commerce and promotional banners.

### The Gentlewoman
https://thegentlewoman.co.uk/

Observed: a strong typographic masthead, a dominant portrait cover, small issue notation and concise navigation. The image carries most of the visual identity.

Adopted: photography as the primary visual surface with typography and captions around it. The website uses Aiden's name at a smaller scale suited to a student portfolio.

### Matt Stuart
https://www.mattstuart.com/

DOM evidence: photo-series links, commissioned work, distinct film and biography/contact destinations, and native Previous/Next controls. The screenshot did not render the page design, so no typography or spacing claims are made from it.

Adopted: named collections and an image-viewer experience separate from biography and other work.

## Mobile research limits

Reference desktop layouts were inspected in the browser. The available browser API did not expose viewport resizing. Reference mobile layouts have not been visually verified. The redesign uses its own mobile rules rather than claiming to reproduce those references: single-column galleries, stacked metadata, a two-column menu and at least 44-pixel controls.

## Generic AI-design research

Sources:
https://www.925studios.co/blog/ai-slop-web-design-guide
https://medium.com/@dollyborade07/ai-design-slop-why-ai-keeps-designing-the-same-dashboard-cards-gradients-and-rounded-corners-26d8e4779a86

These are designer commentary, not a reliable way to establish whether a website was made with AI. Recurring criticisms include default gradients, excessive rounding, repeated cards, generic copy and unnecessary animation. Numerical claims in these articles were not adopted.

Our response: make choices from Aiden's actual content. Photography uses staggered covers, conferences use factual records, projects use an index plus documentation, academics uses a learning record and About uses prose. No gradients, glowing surfaces, glass effects, decorative icons or simulated metrics.

## Visual identity

Background #f6f5f1, text #232620, muted text #64675f, restrained green #42513e. Georgia headings paired with a Helvetica/Arial stack. These system fonts avoid third-party font requests and keep the build portable. Exact rendering varies by operating system.

Thin rules establish alignment. The desktop layout has measured margins, asymmetry and multiple scales. Mobile collapses content in reading order. Photography keeps native ratios rather than forced crops. Motion is limited to browser-native scrolling and direct control feedback, with reduced-motion support.

## Architecture decision

A static Python generator was chosen over Astro because this portfolio needs ordinary pages, local content and one image viewer. Python's standard library produces reusable templates without package installation. Output is plain HTML/CSS/JavaScript, usable on static hosts or directly from disk.

## Content integrity

No external reference photographs were copied into the website. No achievements, grades or technical specifications were invented. Only the user's four supplied awards are displayed. No project is labelled completed without confirmation. Missing material has clearly labelled editable slots.

