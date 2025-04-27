import requests
from src.exceptions.email_exceptions import EmailDoesntExist, EmailInvalidDomain, EmailInvalidFormat, EmailInvalidMX, EmailMissingFields
from pydantic import EmailStr
from src.domain.models.email_models import SendEmailModel
from src.validators.email_field_checker import MissingEmailFieldChecker

def email_validator(email: EmailStr): 

    url = "https://validect-email-verification-v1.p.rapidapi.com/v1/verify"

    querystring = {"email": email}

    headers = {
        "x-rapidapi-key": "f4b83ae637msh41700977eb845f6p15bfd1jsn8995c2dc4201",
        "x-rapidapi-host": "validect-email-verification-v1.p.rapidapi.com"
    }

    try: 
        response = requests.get(url, headers=headers, params=querystring)
        return response
    except Exception as e:
        print("Error during email validation:", str(e))

def validate_email(email: EmailStr):
    response = email_validator(email)
    data = response.json()
    if 'reason' in data:
        if data['reason'] == "invalid_domain":
                raise EmailInvalidDomain(data['domain'])
        if data['reason'] == "invalid_mx_record":
                raise EmailInvalidMX(data['domain'])
        if data['reason'] == "rejected_email":
                raise EmailDoesntExist(email)
        if data['reason'] == "invalid_syntax":
                raise EmailInvalidFormat(email)
    return response

def check_fields(email: SendEmailModel):
    missing_report = MissingEmailFieldChecker(email).run()
    if missing_report.missing_email_fields:
        raise EmailMissingFields(missing_report)
    