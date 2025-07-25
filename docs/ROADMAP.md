# ROADMAP.md

## Essential features

### Entire Application
- [x] Transform into a cli application with "pydeck init", "pydeck build", etc.
- [ ] Proper error handling and extensive logging
- [ ] Create a proper documentation with examples
- [ ] Publish an initial version to GitHub and PyPI

### Card Builder
- [x] Image filters: crop-top / bottom / left / right / square, resize
- [x] Add a new type "shape" with fill and stroke
- [ ] Verify support for transparent images
- [ ] Verify support for symbols and special characters, such as japanese characters

### Deck Builder
- [x] Mantain type for macros like %colname% (e.g. size="%size%" should be an int, cannot use str.replace)

### Export Module
- [ ] Implement export to PDF with real page size using ReportLab

## Nice to have features
- [x] As cards are independent, implement concurrent processing of cards
- [ ] More macros to position elements to the center of the canvas for example
- [ ] Define different json schemas depending on the index of the card or other properties (consider if this is really needed)
