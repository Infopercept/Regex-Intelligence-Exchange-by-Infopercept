# Web Interface User Guide

## Overview

The Regex Intelligence Exchange web interface provides a user-friendly way to explore, search, and analyze the comprehensive database of technology fingerprinting patterns. This guide will help you navigate and use all available features.

## Getting Started

### Accessing the Interface

The web interface is available at `http://localhost:5000` when running locally. In production environments, it will be accessible through your configured domain.

### Navigation

The interface features a responsive navigation bar at the top with the following sections:

- **Dashboard** - Overview of the pattern database
- **Search** - Advanced search functionality
- **Analytics** - Data visualizations and statistics
- **API Docs** - Link to API documentation

## Dashboard

The dashboard provides a comprehensive overview of the pattern database.

### Key Metrics

- **Total Patterns** - The total number of patterns in the database
- **Categories** - Number of different technology categories
- **Vendors** - Number of technology vendors covered

### Category Distribution

A visual representation of how patterns are distributed across different categories, showing the top categories with the most patterns.

### Quick Search

A convenient search bar that allows you to quickly find patterns by vendor, product, or category.

## Search

The search page provides advanced search functionality with filtering options.

### Search Filters

- **Search Query** - Enter keywords to search across vendor names, product names, and categories
- **Category** - Filter results by specific technology category
- **Vendor** - Filter results by specific vendor

### Search Results

Search results are displayed in a list format with the following information for each pattern:

- Vendor and product name
- Number of patterns for this technology
- Category and subcategory tags
- Vendor and product IDs

### Pagination

Search results are paginated with 20 items per page. Use the pagination controls at the bottom to navigate between pages.

## Pattern Details

Clicking on any pattern in the search results or quick search will take you to the pattern details page.

### Pattern Information

This section displays core information about the pattern:

- Vendor name and ID
- Product name and ID
- Category and subcategory
- Metadata including author, creation date, and source

### Pattern Details

This section shows the actual regex patterns used for fingerprinting:

- **All Versions Patterns** - Patterns that apply to all versions of the technology
- **Version-Specific Patterns** - Patterns that apply to specific version ranges

For each pattern, you can see:

- Pattern name
- Actual regex pattern
- Priority and confidence levels
- Version group information
- Additional metadata

### Test Pattern

Each pattern details page includes a "Test Pattern" button that allows you to test the pattern against custom input text:

1. Click the "Test Pattern" button
2. Enter text in the input field
3. Click "Run Test"
4. View the results showing any matches found

## Analytics

The analytics page provides visualizations and statistics about the pattern database.

### Summary Cards

- Total patterns in the database
- Number of categories
- Number of vendors

### Charts

- **Top Categories** - Bar chart showing the categories with the most patterns
- **Top Subcategories** - Bar chart showing the subcategories with the most patterns

### Category Distribution Table

A detailed table showing all categories with their pattern counts and percentages.

## API Documentation

The web interface includes a link to the API documentation in the navigation bar. This opens in a new tab and provides detailed information about all available API endpoints.

## Advanced Features

### Pattern Testing

The pattern testing feature allows you to validate patterns against real-world data:

1. Navigate to any pattern details page
2. Click the "Test Pattern" button
3. Enter text that you believe should match the pattern
4. Click "Run Test" to see the results

This is particularly useful for:

- Validating new patterns
- Debugging existing patterns
- Understanding how patterns work

### Exporting Data

While the web interface doesn't currently support direct export, you can access the same data through the RESTful API:

- Use the `/api/v1/patterns` endpoint to retrieve pattern data
- Apply filters and pagination as needed
- Process the JSON data in your preferred format

## Best Practices

### Searching Effectively

1. **Use specific terms** - The more specific your search terms, the more relevant the results
2. **Combine filters** - Use category and vendor filters together with search terms for precise results
3. **Browse categories** - If you're unsure what to search for, browse the analytics page to discover popular categories

### Understanding Patterns

1. **Pattern priority** - Higher priority patterns are checked first
2. **Confidence levels** - Higher confidence indicates more reliable matches
3. **Version groups** - Indicate which part of a match contains version information

### Testing Patterns

1. **Use realistic data** - Test with actual HTTP headers, HTML content, or other relevant data
2. **Test edge cases** - Try variations of the expected input
3. **Check version extraction** - Verify that version information is correctly extracted

## Troubleshooting

### Common Issues

1. **Page not loading**
   - Check that the web application is running
   - Verify network connectivity
   - Check browser console for errors

2. **Search returning no results**
   - Try broader search terms
   - Remove filters to see if they're too restrictive
   - Check spelling of search terms

3. **Pattern test not working**
   - Ensure you've entered text in the input field
   - Check browser console for JavaScript errors
   - Verify that the web application and API are both running

### Getting Help

If you encounter issues not covered in this guide:

1. Check the application logs for error messages
2. Review the API documentation for correct usage
3. Open an issue on the GitHub repository
4. Contact the maintainers for support

## Feedback and Contributions

We welcome feedback and contributions to improve the web interface:

1. **Report bugs** - Open issues on GitHub for any bugs you encounter
2. **Suggest features** - Propose new features that would enhance the interface
3. **Contribute code** - Submit pull requests with improvements
4. **Improve documentation** - Help make this guide better for other users

The Regex Intelligence Exchange web interface is designed to be intuitive and powerful, providing easy access to a comprehensive database of technology fingerprinting patterns. Whether you're a security researcher, developer, or enthusiast, this interface should help you effectively work with regex patterns for technology identification.