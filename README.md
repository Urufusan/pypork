[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)

# pypork

> A Python library/wrapper for the porkbun.com REST API

## Description

This library provides a convenient interface to the Porkbun API, allowing you to manage domains, DNS records, and URL forwarding through Python. The API documentation can be found [here](https://porkbun.com/api/json/v3/documentation).

## Installation

To install this package directly from the GitHub repository, use the following pip command:

```bash
pip install git+https://github.com/Urufusan/pypork.git
```

## Implemented features

This library implements all the features listed in the API documentation for v3.

### General API Information
- **Domain Pricing**: `get_domain_pricing()`
- **Authentication**: Handled in the `__init__`, when creating a `PorkbunAPI` object

### Domain Functionality
- **Domain Update Name Servers**: `update_name_servers()`
- **Domain Get Name Servers**: `get_name_servers()`
- **Domain List All**: `list_domains()`
- **Domain Add URL Forward**: `add_url_forwarding()`
- **Domain Get URL Forwarding**: `get_url_forwarding()`
- **Domain Delete URL Forward**: `delete_url_forwarding()`
- **Domain Check**: `check_domain_availability()`

### DNS Functionality
- **DNS Create Record**: `create_dns_record()`
- **DNS Edit Record by Domain and ID**: `edit_dns_record()`
- **DNS Edit Records by Domain, Subdomain and Type**: `edit_dns_record_by_name_type()`
- **DNS Delete Record by Domain and ID**: `delete_dns_record()`
- **DNS Delete Records by Domain, Subdomain and Type**: `delete_dns_record_by_name_type()`
- **DNS Retrieve Records by Domain or ID**: `get_dns_records()`
- **DNS Retrieve Records by Domain, Subdomain and Type**: `get_dns_records_by_name_type()`
- **DNSSEC Create Record**: `create_dnssec_record()`
- **DNSSEC Get Records**: `get_dnssec_records()`
- **DNSSEC Delete Record**: `delete_dnssec_record()`

### SSL Functionality
- **SSL Retrieve Bundle by Domain**: `retrieve_ssl_bundle()`

## Usage

Below are some examples of how to use the `PorkbunAPI` class.

```python
from src.pypork.base_api import PorkbunAPI

api_key = 'your_api_key'
secret_key = 'your_secret_key'
default_domain = 'example.com'

client = PorkbunAPI(api_key, secret_key, default_domain)

# Ping the API
response = client.ping()
print(response)

# Retrieve Domain Pricing
pricing = client.get_domain_pricing()
print(pricing)

# List All Domains
domains = client.list_domains(start=0, include_labels=True)
print(domains)

# Check Domain Availability
availability = client.check_domain_availability(domain='example.com')
print(availability)

# Get Name Servers
name_servers = client.get_name_servers(domain='example.com')
print(name_servers)

# Update Name Servers
update_status = client.update_name_servers(domain='example.com', name_servers=['ns1.example.com', 'ns2.example.com'])
print(update_status)

# Create DNS Record
record = client.create_dns_record(domain='example.com', name='www', record_type='A', content='192.0.2.1')
print(record)

# Retrieve DNS Records
dns_records = client.get_dns_records(domain='example.com')
print(dns_records)

# Edit DNS Record
edit_status = client.edit_dns_record(domain='example.com', record_id=12345, name='www', record_type='A', content='192.0.2.2')
print(edit_status)

# Delete DNS Record
delete_status = client.delete_dns_record(domain='example.com', record_id=12345)
print(delete_status)

# Edit DNS Record by Name and Type
edit_by_name_type_status = client.edit_dns_record_by_name_type(domain='example.com', record_type='A', content='192.0.2.3', subdomain='www')
print(edit_by_name_type_status)

# Retrieve DNS Records by Name and Type
dns_records_by_name_type = client.get_dns_records_by_name_type(domain='example.com', record_type='A', subdomain='www')
print(dns_records_by_name_type)

# Delete DNS Record by Name and Type
delete_by_name_type_status = client.delete_dns_record_by_name_type(domain='example.com', record_type='A', subdomain='www')
print(delete_by_name_type_status)

# Add URL Forwarding
forwarding_status = client.add_url_forwarding(domain='example.com', location='https://destination.com', forward_type='temporary', subdomain='www')
print(forwarding_status)

# Get URL Forwarding
url_forwarding = client.get_url_forwarding(domain='example.com')
print(url_forwarding)

# Delete URL Forwarding
delete_forwarding_status = client.delete_url_forwarding(domain='example.com', record_id=12345)
print(delete_forwarding_status)

# Create DNSSEC Record
dnssec_record = client.create_dnssec_record(
    domain='example.com',
    key_tag='64087',
    alg='13',
    digest_type='2',
    digest='15E445BD08128BDC213E25F1C8227DF4CB35186CAC701C1C335B2C406D5530DC'
)
print(dnssec_record)

# Get DNSSEC Records
dnssec_records = client.get_dnssec_records(domain='example.com')
print(dnssec_records)

# Delete DNSSEC Record
delete_dnssec_status = client.delete_dnssec_record(domain='example.com', key_tag='64087')
print(delete_dnssec_status)

# Retrieve SSL Bundle
ssl_bundle = client.retrieve_ssl_bundle(domain='example.com')
print(ssl_bundle)
```

## License

This project is licensed under the AGPL-3.0-or-later License - see the LICENSE file for details.

## Note

This project has been set up using PyScaffold 4.6. For details and usage information on PyScaffold see [https://pyscaffold.org/](https://pyscaffold.org/).

## Author

Urufusan

---
