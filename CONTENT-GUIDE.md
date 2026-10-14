# Editing content

Edit content/portfolio.json in a text editor. Keep valid JSON and run python3 build.py after each edit. The build rejects missing assets and invalid image records.

## Photographs

Create assets/photos/ and add your images there. Add a record to the relevant gallery's photos array. Example, using your own real filenames:

    {
      "src": "assets/photos/photo-1200.webp",
      "full": "assets/photos/photo-2200.webp",
      "title": "Your title",
      "alt": "Describe the subject and scene",
      "width": 1200,
      "height": 800,
      "description": "Your account of this photograph.",
      "technical": "Optional camera, lens, film or exposure notes",
      "featured": true,
      "variants": [
        {"src": "assets/photos/photo-600.webp", "width": 600},
        {"src": "assets/photos/photo-1200.webp", "width": 1200}
      ]
    }

Use the actual dimensions of src. Variants must use the same composition and ratio. Optional fields: full, description, technical, featured and variants. Omit optional fields when unnecessary. Referenced files must exist.

The first featured photograph becomes the homepage image. Without a featured record, the first available photo is used. A gallery's first photo becomes its cover. Reorder records to change the sequence.

Click a photo or press Enter/Space on its button to open the viewer. Arrow keys and Previous/Next change the photograph. Escape closes the viewer and restores focus.

Project and conference photos use the same record format.

## Projects

Duplicate an existing project in projects, give the copy a unique lowercase slug and replace the text. Change status to Completed only after you confirm completion.

Detail fields accept:

    "specs": [{"label": "Controller", "value": "Your confirmed component"}],
    "challenges": ["Your actual problem and attempted solution."],
    "progress": [{"date": "2026-10-14", "text": "Your actual development update."}],
    "documents": [{"title": "Build notes", "path": "assets/documents/build-notes.pdf"}],
    "photos": [],
    "github": ""

GitHub URLs must use HTTPS. Empty links produce no button. Documents must exist locally under assets/.

## Model UN

Edit conferences. Dates are empty because none were supplied. Add actual agenda items to topics, your reflection to reflection and resolutions to documents. The four awards use your brief. The list preserves the given order rather than claiming chronological order.

## Academics and interests

academics.subjects lists areas of interest, not verified subject enrolment.
academics.projects uses records with title and text.
academics.achievements contains confirmed statements.
academics.aspirations contains your university plans.
interests uses title and text records. Add or remove entries as your activities change.

## Contact

Email appears only when contact.approved is true and contact.email contains a valid address. Approved social links use:

    {"label": "Profile name", "url": "https://your-approved-profile"}

There is no nonfunctional form or invented address.

## Biography and appearance

Longer biography and introductory text are in the named functions in build.py. Colours, fonts, spacing and breakpoints live in assets/style.css.

