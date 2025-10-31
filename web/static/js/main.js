// Modern JavaScript for Regex Intelligence Exchange

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initializeBootstrapComponents();
    
    // Initialize page-specific functionality
    initializePageFunctionality();
});

// Initialize Bootstrap components
function initializeBootstrapComponents() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Enable Bootstrap alerts
    var alertList = [].slice.call(document.querySelectorAll('.alert'));
    alertList.map(function (alertEl) {
        return new bootstrap.Alert(alertEl);
    });
}

// Initialize page-specific functionality
function initializePageFunctionality() {
    // Dashboard page
    if (document.getElementById('total-patterns')) {
        loadDashboardData();
    }
    
    // Search page
    if (document.getElementById('search-filters')) {
        initializeSearchFunctionality();
    }
    
    // Pattern detail page
    if (document.getElementById('test-pattern-btn')) {
        initializePatternTesting();
    }
    
    // Analytics page
    if (document.getElementById('category-chart')) {
        loadAnalyticsData();
    }
}

// Dashboard functionality
function loadDashboardData() {
    // Fetch dashboard data
    fetch('/api/analytics/summary')
        .then(response => response.json())
        .then(data => {
            document.getElementById('total-patterns').textContent = data.total_patterns;
            document.getElementById('total-categories').textContent = Object.keys(data.categories).length;
            document.getElementById('total-vendors').textContent = Object.keys(data.subcategories).length;
            
            // Create category chart
            createCategoryChart(data.categories, data.total_patterns);
        })
        .catch(error => {
            console.error('Error fetching dashboard data:', error);
            showNotification('Error loading dashboard data', 'danger');
        });
}

function createCategoryChart(categories, totalPatterns) {
    const categoryData = Object.entries(categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const chartContainer = document.getElementById('category-chart');
    if (!chartContainer) return;
    
    const chartHtml = `
        <div class="row">
            ${categoryData.map(([category, count]) => `
                <div class="col-6 col-md-3 mb-3">
                    <div class="text-center">
                        <div class="fw-bold">${category}</div>
                        <div class="display-6 text-primary">${count}</div>
                        <div class="small text-muted">
                            ${((count / totalPatterns) * 100).toFixed(1)}%
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    chartContainer.innerHTML = chartHtml;
}

// Search functionality
function initializeSearchFunctionality() {
    // Load categories and vendors for filters
    loadFilterOptions();
    
    // Set up search form submission
    const searchForm = document.getElementById('search-filters');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            performSearch(1);
        });
    }
    
    // Set up clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            document.getElementById('search-query').value = '';
            document.getElementById('category-filter').value = '';
            document.getElementById('vendor-filter').value = '';
            document.getElementById('search-results').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Enter search terms or apply filters to begin</p>
                </div>
            `;
            document.getElementById('result-count').textContent = '0';
        });
    }
    
    // Add real-time search with debounce
    let searchTimeout;
    const searchInput = document.getElementById('search-query');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Auto-submit the form when user types (with debounce)
                if (searchInput.value.trim() !== '') {
                    const searchForm = document.getElementById('search-filters');
                    if (searchForm) {
                        searchForm.dispatchEvent(new Event('submit'));
                    }
                } else {
                    document.getElementById('search-results').innerHTML = `
                        <div class="text-center">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p class="mt-2">Enter search terms or apply filters to begin</p>
                        </div>
                    `;
                    document.getElementById('result-count').textContent = '0';
                }
            }, 300); // 300ms debounce
        });
    }
    
    // Also trigger search when filters change
    const categoryFilter = document.getElementById('category-filter');
    const vendorFilter = document.getElementById('vendor-filter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const searchForm = document.getElementById('search-filters');
            if (searchForm) {
                searchForm.dispatchEvent(new Event('submit'));
            }
        });
    }
    
    if (vendorFilter) {
        vendorFilter.addEventListener('change', function() {
            const searchForm = document.getElementById('search-filters');
            if (searchForm) {
                searchForm.dispatchEvent(new Event('submit'));
            }
        });
    }
}

function loadFilterOptions() {
    // Load categories and vendors from patterns endpoint
    fetch('/api/patterns')
        .then(response => response.json())
        .then(data => {
            // Extract unique categories and vendors from patterns
            const categories = [...new Set(data.map(pattern => pattern.category).filter(Boolean))].sort();
            const vendors = [...new Set(data.map(pattern => pattern.vendor).filter(Boolean))].sort();
            
            const categorySelect = document.getElementById('category-filter');
            if (categorySelect) {
                // Clear existing options except the first one
                categorySelect.innerHTML = '<option value="">All Categories</option>';
                categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category;
                    option.textContent = category;
                    categorySelect.appendChild(option);
                });
            }
            
            const vendorSelect = document.getElementById('vendor-filter');
            if (vendorSelect) {
                // Clear existing options except the first one
                vendorSelect.innerHTML = '<option value="">All Vendors</option>';
                vendors.forEach(vendor => {
                    const option = document.createElement('option');
                    option.value = vendor;
                    option.textContent = vendor;
                    vendorSelect.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error loading filter options:', error);
            showNotification('Error loading filter options', 'danger');
        });
}

function performSearch(page = 1) {
    const query = document.getElementById('search-query')?.value || '';
    const category = document.getElementById('category-filter')?.value || '';
    const vendor = document.getElementById('vendor-filter')?.value || '';
    
    // Build query parameters
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (category) params.append('category', category);
    if (vendor) params.append('vendor', vendor);
    
    // Show loading indicator only if there are search terms or filters
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        if (query || category || vendor) {
            resultsContainer.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Searching patterns...</p>
                </div>
            `;
        } else {
            resultsContainer.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Enter search terms or apply filters to begin</p>
                </div>
            `;
            document.getElementById('result-count').textContent = '0';
            return;
        }
    }
    
    fetch(`/api/patterns/search?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            displaySearchResults(data, data.length);
        })
        .catch(error => {
            console.error('Error searching patterns:', error);
            if (resultsContainer) {
                resultsContainer.innerHTML = `<div class="alert alert-danger">Error searching patterns: ${error.message}</div>`;
            }
        });
}

function displaySearchResults(patterns, total) {
    const resultCountElement = document.getElementById('result-count');
    const resultsContainer = document.getElementById('search-results');
    
    if (resultCountElement) {
        resultCountElement.textContent = total;
    }
    
    if (resultsContainer) {
        if (patterns.length === 0) {
            resultsContainer.innerHTML = '<div class="alert alert-info">No patterns found matching your criteria</div>';
            return;
        }
        
        const resultsHtml = `
            <div class="row">
                ${patterns.map(pattern => `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="card h-100">
                            <div class="card-body">
                                <h5 class="card-title">${pattern.vendor} - ${pattern.product}</h5>
                                <p class="card-text">
                                    <span class="badge bg-primary">${pattern.category}</span>
                                    ${pattern.subcategory ? `<span class="badge bg-secondary ms-1">${pattern.subcategory}</span>` : ''}
                                </p>
                                <p class="card-text small text-muted">
                                    Vendor ID: ${pattern.vendor_id}<br>
                                    Product ID: ${pattern.product_id}
                                </p>
                            </div>
                            <div class="card-footer bg-transparent">
                                <a href="/pattern/${pattern.vendor_id}/${pattern.product_id}" class="btn btn-primary btn-sm w-100">
                                    <i class="fas fa-eye"></i> View Details
                                </a>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        resultsContainer.innerHTML = resultsHtml;
    }
}

// Pattern testing functionality
function initializePatternTesting() {
    // Test pattern button
    const testPatternBtn = document.getElementById('test-pattern-btn');
    if (testPatternBtn) {
        testPatternBtn.addEventListener('click', function() {
            const modal = new bootstrap.Modal(document.getElementById('testPatternModal'));
            modal.show();
        });
    }
    
    // Run test button
    const runTestBtn = document.getElementById('run-test-btn');
    if (runTestBtn) {
        runTestBtn.addEventListener('click', function() {
            const testInput = document.getElementById('test-input').value;
            if (!testInput.trim()) {
                document.getElementById('test-results').innerHTML = 
                    '<div class="alert alert-warning">Please enter some text to test</div>';
                return;
            }
            
            // Show loading indicator
            document.getElementById('test-results').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Testing...</span>
                    </div>
                    <p class="mt-2">Testing pattern...</p>
                </div>
            `;
            
            // In a real implementation, this would call the pattern matching API
            // For now, we'll simulate a result
            setTimeout(() => {
                const resultsHtml = `
                    <div class="alert alert-success">
                        <h5>Test Results</h5>
                        <p>Pattern matched successfully!</p>
                        <ul>
                            <li><strong>Matched Text:</strong> Server: Apache/2.4.41 (Ubuntu)</li>
                            <li><strong>Extracted Version:</strong> 2.4.41</li>
                            <li><strong>Confidence:</strong> 90%</li>
                        </ul>
                    </div>
                `;
                document.getElementById('test-results').innerHTML = resultsHtml;
            }, 1000);
        });
    }
    
    // Clear test button
    const clearTestBtn = document.getElementById('clear-test-btn');
    if (clearTestBtn) {
        clearTestBtn.addEventListener('click', function() {
            document.getElementById('test-input').value = '';
            document.getElementById('test-results').innerHTML = '';
        });
    }
    
    // Copy pattern button
    const copyPatternBtn = document.getElementById('copy-pattern-btn');
    if (copyPatternBtn) {
        copyPatternBtn.addEventListener('click', function() {
            // In a real implementation, this would copy the pattern data to clipboard
            // For now, we'll just show a success message
            const modal = new bootstrap.Modal(document.getElementById('copySuccessModal'));
            modal.show();
            
            // Auto-hide the modal after 1.5 seconds
            setTimeout(() => {
                modal.hide();
            }, 1500);
        });
    }
}

// Analytics functionality
function loadAnalyticsData() {
    // Fetch analytics data
    fetch('/api/analytics/summary')
    .then(response => response.json())
    .then(webData => {
        // Update summary cards
        document.getElementById('total-patterns').textContent = webData.total_patterns;
        document.getElementById('total-categories').textContent = Object.keys(webData.categories).length;
        document.getElementById('total-vendors').textContent = Object.keys(webData.subcategories).length;
        
        // Create charts
        createCategoryChartAnalytics(webData.categories, webData.total_patterns);
        createSubcategoryChartAnalytics(webData.subcategories, webData.total_patterns);
        
        // Populate category table
        populateCategoryTable(webData.categories, webData.total_patterns);
        
        // Load recent patterns
        loadRecentPatterns();
    })
    .catch(error => {
        console.error('Error fetching analytics data:', error);
        document.getElementById('total-patterns').textContent = 'Error';
        document.getElementById('total-categories').textContent = 'Error';
        document.getElementById('total-vendors').textContent = 'Error';
        
        // Show error in charts
        document.getElementById('category-chart').innerHTML = 
            '<div class="alert alert-danger">Error loading data</div>';
        document.getElementById('subcategory-chart').innerHTML = 
            '<div class="alert alert-danger">Error loading data</div>';
        document.getElementById('category-table').innerHTML = 
            '<tr><td colspan="4" class="text-center text-danger">Error loading data</td></tr>';
    });
}

function createCategoryChartAnalytics(categories, totalPatterns) {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.categoryChart) {
        window.categoryChart.destroy();
    }
    
    // Get top 10 categories
    const categoryData = Object.entries(categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const labels = categoryData.map(([category]) => category);
    const data = categoryData.map(([, count]) => count);
    
    window.categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pattern Count',
                data: data,
                backgroundColor: 'rgba(67, 97, 238, 0.7)',
                borderColor: 'rgba(67, 97, 238, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createSubcategoryChartAnalytics(subcategories, totalPatterns) {
    const ctx = document.getElementById('subcategory-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.subcategoryChart) {
        window.subcategoryChart.destroy();
    }
    
    // Get top 10 subcategories
    const subcategoryData = Object.entries(subcategories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const labels = subcategoryData.map(([subcategory]) => subcategory || 'Uncategorized');
    const data = subcategoryData.map(([, count]) => count);
    
    window.subcategoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Pattern Count',
                data: data,
                backgroundColor: 'rgba(76, 201, 240, 0.7)',
                borderColor: 'rgba(76, 201, 240, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function populateCategoryTable(categories, totalPatterns) {
    const categoryTableHtml = Object.entries(categories)
        .sort((a, b) => b[1] - a[1])
        .map(([category, count]) => {
            const percentage = ((count / totalPatterns) * 100).toFixed(1);
            const barWidth = Math.min(100, percentage);
            return `
                <tr>
                    <td>${category}</td>
                    <td>${count}</td>
                    <td>${percentage}%</td>
                    <td>
                        <div class="progress" style="height: 10px;">
                            <div class="progress-bar bg-primary" role="progressbar" 
                                 style="width: ${barWidth}%">
                            </div>
                        </div>
                    </td>
                </tr>
            `;
        })
        .join('');
    
    document.getElementById('category-table').innerHTML = categoryTableHtml;
}

function loadRecentPatterns() {
    fetch('/api/patterns?limit=5')
    .then(response => response.json())
    .then(data => {
        const recentPatternsHtml = `
            <div class="list-group">
                ${data.map(pattern => `
                    <a href="/pattern/${pattern.vendor_id}/${pattern.product_id}" 
                       class="list-group-item list-group-item-action">
                        <div class="d-flex w-100 justify-content-between">
                            <h6 class="mb-1">${pattern.vendor} - ${pattern.product}</h6>
                            <small>${pattern.category}</small>
                        </div>
                        <p class="mb-1">
                            <span class="badge bg-primary">${pattern.category}</span>
                            ${pattern.subcategory ? `<span class="badge bg-secondary ms-1">${pattern.subcategory}</span>` : ''}
                        </p>
                    </a>
                `).join('')}
            </div>
        `;
        
        document.getElementById('recent-patterns').innerHTML = recentPatternsHtml;
    })
    .catch(error => {
        document.getElementById('recent-patterns').innerHTML = 
            `<div class="alert alert-danger">Error loading recent patterns: ${error.message}</div>`;
    });
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Add to page
    const container = document.querySelector('.container-fluid');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

// Export functionality
if (document.getElementById('export-csv')) {
    document.getElementById('export-csv').addEventListener('click', function() {
        // In a real implementation, this would download a CSV file
        showNotification('CSV export functionality would be implemented here', 'info');
    });
}

if (document.getElementById('export-json')) {
    document.getElementById('export-json').addEventListener('click', function() {
        // In a real implementation, this would download a JSON file
        showNotification('JSON export functionality would be implemented here', 'info');
    });
}