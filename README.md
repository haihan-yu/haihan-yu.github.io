# Haihan Yu's Academic Website

This website is modified from Pascal Michaillat's [Minimalist Hugo template for academic websites](https://pascalmichaillat.org), available at [github.com/pmichaillat/hugo-website](https://github.com/pmichaillat/hugo-website).

## Site icons

`static/favicon.svg` is the editable, font-independent source of the purple HY
identity. Its regular and optically adjusted 16 px monograms use polygons; the
SVG selects the smaller version at a 16 px viewport. Keep the `background`,
`monogram`, and `monogram-small` IDs when editing it.

To regenerate the ICO, PNGs, web manifest, and size/context preview:

```sh
python3 scripts/generate-icons.py
bash rebuild.sh
```

The generator requires Python 3.9+ and Pillow 10.1+ and reads the SVG geometry
directly; icon production does not need fonts or an external SVG renderer.
System fonts are used only for the preview labels. The default preview is
`../output/favicon-preview.png`; override it with `--preview /path/to/preview.png`.
The preview's 16, 32, and 48 px samples are actual pixels when viewed at 100%.

The ICO contains individually rendered 16, 32, and 48 px images, including the
small-size correction. Browser icons have transparent rounded corners; Apple
and Android icons have opaque, square backgrounds for system presentation.
The web manifest uses ordinary browser display and adds no offline behavior.

When changing the artwork, update `params.assets.icon_version` in `config.yml`
before regeneration. This version is shared by the HTML and manifest icon URLs.
If changing the purple, also update both color settings in `config.yml`.
Commit the generated root assets and HTML together with their sources:
GitHub Pages publishes the repository directly, and `rebuild.sh` synchronizes
the Hugo output into the repository root.
