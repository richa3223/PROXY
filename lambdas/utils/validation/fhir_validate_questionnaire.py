""" Provides functionality to validate a FHIR questionnaire """

import json

from fhirclient.models.fhirabstractbase import FHIRValidationError
from fhirclient.models.questionnaireresponse import QuestionnaireResponse


class FHIRValidateQuestionnaire:
    """Provides functionality to validate a FHIR questionnaire"""

    def validate_questionnaire_response(self, questionnaire_resp: str) -> bool:
        """
        Validates questionnaire response
        Ensures the value is not none, is json and is a fhir questionnaireresponse

        Args:
            questionnaire_resp (str): The questionnaire resp string to validate

        Returns:
            bool: True if questionnaire response is valid, False otherwise
        """

        if questionnaire_resp is None:
            return False

        if type(questionnaire_resp) is str:
            try:
                response_json = json.loads(questionnaire_resp)
            except ValueError:
                return False
        else:
            response_json = questionnaire_resp

        try:
            resp = QuestionnaireResponse(response_json)
            # Further checks to be carried out on questionnaire
            if resp:
                return True
        except FHIRValidationError:
            return False

        return False
