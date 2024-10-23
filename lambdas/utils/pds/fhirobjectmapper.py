"""Provides functionality to map PDS FHIR data to required API FHIR Responses
"""

from datetime import datetime, timezone
from urllib.parse import urlparse

from fhirclient.models.bundle import Bundle, BundleEntry, BundleEntrySearch, BundleLink
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.fhirreference import FHIRReference
from fhirclient.models.identifier import Identifier
from fhirclient.models.operationoutcome import OperationOutcome, OperationOutcomeIssue
from fhirclient.models.patient import Patient
from fhirclient.models.relatedperson import RelatedPerson

from lambdas.utils.pds.errors import OperationalOutcomeResult


class FHIRObjectMapper:
    """Provides functionality to map PDS FHIR data to required API FHIR Responses"""

    SYSTEM_NHS_NUMBER = "https://fhir.nhs.uk/Id/nhs-number"
    RESOURCE_TYPE_PATIENT = "Patient"

    # Surpressing the http warning for SYSTEM_V3_ROLE_CODE as the value is defined
    # in the FHIR standard and cannot be changed to be https
    SYSTEM_V3_ROLE_CODE = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"  # NOSONAR

    def filter_patient_properties(self, pds_patient: Patient) -> Patient:
        """Filters PDS patient properties to extract relevant information for a FHIR API response.

        Args:
            pds_patient (Patient): PDS Patient record

        Returns:
            Patient: Filtered patient information.
        """

        if pds_patient is None:
            return None

        patient = Patient()

        patient.id = pds_patient.id

        identifier = Identifier(
            {"value": pds_patient.identifier[0].value, "system": self.SYSTEM_NHS_NUMBER}
        )
        patient.identifier = [identifier]

        patient.birthDate = pds_patient.birthDate
        patient.name = pds_patient.name
        patient.resource_type = self.RESOURCE_TYPE_PATIENT

        return patient

    def filter_related_person_properties(
        self, patient: Patient, related: RelatedPerson
    ) -> RelatedPerson:
        """Filters PDS related person properties to extract relevant information
        for a FHIR API response.

        Args:
            patient (Patient): PDS patient record
            related (RelatedPerson): PDS related person record

        Returns:
            RelatedPerson: Filtered related person record
        """
        if related is None:
            return None

        rtn = RelatedPerson()
        rtn.id = related.id
        rtn.identifier = related.identifier
        rtn.patient = self.__create_related_patient(patient)

        relationships = related.relationship

        # Enforce the correct system property value for 'MTH' relationships
        # PDS value of system property for 'MTH' is not FHIR compliant

        for relationship in relationships:
            relationship_codes = []
            for coding in relationship.coding:
                if coding.code == "MTH":
                    coding.system = self.SYSTEM_V3_ROLE_CODE
                    relationship_codes.append(coding)

            relationship.coding = relationship_codes

        rtn.relationship = relationships

        return rtn

    def create_related_person_bundle(
        self,
        relations,
        original_request_url: str,
        pds_proxy_identifier: Identifier,
    ) -> Bundle:
        """Creates a bundle based on the patient and relationship data

        Args:
            relations (Patient, RelatedPerson, bool): Tuple containing
                the Patient and the related person record
            original_request_url (str): Link url of original request
            proxy_identifier (Identifier): Proxy identifier

        Returns:
            Bundle: Bundle based on the patient and related person data
        """

        base_url = (
            self.extract_base_url(original_request_url)
            + "/validated-relationships/FHIR/R4/"
        )

        bundle = Bundle()
        entries = []
        timestamp = FHIRDate()
        timestamp.date = datetime.now(timezone.utc)

        for relation in relations:
            patient = relation[0]

            if relation[2]:
                patient_entry = BundleEntry()
                patient_entry.resource = self.filter_patient_properties(patient)
                patient_entry.search = BundleEntrySearch({"mode": "include"})
                patient_entry.fullUrl = (
                    base_url + "Patient/" + patient_entry.resource.id
                )
                entries.append(patient_entry)

            related = relation[1]
            relationship_entry = BundleEntry()
            relationship_entry.resource = self.filter_related_person_properties(
                patient, related
            )
            relationship_entry.resource.identifier = [
                self.create_proxy_identifier(pds_proxy_identifier)
            ]
            relationship_entry.search = BundleEntrySearch({"mode": "match"})
            relationship_entry.fullUrl = (
                base_url + "RelatedPerson/" + relationship_entry.resource.id
            )
            entries.append(relationship_entry)

        bundle_link = BundleLink()
        bundle_link.relation = "self"
        bundle_link.url = original_request_url
        link_arr = []
        link_arr.append(bundle_link)

        bundle.link = link_arr
        bundle.entry = entries
        bundle.type = "searchset"
        bundle.total = len(entries)
        bundle.timestamp = timestamp

        return bundle

    def create_operation_outcome(
        self, outcome: OperationalOutcomeResult
    ) -> OperationOutcome:
        """Generates an operation outcome result based on the supplied input.

        Args:
            code (HTTPStatus): The HTTPStatus code that indicates the error.
            display (str): The string message to include in the operation outcome.

        Returns:
            OperationOutcome: An OperationOutcome based on the supplied input.
        """

        coding = Coding()
        coding.system = outcome["system"]
        coding.version = outcome["version"]
        coding.code = outcome["response_code"]
        coding.display = outcome["display"]

        details = CodeableConcept()
        details.coding = []
        details.coding.append(coding)

        issue = OperationOutcomeIssue()
        issue.severity = outcome["severity"]
        issue.code = outcome["issue_code"]
        issue.diagnostics = outcome["audit_msg"]
        issue.details = details

        rtn = OperationOutcome()
        rtn.issue = []
        rtn.issue.append(issue)
        return rtn

    def extract_base_url(self, url: str) -> str:
        """Extracts the base URL from the given URL.

        Args:
            url (str): URL input to extract the base URL from.

        Returns:
            str: Extracted base URL.
        """
        parsed_url = urlparse(url)
        if parsed_url.netloc:
            return f"https://{parsed_url.netloc}"

        return ""

    def __create_related_patient(self, pds_patient: Patient) -> FHIRReference:
        """Generates FHIRReference object based on the patient information

        Args:
            pds_patient (Patient): Patient to generate from

        Returns:
            FHIRReference: Generated FHIRReference
        """
        rtn = FHIRReference()

        rtn.type = self.RESOURCE_TYPE_PATIENT
        rtn.identifier = Identifier(
            {"system": self.SYSTEM_NHS_NUMBER, "value": pds_patient.identifier[0].value}
        )
        return rtn

    def create_proxy_identifier(self, pds_proxy_identifier: Identifier) -> Identifier:
        """Generates an Identifier object based on the proxy identifier information

        Args:
            pds_proxy_identifier (dict): Proxy identifier information

        Returns:
            Identifier: Generated Identifier object
        """
        return Identifier(
            {
                "system": pds_proxy_identifier.system,
                "value": pds_proxy_identifier.value,
            }
        )
