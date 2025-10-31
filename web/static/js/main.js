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
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" 
                             style="width: ${Math.min(100, (count / totalPatterns) * 100)}%">
                        </div>
                    </div>
                    <div class="text-center small mt-1">
                        <strong>${category}</strong><br>
                        ${count} patterns
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
    
    // Initial search
    performSearch(1);
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
    
    // Show loading indicator
    const resultsContainer = document.getElementById('search-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p>Searching patterns...</p>
            </div>
        `;
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
    if (resultCountElement) {
        resultCountElement.textContent = total;
    }
    
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    if (patterns.length === 0) {
        resultsContainer.innerHTML = '<div class="alert alert-info">No patterns found matching your criteria.</div>';
        return;
    }
    
    const resultsHtml = `
        <div class="list-group">
            ${patterns.map(pattern => `
                <a href="/pattern/${pattern.vendor_id}/${pattern.product_id}" 
                   class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${pattern.vendor} - ${pattern.product}</h5>
                        <small class="text-muted">${pattern.pattern_count} patterns</small>
                    </div>
                    <p class="mb-1">
                        <span class="badge bg-primary">${pattern.category}</span>
                        ${pattern.subcategory ? `<span class="badge bg-secondary ms-1">${pattern.subcategory}</span>` : ''}
                    </p>
                    <small class="text-muted">Vendor ID: ${pattern.vendor_id} | Product ID: ${pattern.product_id}</small>
                </a>
            `).join('')}
        </div>
    `;
    
    resultsContainer.innerHTML = resultsHtml;
}

function updatePagination(totalItems, currentPage, itemsPerPage) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const paginationContainer = document.getElementById('pagination-controls');
    
    if (!paginationContainer) return;
    
    if (totalPages <= 1) {
        paginationContainer.classList.add('d-none');
        return;
    }
    
    paginationContainer.classList.remove('d-none');
    
    let paginationHtml = '<ul class="pagination justify-content-center">';
    
    // Previous button
    if (currentPage > 1) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Previous</a>
            </li>
        `;
    } else {
        paginationHtml += '<li class="page-item disabled"><a class="page-link" href="#">Previous</a></li>';
    }
    
    // Page numbers (simplified - show current page and nearby pages)
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === currentPage) {
            paginationHtml += `<li class="page-item active"><a class="page-link" href="#">${i}</a></li>`;
        } else {
            paginationHtml += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        paginationHtml += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Next</a>
            </li>
        `;
    } else {
        paginationHtml += '<li class="page-item disabled"><a class="page-link" href="#">Next</a></li>';
    }
    
    paginationHtml += '</ul>';
    paginationContainer.innerHTML = paginationHtml;
    
    // Add event listeners to pagination links
    paginationContainer.querySelectorAll('.page-link[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = parseInt(this.getAttribute('data-page'));
            performSearch(page);
        });
    });
}

// Pattern testing functionality
function initializePatternTesting() {
    const testButton = document.getElementById('test-pattern-btn');
    if (testButton) {
        testButton.addEventListener('click', function() {
            const testModal = new bootstrap.Modal(document.getElementById('testPatternModal'));
            testModal.show();
        });
    }
    
    const runTestButton = document.getElementById('run-test-btn');
    if (runTestButton) {
        runTestButton.addEventListener('click', runPatternTest);
    }
}

function runPatternTest() {
    const inputText = document.getElementById('test-input')?.value || '';
    
    if (!inputText.trim()) {
        const resultsContainer = document.getElementById('test-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = '<div class="alert alert-warning">Please enter some text to test.</div>';
        }
        return;
    }
    
    // Show loading indicator
    const resultsContainer = document.getElementById('test-results');
    if (resultsContainer) {
        resultsContainer.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Testing...</span>
                </div>
                <p>Testing patterns against input text...</p>
            </div>
        `;
    }
    
    fetch('/api/match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text: inputText
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (resultsContainer) {
            if (data.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="alert alert-info">
                        <h5>No Matches Found</h5>
                        <p>No technology patterns were detected in the provided text.</p>
                    </div>
                `;
                return;
            }
            
            // Group matches by vendor and product for better organization
            const groupedMatches = {};
            data.forEach(match => {
                const key = `${match.vendor_id}/${match.product_id}`;
                if (!groupedMatches[key]) {
                    groupedMatches[key] = {
                        vendor: match.vendor,
                        product: match.product,
                        vendor_id: match.vendor_id,
                        product_id: match.product_id,
                        matches: []
                    };
                }
                groupedMatches[key].matches.push(match);
            });
            
            // Convert to array and sort by number of matches
            const sortedMatches = Object.values(groupedMatches).sort((a, b) => 
                b.matches.length - a.matches.length
            );
            
            // Create advanced results display
            let resultsHtml = `
                <div class="alert alert-success">
                    <h5>Found ${data.length} total match${data.length !== 1 ? 'es' : ''} across ${sortedMatches.length} technology pattern${sortedMatches.length !== 1 ? 's' : ''}!</h5>
                    <p>Potential technologies detected:</p>
                </div>
                
                <div class="accordion" id="advancedTestResults">
            `;
            
            sortedMatches.forEach((group, index) => {
                const firstMatch = group.matches[0];
                resultsHtml += `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="heading-${index}">
                            <button class="accordion-button${index === 0 ? '' : ' collapsed'}" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#collapse-${index}" aria-expanded="${index === 0 ? 'true' : 'false'}" 
                                    aria-controls="collapse-${index}">
                                ${escapeHtml(group.vendor)} - ${escapeHtml(group.product)}
                                <span class="badge bg-primary ms-2">${group.matches.length} match${group.matches.length !== 1 ? 'es' : ''}</span>
                                ${firstMatch.version ? `<span class="badge bg-success ms-2">Version: ${escapeHtml(firstMatch.version)}</span>` : ''}
                            </button>
                        </h2>
                        <div id="collapse-${index}" class="accordion-collapse collapse${index === 0 ? ' show' : ''}" 
                             aria-labelledby="heading-${index}">
                            <div class="accordion-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Pattern Information</h6>
                                        <ul class="list-unstyled">
                                            <li><strong>Vendor:</strong> ${escapeHtml(group.vendor)}</li>
                                            <li><strong>Product:</strong> ${escapeHtml(group.product)}</li>
                                            <li><strong>Vendor ID:</strong> ${escapeHtml(group.vendor_id)}</li>
                                            <li><strong>Product ID:</strong> ${escapeHtml(group.product_id)}</li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Match Statistics</h6>
                                        <ul class="list-unstyled">
                                            <li><strong>Total Matches:</strong> ${group.matches.length}</li>
                                            ${firstMatch.version ? `<li><strong>Detected Version:</strong> ${escapeHtml(firstMatch.version)}</li>` : ''}
                                        </ul>
                                    </div>
                                </div>
                                
                                <h6 class="mt-3">Detailed Matches</h6>
                                <div class="list-group">
                                    ${group.matches.map((match, matchIndex) => `
                                        <div class="list-group-item">
                                            <div class="d-flex w-100 justify-content-between">
                                                <h6 class="mb-1">Match #${matchIndex + 1}: ${escapeHtml(match.pattern_name)}</h6>
                                                ${match.version ? `<span class="badge bg-primary">Version: ${escapeHtml(match.version)}</span>` : ''}
                                            </div>
                                            ${match.version_range ? `<small class="text-muted">Version Range: ${escapeHtml(match.version_range)}</small>` : ''}
                                            <p class="mb-1"><strong>Matched Text:</strong> <code>${escapeHtml(match.matched_text)}</code></p>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            resultsHtml += `
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-outline-primary" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#raw-test-results" aria-expanded="false" aria-controls="raw-test-results">
                        <i class="fas fa-code"></i> Show Raw Results
                    </button>
                    <div class="collapse mt-2" id="raw-test-results">
                        <div class="card card-body">
                            <pre class="mb-0">${escapeHtml(JSON.stringify(data, null, 2))}</pre>
                        </div>
                    </div>
                </div>
            `;
            
            resultsContainer.innerHTML = resultsHtml;
        }
    })
    .catch(error => {
        console.error('Error testing pattern:', error);
        if (resultsContainer) {
            resultsContainer.innerHTML = `<div class="alert alert-danger">Error testing patterns: ${error.message}</div>`;
        }
    });
}

// Analytics functionality
function loadAnalyticsData() {
    // Fetch analytics data - only use web app endpoint
    fetch('/api/analytics/summary')
        .then(response => response.json())
        .then(data => {
            // Update summary cards
            const totalPatternsElement = document.getElementById('total-patterns');
            if (totalPatternsElement) {
                totalPatternsElement.textContent = data.total_patterns;
            }
            
            const totalCategoriesElement = document.getElementById('total-categories');
            if (totalCategoriesElement) {
                totalCategoriesElement.textContent = Object.keys(data.categories).length;
            }
            
            const totalVendorsElement = document.getElementById('total-vendors');
            if (totalVendorsElement) {
                totalVendorsElement.textContent = Object.keys(data.subcategories).length;
            }
            
            // Create charts using the web app data
            createAnalyticsCharts(data, data.total_patterns);
            
            // Populate category table
            populateCategoryTable(data.categories, data.total_patterns);
        })
        .catch(error => {
            console.error('Error fetching analytics data:', error);
            showNotification('Error loading analytics data', 'danger');
        });
}

function createAnalyticsCharts(data, totalPatterns) {
    // Category chart
    const categoryData = Object.entries(data.categories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const categoryChartContainer = document.getElementById('category-chart');
    if (categoryChartContainer) {
        const categoryChartHtml = `
            <div class="row">
                ${categoryData.map(([category, count], index) => `
                    <div class="col-12 mb-2">
                        <div class="d-flex justify-content-between">
                            <span>${category}</span>
                            <span>${count}</span>
                        </div>
                        <div class="progress">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: ${Math.min(100, (count / totalPatterns) * 100)}%">
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        categoryChartContainer.innerHTML = categoryChartHtml;
    }
    
    // Subcategory chart
    const subcategoryData = Object.entries(data.subcategories)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    const subcategoryChartContainer = document.getElementById('subcategory-chart');
    if (subcategoryChartContainer) {
        const subcategoryChartHtml = `
            <div class="row">
                ${subcategoryData.map(([subcategory, count], index) => `
                    <div class="col-12 mb-2">
                        <div class="d-flex justify-content-between">
                            <span>${subcategory || 'Uncategorized'}</span>
                            <span>${count}</span>
                        </div>
                        <div class="progress">
                            <div class="progress-bar bg-success" role="progressbar" 
                                 style="width: ${Math.min(100, (count / totalPatterns) * 100)}%">
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
        subcategoryChartContainer.innerHTML = subcategoryChartHtml;
    }
}

function populateCategoryTable(categories, totalPatterns) {
    const tableBody = document.getElementById('category-table');
    if (!tableBody) return;
    
    const tableHtml = Object.entries(categories)
        .sort((a, b) => b[1] - a[1])
        .map(([category, count]) => {
            const percentage = ((count / totalPatterns) * 100).toFixed(1);
            return `
                <tr>
                    <td>${category}</td>
                    <td>${count}</td>
                    <td>${percentage}%</td>
                </tr>
            `;
        })
        .join('');
    
    tableBody.innerHTML = tableHtml;
}

// Utility functions
function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container-fluid');
    if (container) {
        // Insert at the top of the container
        container.insertAdjacentHTML('afterbegin', alertHtml);
    }
}

// Debounce function for rate limiting
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Add utility function for escaping HTML
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

// Export functions for global use
window.showNotification = showNotification;
window.debounce = debounce;