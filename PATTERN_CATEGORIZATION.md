# Pattern Categorization System

This document defines the enhanced pattern categorization system for the Regex Intelligence Exchange.

## Main Categories

The main categories remain the same as before:

1. **web** - Web servers and related technologies
2. **cms** - Content Management Systems
3. **database** - Database engines and systems
4. **framework** - Application frameworks
5. **messaging** - Messaging systems and protocols
6. **networking** - Networking equipment and protocols
7. **os** - Operating systems

## Subcategories

Each main category has specific subcategories for more granular classification:

### Web Category Subcategories
- **web-server** - Web servers like Apache HTTPD, NGINX, IIS
- **web-proxy** - Proxy servers like Squid, Varnish
- **web-application** - Web applications and platforms
- **cdn** - Content Delivery Networks
- **load-balancer** - Load balancing solutions

### CMS Category Subcategories
- **cms-platform** - Full CMS platforms like WordPress, Drupal, Joomla
- **cms-plugin** - Plugins and extensions for CMS platforms
- **cms-theme** - Themes and templates for CMS platforms
- **ecommerce** - E-commerce platforms like Magento, Shopify

### Database Category Subcategories
- **database-engine** - Database engines like MySQL, PostgreSQL, MongoDB
- **database-management** - Database management tools
- **database-proxy** - Database proxy solutions

### Framework Category Subcategories
- **web-framework** - Web application frameworks like Django, Rails, Spring
- **mobile-framework** - Mobile application frameworks
- **frontend-framework** - Frontend JavaScript frameworks like React, Vue

### Messaging Category Subcategories
- **email-server** - Email servers like Exchange, Postfix
- **message-queue** - Message queue systems like RabbitMQ, Kafka
- **chat-system** - Chat and instant messaging systems

### Networking Category Subcategories
- **router** - Network routers
- **switch** - Network switches
- **firewall** - Firewall and security appliances
- **vpn** - VPN solutions
- **wireless** - Wireless networking equipment
- **network-monitoring** - Network monitoring tools

### OS Category Subcategories
- **linux-distribution** - Linux distributions like Ubuntu, CentOS
- **windows** - Windows operating systems
- **unix** - Unix variants
- **embedded** - Embedded operating systems

## Usage Guidelines

When creating or updating pattern files:

1. Always specify the main `category` field from the allowed list above
2. Include the optional but recommended `subcategory` field for more precise classification
3. Use existing subcategories when possible to maintain consistency
4. If a new subcategory is needed, propose it through the contribution process

## Examples

### Web Server Pattern
```json
{
  "vendor": "Apache",
  "vendor_id": "apache",
  "product": "HTTPD",
  "product_id": "apache-httpd",
  "category": "web",
  "subcategory": "web-server"
  // ... rest of the pattern
}
```

### CMS Pattern
```json
{
  "vendor": "WordPress",
  "vendor_id": "wordpress",
  "product": "WordPress",
  "product_id": "wordpress-wordpress",
  "category": "cms",
  "subcategory": "cms-platform"
  // ... rest of the pattern
}
```

### Database Pattern
```json
{
  "vendor": "MySQL",
  "vendor_id": "mysql",
  "product": "MySQL",
  "product_id": "mysql-mysql",
  "category": "database",
  "subcategory": "database-engine"
  // ... rest of the pattern
}
```

This enhanced categorization system allows for more precise filtering and searching of patterns while maintaining backward compatibility with existing tools.