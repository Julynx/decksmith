# ROADMAP.md

## Essential features

### Entire Application
- [x] Transform into a cli application with "pydeck init", "pydeck build", etc.
- [x] Basic tests
- [x] Basic error handling in cli with error messages
- [x] Create a proper documentation with examples
- [ ] Improve the default template
- [ ] Validation of fields and values
- [ ] Publish an initial version to GitHub and PyPI

### Card Builder
- [x] Image filters: crop-top / bottom / left / right / box, resize
- [x] Add a new type "shape" with fill and stroke
- [x] Verify support for transparent images
- [x] Verify support for symbols and special characters, such as japanese characters
- [x] Font variants (Bold, Semibold...)

### Deck Builder
- [x] Mantain type for macros like %colname% (e.g. size="%size%" should be an int, cannot use str.replace)

### Export Module
- [x] Implement export to PDF with real page size using ReportLab
- [x] Fix layout issues with rotated images

## Naming
- [ ] Text:
      "spacing"     -> "line_spacing"
      "width"       -> "max_width"
      "stroke_fill" -> "stroke_color"

## Nice to have features
- [x] As cards are independent, implement concurrent processing of cards
- [ ] Extensive logging
- [ ] More macros to position elements to the center of the canvas for example
- [ ] Define different json schemas depending on the index of the card or other properties (consider if this is really needed)
