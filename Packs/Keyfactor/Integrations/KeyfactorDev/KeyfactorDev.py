import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

""" IMPORTS """
# Std imports

import re
# 3-rd party imports
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple, Union

import requests
import urllib3

# Local imports
# N/A

"""

GLOBALS/PARAMS

Attributes:
    INTEGRATION_NAME:
        Name of the integration as shown in the integration UI, for example: Microsoft Graph User.

    INTEGRATION_COMMAND_NAME:
        Command names should be written in all lower-case letters,
        and each word separated with a hyphen, for example: msgraph-user.

    INTEGRATION_CONTEXT_NAME:
        Context output names should be written in camel case, for example: MSGraphUser.
"""
INTEGRATION_NAME = 'Keyfactor Dev'
INTEGRATION_COMMAND_NAME = 'keyfactor'
INTEGRATION_CONTEXT_NAME = 'Keyfactor'

# Disable insecure warnings
urllib3.disable_warnings()


class Client(BaseClient):

    def test_module(self) -> Dict:
        """
            Performs basic GET request to check if the API is reachable and authentication is successful.
        Returns:
            Response dictionary
        """
        return self.get_enrollment_csr_context_my()

    def get_enrollment_csr_context_my(self) -> dict:
        """
            Get enrollment CSR context my
            > Retrieve a list of existing certificate templates
        Args:
            N/A

        Returns:
            Json response as dictionary
        """

        headers = {
            'x-keyfactor-api-version': '1',
            'x-keyfactor-requested-with': 'APIClient',
            'Accept': 'application/json'
        }

        return self._http_request(method='GET',
                                  url_suffix='Enrollment/CSR/Context/My',
                                  headers=headers)

    def post_enrollment_csr(self,
                            csr_base64: str,
                            cert_authority: str,
                            include_chain: str,
                            time_stamp: date,
                            template: str,
                            sans_ip4: str,
                            keyAlgorithm: str,
                            metadata: dict) -> dict:
        """
            Post Enrollment CSR
            Send the certifcate CSR and return the certificate
        Args:
            csr_base64
            cert_authority
            include_chain
            time_stamp
            template
            sans_ip4
            keyAlgorithm
            metadata

        Returns:
            Json response as dictionary
        """
        if sans_ip4 == '':
            body = {"CSR": csr_base64,
                    "CertificateAuthority": cert_authority,
                    "includeChain": include_chain,
                    "Timestamp": time_stamp,
                    "Template": template,
                    "Metadata": metadata
                    }

        else:
            ip4 = {
                'ip4': [sans_ip4]
            }

            body = {"CSR": csr_base64,
                    "CertificateAuthority": cert_authority,
                    "includeChain": include_chain,
                    "Timestamp": time_stamp,
                    "Template": template,
                    "SANs": ip4,
                    "Metadata": metadata
                    }

        headers = {
            'x-keyfactor-api-version': '1',
            'x-keyfactor-requested-with': 'APIClient',
            'x-certificateformat': 'PEM',
            'Accept': 'application/json'
        }

        return self._http_request(method='POST',
                                  url_suffix='Enrollment/CSR',
                                  headers=headers,
                                  json_data=body,
                                  )


''' HELPER FUNCTIONS '''


def get_enrollment_csr_context_my_ec(raw_response: dict) -> Tuple[list, list]:
    """
        Get raw response of Enrollment csr templates and parse to ec
    Args:
        raw_response: Enrollment csr templates list

    Returns:
        List of Enrollment csr templates entry context for human readable
    """
    entry_context = []
    human_readable = []
    if raw_response:
        for template in raw_response.get('Templates'):
            entry_context.append(assign_params(**{
                "Name": template.get('Name'),
                "CAs": template.get('CAs')[0].get('Name')
            }))
            human_readable.append(assign_params(**{
                "Name": template.get('Name'),
                "CAs": template.get('CAs')[0].get('Name')
            }))
    return entry_context, human_readable


def post_enrollment_csr_command_ec(raw_response: dict) -> Tuple[list, list]:
    """
        Parse the post enrollment CSR
        > Parse the Certificate received from keyFactor
    Args:
        raw_response: Certificate Info received from keyFactor

    Returns:
        List of Certificate info

    Test Cert:
    "#CN=Jun30.Changliutest.org,OU=Corporate Account,O=Fidelity National Information Services,L=Jacksonville,C=US-----BEGIN CERTIFICATE-----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-----END CERTIFICATE-----"
    """
    entry_context = []
    human_readable = []
    if raw_response:
        certificateinfo = raw_response.get("CertificateInformation")
        regex = r"-----BEGIN CERTIFICATE-----[\w\W]*END CERTIFICATE-----"
        formated_certs = []

        certificates = certificateinfo.get('Certificates')

        for certs in certificates:

            matches = re.findall(regex, certs)
            formated_certs = formated_certs + matches
        new_formated_certs = []
        for cert in formated_certs:
            new_formated_certs.append(cert.replace('\r\n', ' '))
        formated_chain = new_formated_certs[1] + ' ' + new_formated_certs[2]

        entry_context.append(assign_params(**{
            "SerialNumber": certificateinfo.get('SerialNumber'),
            "IssuerDN": certificateinfo.get('IssuerDN'),
            "Thumbprint": certificateinfo.get('Thumbprint'),
            "KeyfactorID": certificateinfo.get('KeyfactorID'),
            "KeyfactorRequestId": certificateinfo.get('KeyfactorRequestId'),
            "Certificates": certificateinfo.get('Certificates'),
            "RequestDisposition": certificateinfo.get('RequestDisposition'),
            "DispositionMessage": certificateinfo.get('DispositionMessage'),
            "EnrollmentContext": certificateinfo.get('EnrollmentContext'),
            "formated_certs": new_formated_certs,
            "formated_cert": new_formated_certs[0],
            "formated_chain": formated_chain,
        }))
        human_readable.append(assign_params(**{
            "SerialNumber": certificateinfo.get('SerialNumber'),
            "IssuerDN": certificateinfo.get('IssuerDN'),
            "Thumbprint": certificateinfo.get('Thumbprint'),
            "KeyfactorID": certificateinfo.get('KeyfactorID'),
            "KeyfactorRequestId": certificateinfo.get('KeyfactorRequestId'),
            "Certificates": certificateinfo.get('Certificates'),
            "RequestDisposition": certificateinfo.get('RequestDisposition'),
            "DispositionMessage": certificateinfo.get('DispositionMessage'),
            "EnrollmentContext": certificateinfo.get('EnrollmentContext'),
            "formated_certs": formated_certs,
            "formated_cert": formated_certs[0],
            "formated_chain": formated_chain,
        }))

    return entry_context, human_readable


''' COMMANDS '''


@logger
def post_enrollment_csr_command(client: Client,
                                csr_base64: str,
                                cert_authority: str,
                                include_chain: str,
                                template: str,
                                metadata: dict,
                                keyAlgorithm: str,
                                sans_ip4: List = ''
                                ) -> dict:
    """
        Post Enrollment CSR
        Send the certifcate CSR and return the certificate created
    Args:
        client: Client object with request
        csr_base64
        cert_authority
        include_chain
        template
        sans_ip4
        keyAlgorithm
        metadata

    Returns:
        human readable (markdown format), entry context and raw response
    """
    if keyAlgorithm != '':
        csr_base64_changed = ''
        for csr in csr_base64['csrs']:
            if csr['keyAlgorithm'] == keyAlgorithm:
                csr_base64_changed = csr['csr']
        csr_base64 = csr_base64_changed
    now_iso8601 = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    raw_response: Dict = client.post_enrollment_csr(csr_base64=csr_base64,
                                                    cert_authority=cert_authority,
                                                    include_chain=include_chain,
                                                    time_stamp=now_iso8601,
                                                    template=template,
                                                    keyAlgorithm=keyAlgorithm,
                                                    sans_ip4=sans_ip4,
                                                    metadata=metadata
                                                    )
    if raw_response:
        title = f'{INTEGRATION_NAME} - Post Enrollment CSR'
        entry_context, human_readable_ec = post_enrollment_csr_command_ec(raw_response)

        context_entry: Dict = {
            f"{INTEGRATION_CONTEXT_NAME}.CertInfo.Lists(val.UniqueID && val.UniqueID == obj.UniqueID &&"
            f" val.UpdateDate && val.UpdateDate == obj.UpdateDate)": entry_context
        }

        human_readable = tableToMarkdown(name=title,
                                         t=human_readable_ec,
                                         removeNull=True)
        return human_readable, context_entry, raw_response


@logger
def get_enrollment_csr_context_my_command(client: Client, *_) -> Tuple[List, List, dict]:
    """Get all Enrollment CSR Context My (templates)

    Args:
        client: Client object with request

    Returns:
        human readable (markdown format), entry context and raw response
    """

    raw_response: dict = client.get_enrollment_csr_context_my()

    if raw_response:
        title = f'{INTEGRATION_NAME} - Get enrollment csr context my'
        entry_context, human_readable_ec = get_enrollment_csr_context_my_ec(raw_response)
        context_entry: Dict = {
            f"{INTEGRATION_CONTEXT_NAME}.CSRTemplate.Lists(val.UniqueID && val.UniqueID == obj.UniqueID &&"
            f" val.UpdateDate && val.UpdateDate == obj.UpdateDate)": entry_context
        }
        human_readable = tableToMarkdown(name=title,
                                         t=human_readable_ec,
                                         removeNull=True)
        return human_readable, context_entry, raw_response
    else:
        return f'{INTEGRATION_NAME} - Could not find any results for given query', {}, {}


@logger
def test_module_command(client: Client, *_) -> Tuple[None, None, str]:
    """Performs a basic GET request to check if the API is reachable and authentication is successful.

    Args:
        client: Client object with request
        *_: Usually demisto.args()

    Returns:
        'ok' if test successful.

    Raises:
        DemistoException: If test failed.
    """
    results = client.test_module()
    if 'Templates' or 'CertificateInformation' in results:
        return None, None, 'ok'
    raise DemistoException(f'Test module failed, {results}')


def main():
    params = demisto.params()
    verify_ssl = not params.get('insecure', False)
    proxy = params.get('proxy')
    username = params.get('username')
    password = params.get('password')
    client = Client(
        base_url=params.get('host'),
        verify=verify_ssl,
        proxy=proxy,
        auth=(username, password)
    )
    command = demisto.command()
    commands = {
        'test-module': test_module_command,
        f'{INTEGRATION_COMMAND_NAME}-get-enrollment-csr-context-my': get_enrollment_csr_context_my_command,
        f'{INTEGRATION_COMMAND_NAME}-post-enrollment-csr': post_enrollment_csr_command
    }

    try:
        readable_output, outputs, raw_response = commands[command](client=client, **demisto.args())
        return_outputs(readable_output, outputs, raw_response)

    except Exception as e:
        err_msg = f'Error in {INTEGRATION_NAME} Integration [{e}]'
        return_error(err_msg, error=e)


if __name__ == 'builtins':
    main()
