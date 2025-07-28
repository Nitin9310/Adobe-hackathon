# Challenge 1A – PDF Heading Extractor

## How It Works
This script processes all PDFs in `/app/input` and extracts the title and headings (H1, H2, H3) using font size logic. It saves the result as JSON in `/app/output`.

## Build Instructions
```bash
docker build --platform linux/amd64 -t pdf-processor .
