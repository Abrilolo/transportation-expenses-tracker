# Transportation Expenses Extractor

## Objective

The objective of this project is to extract transportation expenses and transaction history from a physical Suica or Pasmo card using an NFC reader. The extracted data is organized into a persistent JSON database, exported to a clean Excel spreadsheet for reimbursement or accounting purposes, and visualized in a local web dashboard. This project also serves to practice Python development, hardware integration via NFC, and technical documentation.

## Hardware

- **NFC Reader**: SONY RC-S330 or RC-S380 (USB NFC Reader).
- **Target OS**: Windows.
- **Card Type**: Physical FeliCa-based smart cards (Suica, Pasmo, etc.).

## Software Requirements

- **Programming Language**: Python 3
- **Python Packages** (defined in `requirements.txt`):
  - `nfcpy`: Core library to communicate with the NFC reader.
  - `openpyxl`: Used to generate and format the Excel output file.
  - `pykakasi`: Converts Japanese Kanji/Kana station names into Romaji.
- **External Tools**:
  - **Zadig**: Required on Windows to replace the proprietary SONY driver with the generic WinUSB driver so `nfcpy` can recognize the device.

## Setup

1. **Hardware Driver Preparation**: 
   - Plug in the SONY NFC reader.
   - Open Zadig, list all devices, and find the NFC reader.
   - Replace the driver with **WinUSB**.
2. **Python Environment**:
   - Create a virtual environment and install dependencies:
     ```powershell
     python -m pip install -r requirements.txt
     ```
3. **Data Dependency**:
   - Ensure the station mapping table `ekicode.csv` is located in `data/ekicode.csv` to successfully translate raw hexadecimal station codes into readable names.

## How It Works

The main entry point is `read.py`. The execution flow is as follows:

1. **Reader Initialization**: The program uses `nfcpy` to open the USB connection to the NFC reader and waits for a card to be placed.
2. **Data Extraction**: Once a FeliCa card is detected, it queries the specific service code for transaction history and reads up to 20 records (the physical limit of the card).
3. **Data Parsing**: Each 16-byte record is parsed byte-by-byte into a structured `SuicaHistoryRecord` object. This includes parsing dates, processing codes (e.g., train, bus, vending machine), and balances.
4. **Enrichment**: Station codes are looked up using `ekicode.csv`. The retrieved Japanese names are then romanized using `pykakasi`. Balance changes (charges and expenses) are calculated by comparing consecutive records.
5. **Persistence & Deduplication**: The new records are merged with the existing history in `output/transactions.json`. Deduplication prevents recording the same transaction multiple times across different scans.
6. **Exporting**: The full merged dataset is exported to `output/transactions.xlsx` using `openpyxl`.
7. **Dashboard Integration**: Finally, `dashboard/data.js` is generated containing a JavaScript payload of the data, which the dashboard consumes to update its UI.

## How to Read the SUICA

The SUICA card uses the FeliCa standard (NFC Type-F, or `Type3Tag` in `nfcpy`). The reading process involves targeting the correct service code and extracting data blocks.

- **Service Code**: The history records are stored under Service Code `0x090F`.
- **Block Reads**: The reader iterates through blocks `0` to `19`. Each read command returns a 16-byte raw block.
- **Byte Structure**:
  - `Byte 0`: Terminal code (type of machine used).
  - `Byte 1`: Process code (type of operation: rail, bus, shopping, etc.).
  - `Bytes 4-5`: Date, packed in bits (7 bits for year from 2000, 4 bits for month, 5 bits for day).
  - `Bytes 6-7`: Entry station code.
  - `Bytes 8-9`: Exit station code.
  - `Bytes 10-11`: Balance (Little-endian).
  - `Bytes 12-14`: Transaction sequence number (Big-endian).
  - `Byte 15`: Region code for the entry and exit stations.

## Output Files

- **`output/transactions.json`**: A cumulative, deduplicated database of all scanned records. Scanning regularly prevents data loss when old records fall off the 20-record limit on the physical card.
- **`output/transactions.xlsx`**: An automatically formatted Excel sheet containing the human-readable transaction history, useful for expense claims.
- **`dashboard/data.js`**: An auto-generated JavaScript file that injects the latest JSON data directly into the dashboard.

## Dashboard

The project includes a lightweight, static web dashboard built with HTML, CSS, and Vanilla JavaScript. It visualizes the latest transaction data, balances, and trends.

To view the dashboard, run a local web server:
```powershell
python -m http.server 4173 --bind 127.0.0.1 --directory dashboard
```
Then, navigate to `http://127.0.0.1:4173/` in your browser. The dashboard updates automatically on refresh after a new successful card scan.

## Known Limitations

- **Card Storage Limit**: Physical Suica/Pasmo cards only retain the last 20 transactions. If the user makes more than 20 transactions between scans, the oldest records are permanently lost.
- **Driver Friction**: The requirement to use Zadig on Windows to swap drivers can conflict with official Sony software, making the reader temporarily unusable for other official applications.
- **Station Data Completeness**: The `ekicode.csv` mapping relies on static data. Newly constructed stations or specific bus routes might display as raw hexadecimal codes until the file is updated.

## Future Work

- **Automated Station Updates**: Fetch the latest station codes dynamically from an online API or repository.
- **Mobile Suica Support**: Enhance parsing capabilities to read and interpret data from Mobile Suica/Pasmo via smartphones.
- **Cloud Database Integration**: Migrate from local JSON storage to a cloud-based database (e.g., PostgreSQL, Firebase) for better synchronization across multiple devices.
- **Non-Transportation Categorization**: Improve the classification of vending machine and retail purchases to distinguish them from standard travel expenses.
