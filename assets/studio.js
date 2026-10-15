(() => {
  const $ = (selector) => document.querySelector(selector);
  const message = $("#message");
  const editor = $("#json-editor");
  const files = new Map();
  let data;

  function notice(text, type = "") {
    message.textContent = text;
    message.className = "message " + type;
  }
  function slugify(value) {
    return value.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }
  function render() {
    editor.value = JSON.stringify(data, null, 2);
    const profile = $("#profile-form");
    profile.school.value = data.school || "";
    profile.intro.value = data.intro || "";
    profile.email.value = data.contact?.email || "";
    profile.approved.checked = Boolean(data.contact?.approved);
    const gallery = $("#photo-form").gallery;
    const selected = gallery.value;
    gallery.innerHTML = (data.galleries || []).map(item => `<option value="${item.slug}">${item.title}</option>`).join("");
    if ([...gallery.options].some(option => option.value === selected)) gallery.value = selected;
  }
  function validate(candidate = data) {
    if (!candidate || typeof candidate !== "object") throw new Error("The content must be a JSON object.");
    for (const key of ["galleries", "projects", "conferences", "interests", "customPages"]) {
      if (!Array.isArray(candidate[key])) throw new Error(`${key} must be a list.`);
    }
    const slugs = [];
    for (const group of ["galleries", "projects", "conferences", "customPages"]) {
      for (const item of candidate[group]) {
        if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(item.slug || "")) throw new Error(`Invalid URL name in ${group}: ${item.slug || "(empty)"}`);
        slugs.push(group + ":" + item.slug);
        for (const photo of item.photos || []) {
          if (!photo.src || !photo.alt || !photo.title || !Number.isInteger(photo.width) || !Number.isInteger(photo.height)) throw new Error(`A photograph in ${item.title || item.name} is missing a file, title, alt text, width or height.`);
        }
      }
    }
    if (new Set(slugs).size !== slugs.length) throw new Error("A section contains duplicate URL names.");
    return true;
  }
  function download(name, blob) {
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = name;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }

  fetch("portfolio.json", {cache: "no-store"}).then(response => {
    if (!response.ok) throw new Error("Could not load portfolio.json.");
    return response.json();
  }).then(json => {
    data = json;
    data.customPages ||= [];
    render();
    notice("Current portfolio loaded. Changes are saved only when you download the file.", "success");
  }).catch(error => notice(error.message + " Build the site before opening this editor.", "error"));

  $("#profile-form").addEventListener("submit", event => {
    event.preventDefault();
    const form = event.currentTarget;
    data.school = form.school.value.trim();
    data.intro = form.intro.value.trim();
    data.contact ||= {approved:false,email:"",socials:[]};
    data.contact.email = form.email.value.trim();
    data.contact.approved = form.approved.checked;
    render();
    notice("General information updated in this editing session.", "success");
  });

  $("#photo-form").addEventListener("submit", async event => {
    event.preventDefault();
    const form = event.currentTarget;
    const file = form.file.files[0];
    if (!file) return;
    const safeBase = slugify(file.name.replace(/\.[^.]+$/, "")) || "photograph";
    const extension = (file.name.match(/\.[a-zA-Z0-9]+$/) || [".jpg"])[0].toLowerCase();
    let filename = safeBase + extension;
    let count = 2;
    while (files.has(filename)) filename = safeBase + "-" + count++ + extension;
    try {
      const bitmap = await createImageBitmap(file);
      const gallery = data.galleries.find(item => item.slug === form.gallery.value);
      gallery.photos.push({
        src: "assets/photos/" + filename,
        title: form.title.value.trim(),
        alt: form.alt.value.trim(),
        description: form.description.value.trim(),
        technical: form.technical.value.trim(),
        width: bitmap.width,
        height: bitmap.height,
        featured: form.featured.checked
      });
      bitmap.close();
      files.set(filename, file);
      render();
      form.reset();
      notice(`${filename} added. Remember to download both the content file and photographs.`, "success");
    } catch {
      notice("This browser could not read the image dimensions. Try JPEG, PNG, WebP or AVIF.", "error");
    }
  });

  $("#page-form").title.addEventListener("input", event => {
    const slug = $("#page-form").slug;
    if (!slug.dataset.edited) slug.value = slugify(event.target.value);
  });
  $("#page-form").slug.addEventListener("input", event => event.target.dataset.edited = "true");
  $("#page-form").addEventListener("submit", event => {
    event.preventDefault();
    const form = event.currentTarget;
    const slug = form.slug.value.trim();
    if (data.customPages.some(page => page.slug === slug)) return notice("That page URL name already exists.", "error");
    data.customPages.push({
      slug,
      title: form.title.value.trim(),
      description: form.description.value.trim(),
      sections: [{heading: form.heading.value.trim() || "About", body: form.body.value.trim()}]
    });
    render();
    form.reset();
    delete form.slug.dataset.edited;
    notice("New page added. It will appear under Other interests after publishing.", "success");
  });

  $("#apply-json").addEventListener("click", () => {
    try {
      const candidate = JSON.parse(editor.value);
      candidate.customPages ||= [];
      validate(candidate);
      data = candidate;
      render();
      notice("JSON changes applied.", "success");
    } catch (error) { notice(error.message, "error"); }
  });
  $("#validate").addEventListener("click", () => {
    try { validate(JSON.parse(editor.value)); notice("Content is valid and ready to download.", "success"); }
    catch (error) { notice(error.message, "error"); }
  });
  $("#download-json").addEventListener("click", () => {
    try {
      const candidate = JSON.parse(editor.value);
      candidate.customPages ||= [];
      validate(candidate);
      data = candidate;
      download("portfolio.json", new Blob([JSON.stringify(data, null, 2) + "\n"], {type:"application/json"}));
      notice("portfolio.json downloaded.", "success");
    } catch (error) { notice(error.message, "error"); }
  });
  $("#download-images").addEventListener("click", () => {
    if (!files.size) return notice("No new photographs are selected in this session.", "error");
    let delay = 0;
    for (const [name, file] of files) setTimeout(() => download(name, file), delay += 250);
    notice(`${files.size} photograph file(s) downloaded.`, "success");
  });
})();