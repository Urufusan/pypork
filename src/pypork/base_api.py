# Copyright 2025 Urufusan.
# SPDX-License-Identifier: 	AGPL-3.0-or-later

__author__ = "Urufusan"
__copyright__ = "Urufusan"
__license__ = "AGPL-3.0-or-later"

import requests


class PorkbunError(Exception):
    def __init__(self, message):
        if "record" in message:
            message += f"\nSupported record types: {', '.join(PorkbunAPI.ALLOWEDTYPES)}"
        elif "priority":
            message += f"\nSupported record types with priority: {', '.join(PorkbunAPI.ALLOWEDTYPES_PRIO)}"
        super().__init__(message)


class PorkbunAPI:
    """
    A Python client for interacting with the Porkbun API.

    API Documentation: https://porkbun.com/api/json/v3/documentation

    All API calls require valid API keys, which can be created at:
    https://porkbun.com/account/api
    """

    BASE_URL = "https://api.porkbun.com/api/json/v3"
    V4ONLYPINGURI = "https://api-ipv4.porkbun.com/api/json/v3"
    ALLOWEDTYPES = ["A", "MX", "CNAME", "ALIAS", "TXT", "NS", "AAAA", "SRV", "TLSA", "CAA", "SVCB", "HTTPS"]
    ALLOWEDTYPES_PRIO = ["SRV", "MX"]

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

    def ping(self, ipv4only: bool = False) -> dict:
        """
        Test communication with the Porkbun API.

        :param ipv4only: Whether to use IPv4 only (default: False).
        :return: JSON response with API status and your public IP.
        """
        url = f"{self.V4ONLYPINGURI if ipv4only else self.BASE_URL}/ping"
        payload = {"apikey": self.api_key, "secretapikey": self.secret_key}
        response = requests.post(url, json=payload)
        return response.json()

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
        record_type = record_type.upper()
        if record_type not in self.ALLOWEDTYPES:
            raise PorkbunError(f"Type {record_type} is not a valid record type supported by Porkbun")
        data = {"name": name, "type": record_type, "content": content, "ttl": str(ttl)}
        if prio:
            if record_type not in self.ALLOWEDTYPES_PRIO:
                raise PorkbunError(f"Your request type {record_type} does not support priority")
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
        record_type = record_type.upper()
        if record_type not in self.ALLOWEDTYPES:
            raise PorkbunError(f"Type {record_type} is not a valid record type supported by Porkbun")
        data = {"name": name, "type": record_type, "content": content, "ttl": str(ttl)}
        if prio:
            if record_type not in self.ALLOWEDTYPES_PRIO:
                raise PorkbunError(f"Your request type {record_type} does not support priority")
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
    def edit_dns_record_by_name_type(
        self, domain: str, record_type: str, content: str, subdomain: str = "", ttl: int = 600, prio: int = None
    ) -> dict:
        """
        Edit DNS records by name and type.

        :param domain: The domain name.
        :param record_type: The type of DNS record (A, MX, CNAME, etc.).
        :param content: The updated content of the record.
        :param subdomain: The subdomain for the record (default: root).
        :param ttl: Time-to-live in seconds (default: 600).
        :param prio: Priority for records like MX (optional).
        :return: JSON dict with update status.
        """
        record_type = record_type.upper()
        if record_type not in self.ALLOWEDTYPES:
            raise PorkbunError(f"Type {record_type} is not a valid record type supported by Porkbun")
        data = {"content": content, "ttl": str(ttl)}
        if prio:
            if record_type not in self.ALLOWEDTYPES_PRIO:
                raise PorkbunError(f"Your request type {record_type} does not support priority")
            data["prio"] = str(prio)
        return self._post(f"dns/editByNameType/{domain}/{record_type}/{subdomain}", data)

    @set_domain
    def get_dns_records_by_name_type(self, domain: str, record_type: str, subdomain: str = "") -> dict:
        """
        Retrieve DNS records by name and type.

        :param domain: The domain name.
        :param record_type: The type of DNS record (A, MX, CNAME, etc.).
        :param subdomain: The subdomain for the record (default: root).
        :return: JSON dict containing the DNS records.
        """
        record_type = record_type.upper()
        if record_type not in self.ALLOWEDTYPES:
            raise PorkbunError(f"Type {record_type} is not a valid record type supported by Porkbun")
        return self._post(f"dns/retrieveByNameType/{domain}/{record_type}/{subdomain}")

    @set_domain
    def delete_dns_record_by_name_type(self, domain: str, record_type: str, subdomain: str = "") -> dict:
        """
        Delete DNS records by name and type.

        :param domain: The domain name.
        :param record_type: The type of DNS record (A, MX, CNAME, etc.).
        :param subdomain: The subdomain for the record (default: root).
        :return: JSON dict with deletion status.
        """
        record_type = record_type.upper()
        if record_type not in self.ALLOWEDTYPES:
            raise PorkbunError(f"Type {record_type} is not a valid record type supported by Porkbun")
        return self._post(f"dns/deleteByNameType/{domain}/{record_type}/{subdomain}")

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

    @set_domain
    def ddns_update(self, domain: str, ip: str = "", subdomain: str = "", ipv4only: bool = True) -> dict:
        """
        Update a dynamic DNS record.

        :param domain: The domain name.
        :param ip: The IP address to update (optional).
        :param subdomain: The subdomain for the record (default: root).
        :param ipv4only: Whether to use IPv4 only (default: True).
        :return: JSON dict with update status.
        """
        if ip:
            ipaddr = ip
        else:
            ipaddr = self.ping(ipv4only=ipv4only)["yourIp"]
        record_type = "A" if ipv4only or ":" not in ipaddr else "AAAA"
        return self.edit_dns_record_by_name_type(domain, record_type, ipaddr, subdomain)

    @set_domain
    def create_dnssec_record(
        self,
        domain: str,
        key_tag: str,
        alg: str,
        digest_type: str,
        digest: str,
        max_sig_life: str = "",
        key_data_flags: str = "",
        key_data_protocol: str = "",
        key_data_algo: str = "",
        key_data_pub_key: str = "",
    ) -> dict:
        """
        Create a DNSSEC record at the registry.

        :param domain: The domain name.
        :param key_tag: Key Tag.
        :param alg: DS Data Algorithm.
        :param digest_type: Digest Type.
        :param digest: Digest.
        :param max_sig_life: Max Sig Life (optional).
        :param key_data_flags: Key Data Flags (optional).
        :param key_data_protocol: Key Data Protocol (optional).
        :param key_data_algo: Key Data Algorithm (optional).
        :param key_data_pub_key: Key Data Public Key (optional).
        :return: JSON dict containing the creation status.
        """
        data = {
            "keyTag": key_tag,
            "alg": alg,
            "digestType": digest_type,
            "digest": digest,
            "maxSigLife": max_sig_life,
            "keyDataFlags": key_data_flags,
            "keyDataProtocol": key_data_protocol,
            "keyDataAlgo": key_data_algo,
            "keyDataPubKey": key_data_pub_key,
        }
        return self._post(f"dns/createDnssecRecord/{domain}", data)

    @set_domain
    def get_dnssec_records(self, domain: str) -> dict:
        """
        Get the DNSSEC records associated with the domain at the registry.

        :param domain: The domain name.
        :return: JSON dict containing the DNSSEC records.
        """
        return self._post(f"dns/getDnssecRecords/{domain}")

    @set_domain
    def delete_dnssec_record(self, domain: str, key_tag: str) -> dict:
        """
        Delete a DNSSEC record associated with the domain at the registry.

        :param domain: The domain name.
        :param key_tag: The Key Tag of the record to delete.
        :return: JSON dict containing the deletion status.
        """
        return self._post(f"dns/deleteDnssecRecord/{domain}/{key_tag}")

    @set_domain
    def retrieve_ssl_bundle(self, domain: str) -> dict:
        """
        Retrieve the SSL certificate bundle for the domain.

        :param domain: The domain name.
        :return: JSON dict containing the SSL certificate bundle.
        """
        return self._post(f"ssl/retrieve/{domain}")
