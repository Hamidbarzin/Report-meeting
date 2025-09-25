# Toronto B2B Lead Generator 🚀

A modern web application for generating B2B leads in Toronto, focusing on importers, distributors, wholesalers, suppliers, fulfillment/3PL, logistics, and e-commerce companies.

## Features

- **Modern UI**: Clean, professional interface with FedEx-style design
- **Google Places API**: Real business data with phone numbers and websites
- **Email Enrichment**: Hunter.io API + website scraping for verified emails
- **Smart Categorization**: Automatic detection of delivery and shipping potential
- **Multiple Views**: Card view and table view for results
- **Export Functionality**: CSV export with all business details
- **Rate Limiting**: Built-in protection against API limits
- **Error Handling**: Robust error handling with user-friendly messages

## Quick Start

### Prerequisites

1. **Google Cloud Console**:
   - Enable Places API and Geocoding API
   - Create API key with appropriate restrictions

2. **Hunter.io API** (Optional):
   - Sign up at [Hunter.io](https://hunter.io)
   - Get your API key

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Hamidbarzin/Report-meeting.git
cd Report-meeting
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
export HUNTER_API_KEY="your_hunter_api_key_here"  # Optional
```

4. **Run the application**:
```bash
streamlit run app_final_b2b.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Search Filters

- **Keywords**: Enter specific business types (e.g., "electronics", "auto parts")
- **Business Focus**: Select from predefined B2B categories
- **Location**: Search in specific areas (default: Toronto, ON)
- **Max Results**: Control the number of businesses returned
- **Email Enrichment**: Enable Hunter.io and website scraping for emails

### Results Display

The app shows businesses with:

- **Name & Category**: Business information
- **Contact Details**: Phone, email, website, address
- **Rating & Reviews**: Google Places ratings
- **Flags**: Delivery, worldwide shipping, logistics indicators
- **Source Tracking**: Email source (Hunter.io vs Scraping)

### Export

Click "Export to CSV" to download all results with complete contact information.

## API Integration

### Google Places API
- **Text Search**: Find businesses by keywords
- **Place Details**: Get phone, website, and address
- **Geocoding**: Location-based searches

### Hunter.io API
- **Domain Search**: Find verified emails for business domains
- **Contact Roles**: Identify contact positions
- **Rate Limiting**: Built-in delays to respect limits

### Website Scraping
- **Fallback Method**: When Hunter.io quota is reached
- **Email Patterns**: Multiple regex patterns for email detection
- **Contact Pages**: Scans common contact page URLs

## Project Structure

```
market_place/
├── app_final_b2b.py        # Main application (recommended)
├── app_modern_hunter.py    # Alternative version
├── app_hunter_enriched.py  # Hunter.io focused version
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/                   # Source modules
    ├── data_sources.py    # API integrations
    ├── categorization.py  # Business classification
    └── utils.py          # Utility functions
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Google Places API key (required)
- `HUNTER_API_KEY`: Hunter.io API key (optional)

### Customization

- Modify business focus categories in the UI
- Adjust email patterns in scraping functions
- Customize flag detection logic
- Change UI styling and colors

## Performance

- **Rate Limiting**: 1.5-second delays between API calls
- **Progress Indicators**: Real-time progress bars
- **Caching**: Efficient data processing
- **Error Recovery**: Graceful handling of API failures

## Troubleshooting

### Common Issues

1. **"No businesses found"**: Try different keywords or business focus types
2. **"Rate limit reached"**: Wait a few minutes before retrying
3. **"Email enrichment disabled"**: Enable it in Advanced Options
4. **"API key missing"**: Set your Google API key in environment

### Getting Help

1. Check the console output for detailed error messages
2. Verify your API keys are correct and have proper permissions
3. Ensure you have an internet connection
4. Check API quotas and billing status

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue on the [GitHub repository](https://github.com/Hamidbarzin/Report-meeting).
