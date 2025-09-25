# Toronto Business Lead Generator 🚀

A web-based mini-app that acts as a "lead generation marketing bot" for Toronto businesses that need delivery or international shipping services.

## Features

- **Minimal UI**: Fast-loading, clean interface built with Streamlit
- **Multiple Data Sources**: Yelp Fusion API and OpenStreetMap/Overpass API
- **Smart Categorization**: Automatic detection of delivery and shipping potential
- **AI Analysis**: Optional OpenAI-powered analysis for business insights
- **Export Functionality**: CSV export for lead management
- **Caching**: Request caching for improved performance
- **Error Handling**: Robust error handling with user-friendly messages

## Quick Start

### Option 1: Demo Version (Recommended for Testing)

The demo version works immediately without any setup:

```bash
streamlit run app_minimal.py
```

This version includes:
- ✅ Sample business data
- ✅ All UI features
- ✅ CSV export
- ✅ Business categorization
- ❌ Real API data (Yelp/OSM)
- ❌ AI analysis

### Option 2: Full Version (Requires Setup)

For the full version with real data sources and AI analysis:

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp env_example.txt .env
```

Edit `.env` and add your API keys:

```env
# Yelp Fusion API Key (required for Yelp data source)
YELP_API_KEY=your_yelp_api_key_here

# OpenAI API Key (optional, for AI analysis)
OPENAI_API_KEY=your_openai_api_key_here

# App Configuration
TORONTO_LAT=43.6532
TORONTO_LON=-79.3832
TORONTO_RADIUS=50000
```

#### 3. Get API Keys

##### Yelp Fusion API (Required for Yelp data)
1. Go to [Yelp Fusion API](https://www.yelp.com/developers/documentation/v3/authentication)
2. Create a Yelp account
3. Create a new app
4. Copy your API key

##### OpenAI API (Optional for AI analysis)
1. Go to [OpenAI API](https://platform.openai.com/api-keys)
2. Create an account
3. Generate a new API key

#### 4. Run the Full Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### Search Filters

- **Search Term**: Enter keywords to search for specific business types
- **Business Categories**: Select from predefined categories (Restaurant, Grocery, Pharmacy, etc.)
- **Number of Results**: Use the slider to control how many businesses to return
- **Data Source**: Choose between Yelp (requires API key) or OpenStreetMap (free)
- **AI Analysis**: Enable AI-powered analysis for delivery/shipping potential

### Results

The app displays businesses in a table with the following information:

- **Name**: Business name
- **Category**: Business category
- **Phone**: Contact phone number
- **Address**: Business address
- **URL**: Website URL
- **Rating**: Average rating (Yelp only)
- **Review Count**: Number of reviews (Yelp only)
- **Flags**: 
  - `likely_delivery`: Business likely needs delivery services
  - `potential_worldwide_shipping`: Business has potential for international shipping
  - `is_logistics`: Business is a logistics/freight service provider

### Export

Click "Export to CSV" to download the results for further analysis or lead management.

## Data Sources

### Yelp Fusion API
- **Pros**: Rich data with ratings, reviews, and detailed business information
- **Cons**: Requires API key and has rate limits
- **Best for**: High-quality business data with ratings and reviews

### OpenStreetMap/Overpass
- **Pros**: Free, no API key required, comprehensive coverage
- **Cons**: Limited business details, no ratings/reviews
- **Best for**: Basic business information when Yelp is not available

## Business Categorization

The app uses rule-based categorization to detect:

1. **Delivery Potential**: Based on business category and keywords
2. **Shipping Potential**: Based on business type and e-commerce indicators
3. **Logistics Services**: Based on business name and category keywords

### AI Analysis (Optional)

When enabled, the app uses OpenAI's GPT-3.5-turbo to analyze businesses for:

- Delivery service needs
- International shipping potential
- Logistics service provider identification
- Confidence scores and reasoning

## Project Structure

```
market_place/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── env_example.txt       # Environment variables example
├── README.md             # This file
└── src/
    ├── __init__.py
    ├── data_sources.py   # Yelp and OSM data sources
    ├── categorization.py # Business categorization logic
    ├── ai_analysis.py    # AI-powered analysis
    └── utils.py          # Utility functions
```

## Configuration

### Environment Variables

- `YELP_API_KEY`: Yelp Fusion API key (required for Yelp data)
- `OPENAI_API_KEY`: OpenAI API key (optional for AI analysis)
- `TORONTO_LAT`: Toronto latitude (default: 43.6532)
- `TORONTO_LON`: Toronto longitude (default: -79.3832)
- `TORONTO_RADIUS`: Search radius in meters (default: 50000)

### Customization

You can modify the search radius, add new business categories, or adjust the categorization rules by editing the respective files in the `src/` directory.

## Error Handling

The app includes comprehensive error handling for:

- Missing API keys
- Network timeouts
- Rate limiting
- Invalid responses
- Data processing errors

## Performance

- **Caching**: 1-hour TTL cache for API requests
- **Rate Limiting**: Built-in delays to respect API limits
- **Lazy Loading**: Data loaded only when needed
- **Minimal UI**: Fast initial load time

## Troubleshooting

### Common Issues

1. **"Yelp API key not found"**: Make sure you've set the `YELP_API_KEY` environment variable
2. **"No businesses found"**: Try different search terms or categories
3. **"AI analysis not working"**: Check your `OPENAI_API_KEY` and ensure you have credits
4. **Slow loading**: The app caches results, so subsequent searches should be faster

### Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify your API keys are correct
3. Ensure you have an internet connection
4. Check if the APIs are experiencing downtime

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue on the project repository.
