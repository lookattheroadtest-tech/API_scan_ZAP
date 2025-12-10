name: ZAP Custom API Scan

on:
  workflow_dispatch:

jobs:
  zap-custom-api:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Fix permissions
      run: chmod -R 777 .

    # Build merged request file dynamically
    - name: Merge Authorization into each request
      run: |
        echo "" > merged-requests.txt
        while IFS= read -r line; do
          if echo "$line" | grep -q "^GET\|^POST"; then
            # New request block → add method URL + auth header
            echo "$line" >> merged-requests.txt
            cat auth-header.txt >> merged-requests.txt
          else
            echo "$line" >> merged-requests.txt
          fi
        done < api-requests.txt

    - name: Run ZAP Custom Scan
      run: |
        docker run --rm \
          -v "$(pwd):/zap/wrk" \
          ghcr.io/zaproxy/zaproxy:stable \
          zap-full-scan.py \
            -t https://demo.testfire.net \
            -z "script.console.commands=importUrls('/zap/wrk/merged-requests.txt')" \
            -r zap-report.html \
            -x zap-report.xml \
            -I \
            -d

    - name: Upload HTML Report
      uses: actions/upload-artifact@v4
      with:
        name: zap-html-report
        path: zap-report.html

    - name: Upload XML Report
      uses: actions/upload-artifact@v4
      with:
        name: zap-xml-report
        path: zap-report.xml
