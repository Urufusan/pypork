# Copyright 2025 Urufusan.
# SPDX-License-Identifier: 	AGPL-3.0-or-later

__author__ = "Urufusan"
__copyright__ = "Urufusan"
__license__ = "AGPL-3.0-or-later"

import requests


class PorkbunAPI:
    """
    A Python client for interacting with the Porkbun API.

    API Documentation: https://porkbun.com/api/json/v3/documentation

    All API calls require valid API keys, which can be created at:
    https://porkbun.com/account/api
    """

    BASE_URL = "https://api.porkbun.com/api/json/v3"

    def set_domain(_method):
        """Sets the default domain, defined in ``__init__``, for all functions that use it"""
        arg_name = "domain"

        def wrapper(self, *args, **kwargs):
            if getattr(self, arg_name, None):
                if arg_name in kwargs and kwargs[arg_name] is None:
                    kwargs[arg_name] = getattr(self, arg_name)
                elif len(args) < _method.__code__.co_argcount - 1:
                    kwargs[arg_name] = getattr(self, arg_name)
            return _method(self, *args, **kwargs)

        return wrapper

    def __init__(self, api_key: str, secret_key: str, domain: str = None, check_creds: bool = True):
        """
        Initialize the Porkbun API client.

        :param api_key: Your Porkbun API key.
        :param secret_key: Your Porkbun secret API key.
        :param domain: The domain you want to use by default (will be used as `domain` arg in functions, but can be left empty)
        :param check_creds: Check the provided credentials
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.domain = domain
        if check_creds:
            _ping = self.ping()
            if _ping["status"] == "ERROR":
                raise ConnectionRefusedError(_ping["message"])

    def _post(self, endpoint: str, data: dict = None) -> dict:
        """
        Helper method to make a POST request to the Porkbun API.

        :param endpoint: The API endpoint (excluding the base URL).
        :param data: Additional payload data for the request.
        :return: JSON response as a dictionary.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        payload = {"apikey": self.api_key, "secretapikey": self.secret_key}
        if data:
            payload.update(data)
        response = requests.post(url, json=payload)
        return response.json()

    def ping(self) -> dict:
        """
        Test communication with the Porkbun API.

        :return: JSON response with API status and your public IP.
        """
        return self._post("ping")

    def get_domain_pricing(self) -> dict:
        """
        Retrieve pricing information for domain registration, renewal, and transfer.

        :return: JSON dict containing pricing details for supported TLDs.
        """
        return self._post("pricing/get")

    def list_domains(self, start: int = 0, include_labels: bool = False) -> dict:
        """
        Get a list of all domains in your Porkbun account.

        :param start: Index to start retrieving domains (default: 0). Increment by 1000 to get all.
        :param include_labels: Whether to include label information (default: False).
        :return: JSON dict with domain details.
        """
        return self._post("domain/listAll", {"start": str(start), "includeLabels": "yes" if include_labels else "no"})

    @set_domain
    def check_domain_availability(self, domain: str) -> dict:
        """
        Check if a domain is available for registration.

        :param domain: The domain name to check.
        :return: JSON dict with availability status and pricing.
        """
        return self._post(f"domain/checkDomain/{domain}")

    @set_domain
    def get_name_servers(self, domain: str) -> dict:
        """
        Retrieve the authoritative name servers for a domain.

        :param domain: The domain to check.
        :return: JSON dict containing the name servers.
        """
        return self._post(f"domain/getNs/{domain}")

    @set_domain
    def update_name_servers(self, domain: str, name_servers: list) -> dict:
        """
        Update the name servers for a domain.

        :param domain: The domain to update.
        :param name_servers: List of name servers to assign.
        :return: JSON dict with the update status.
        """
        return self._post(f"domain/updateNs/{domain}", {"ns": name_servers})

    @set_domain
    def create_dns_record(self, domain: str, name: str, record_type: str, content: str, ttl: int = 600, prio: int = None) -> dict:
        """
        Create a DNS record for a domain.

        :param domain: The domain name.
        :param name: The subdomain for the record (leave blank for root, use '*' for wildcard).
        :param record_type: The type of DNS record (A, CNAME, MX, TXT, etc.).
        :param content: The content/value of the record.
        :param ttl: Time-to-live in seconds (default: 600).
        :param prio: Priority for records like MX (optional).
        :return: JSON dict with the created record ID.
        """
        data = {"name": name, "type": record_type, "content": content, "ttl": str(ttl)}
        if prio:
            data["prio"] = str(prio)
        return self._post(f"dns/create/{domain}", data)

    @set_domain
    def get_dns_records(self, domain: str) -> dict:
        """
        Retrieve all DNS records for a given domain.

        :param domain: The domain name.
        :return: JSON dict containing the DNS records.
        """
        return self._post(f"dns/retrieve/{domain}")

    @set_domain
    def edit_dns_record(self, domain: str, record_id: str | int, name: str, record_type: str, content: str, ttl: int = 600, prio: int = None) -> dict:
        """
        Edit an existing DNS record.

        :param domain: The domain name.
        :param record_id: The ID of the DNS record to edit.
        :param name: The subdomain for the record.
        :param record_type: The type of DNS record.
        :param content: The updated content of the record.
        :param ttl: Time-to-live in seconds (default: 600).
        :param prio: Priority (for MX records, optional).
        :return: JSON dict with update status.
        """
        data = {"name": name, "type": record_type, "content": content, "ttl": str(ttl)}
        if prio:
            data["prio"] = str(prio)
        return self._post(f"dns/edit/{domain}/{record_id}", data)

    @set_domain
    def delete_dns_record(self, domain: str, record_id: str | int) -> dict:
        """
        Delete a specific DNS record by ID.

        :param domain: The domain name.
        :param record_id: The ID of the DNS record to delete.
        :return: JSON dict with deletion status.
        """
        return self._post(f"dns/delete/{domain}/{record_id}")

    @set_domain
    def add_url_forwarding(
        self, domain: str, location: str, forward_type: str = "temporary", subdomain: str = "", include_path: bool = False, wildcard: bool = True
    ) -> dict:
        """
        Add URL forwarding for a domain.

        :param domain: The domain name.
        :param location: The destination URL.
        :param forward_type: The type of forward (`'temporary'` or `'permanent'`).
        :param subdomain: The subdomain to forward (default: root).
        :param include_path: Whether to include URI path ('yes' or 'no').
        :param wildcard: Forward all subdomains ('yes' or 'no').
        :return: JSON dict with forward creation status.
        """
        return self._post(
            f"domain/addUrlForward/{domain}",
            {
                "subdomain": subdomain,
                "location": location,
                "type": forward_type,
                "includePath": ("yes" if include_path else "no"),
                "wildcard": ("yes" if wildcard else "no"),
            },
        )

    @set_domain
    def get_url_forwarding(self, domain: str) -> dict:
        """
        Retrieve URL forwarding records for a domain.

        :param domain: The domain name.
        :return: JSON dict containing forwarding records.
        """
        return self._post(f"domain/getUrlForwarding/{domain}")

    @set_domain
    def delete_url_forwarding(self, domain: str, record_id: str | int) -> dict:
        """
        Delete a URL forwarding record.

        :param domain: The domain name.
        :param record_id: The ID of the forwarding record.
        :return: JSON dict with deletion status.
        """
        return self._post(f"domain/deleteUrlForward/{domain}/{record_id}")
