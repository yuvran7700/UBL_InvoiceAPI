# UBL Invoice API

A RESTful API that enables Small to Medium-sized Enterprises (SMEs) to generate ATO-compliant UBL invoices from UBL order documents. Built with Python and FastAPI, deployed on Heroku, with Amazon DynamoDB for persistence.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Reference](#api-reference)
  - [Account Management](#account-management)
  - [Order Document Upload](#order-document-upload)
  - [Invoice Generation](#invoice-generation)
  - [Invoice Management](#invoice-management)
- [Features](#features)
- [Non-Functional Requirements](#non-functional-requirements)

---

## Overview

With the rise of Industry 4.0, SMEs struggle to participate in digital collaborations due to the high cost and complexity of compliant invoicing systems. This API addresses that by:

- Accepting UBL order documents (XML/JSON) and automatically converting them into ATO-compliant invoices
- Validating invoices against ATO regulations, UBL 2.1, PEPPOL, and Australian Business Rules (ABR) schemas
- Allowing users to manually edit, tag, store, and manage invoices
- Supporting advanced features like partial payments, instalment plans, credit/debit notes, and invoice analytics

---

## Tech Stack

| Layer | Technology |
|---|---|
| Application | Python |
| Service | FastAPI |
| Persistence | Amazon DynamoDB |
| Deployment | Heroku |

---

## Getting Started

### Prerequisites

- Python 3.9+
- AWS credentials configured (for DynamoDB)
- Heroku CLI (for deployment)

### Installation

```bash
# Clone the repository
git clone https://github.com/yuvran7700/UBL_InvoiceAPI.git
cd UBL_InvoiceAPI

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload
```

### Environment Variables

Create a `.env` file in the root directory:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
DYNAMODB_TABLE=your_table_name
JWT_SECRET=your_jwt_secret
```

---

## API Reference

Authentication is handled via JWT tokens. Include the token in the `authToken` parameter or Authorization header where required.

### Account Management

| Method | Route | Description |
|---|---|---|
| POST | `/v1/admin/register` | Register a new user with business name, email, password, and ABN |
| POST | `/v1/admin/login` | Log in and receive an auth token |
| POST | `/v1/admin/logout` | Invalidate the current session token |
| PUT | `/v1/admin/password` | Reset password via email |
| PUT | `/v1/admin/email` | Update account email |
| PUT | `/v1/admin/username` | Update account username |
| GET | `/v1/admin/abn/validate` | Validate an ABN via the ATO ABN Lookup API |
| GET | `/v1/admin/email/validate` | Check if an email exists in the system |
| POST | `/v1/admin/user/password/validate` | Validate username/password combination |
| GET | `/v1/admin/validate/login` | Verify a token is valid and active |
| GET | `/v1/admin/validate/user` | Extract and validate user identity from a token |
| GET | `/v1/admin/validate/logout` | Confirm a token has been invalidated |

### Order Document Upload

| Method | Route | Description |
|---|---|---|
| POST | `/v1/admin/order/upload` | Upload a UBL order document (XML or JSON) |
| POST | `/v1/admin/duplicate/validate` | Check for duplicate order submissions |
| POST | `/v1/admin/file/validate` | Validate uploaded file format |

### Invoice Generation

#### Parsing & Draft Generation

| Method | Route | Description |
|---|---|---|
| POST | `/v1/admin/order/parse` | Extract relevant fields from the order document |
| POST | `/v1/admin/order/generate-draft-invoice` | Generate a draft invoice from parsed order data |

#### Data Transfer (Order → Invoice)

| Method | Route | Description |
|---|---|---|
| GET | `/v1/invoice/validation-summary` | View validation report after data transfer |
| PUT | `/v1/invoice/edit-errors` | Manually correct errors in the draft invoice |
| PUT | `/v1/invoice/copy-buyer-seller` | Copy buyer/seller details from order to invoice |
| PUT | `/v1/invoice/copy-payment-terms` | Copy payment terms from order to invoice |
| PUT | `/v1/invoice/copy-delivery-info` | Copy delivery information from order to invoice |
| PUT | `/v1/invoice/copy-invoice-lines` | Copy line items from order to invoice |
| PUT | `/v1/invoice/copy-total` | Calculate and copy line extension totals |
| PUT | `/v1/invoice/copy-tax-currency` | Copy tax and currency data, calculate TaxTotal |
| PUT | `/v1/invoice/copy-notes` | Copy notes from order to invoice |
| PUT | `/v1/invoice/calculate-line-amount` | Calculate line extension amount per line item |

#### Transfer Validation

| Method | Route | Description |
|---|---|---|
| GET | `/v1/invoice/validate-tax-currency` | Validate tax/currency data was transferred correctly |
| GET | `/v1/invoice/validate-payment-terms` | Validate payment terms were copied |
| GET | `/v1/invoice/validate-notes` | Validate notes were transferred |
| GET | `/v1/invoice/validate-line-extension` | Validate line extension amounts were copied |
| GET | `/v1/invoice/validate-line-extension-calculation` | Validate line extension calculations are correct |
| GET | `/v1/invoice/validate-invoice-lines` | Validate all invoice lines were copied |
| GET | `/v1/invoice/validate-delivery-info` | Validate delivery info was transferred |
| GET | `/v1/invoice/validate-buyer-seller` | Validate buyer/seller info was transferred |

#### User-Input Invoice Fields

| Method | Route | Description |
|---|---|---|
| PUT | `/v1/invoice/update` | Update payment terms on the invoice |
| POST | `/v1/invoice/create-id` | Generate a unique Invoice ID |
| POST | `/v1/invoice/create-issue-date` | Set the invoice issue date |
| POST | `/v1/invoice/create-due-date` | Calculate and set the payment due date |
| POST | `/v1/invoice/calculate-totals` | Calculate tax-exclusive, tax-inclusive, and payable amounts |
| POST | `/v1/invoice/create-tax-details` | Calculate and add TaxTotal and TaxSubtotal |
| POST | `/v1/invoice/create-payment-terms` | Add payment terms and due date to the invoice |
| POST | `/v1/invoice/create-quantity` | Record invoiced quantity per line item |
| POST | `/v1/invoice/create-allowance-charges` | Add allowances/charges (discounts, fees) |
| POST | `/v1/invoice/create-payment-method` | Specify payment method and bank account details |
| POST | `/v1/invoice/create-payment-instructions` | Add payment instructions |
| POST | `/v1/invoice/create-legal-reference` | Set invoice type code (commercial invoice, credit note, etc.) |
| POST | `/v1/invoice/create-contract-reference` | Add contract reference if applicable |
| POST | `/v1/invoice/create-order-reference` | Add order and delivery note references |
| GET | `/v1/invoice/display` | Display a finalised invoice for review |

#### Schema Compliance Validation

| Method | Route | Description |
|---|---|---|
| GET | `/v1/invoice/validate-syntax-schema` | Validate XML structure and required tags |
| GET | `/v1/invoice/validate-header` | Validate required invoice header elements |
| GET | `/v1/invoice/validate-abr` | Validate against Australian Business Rules (ABN, GST, currency) |
| GET | `/v1/invoice/validate-peppol` | Validate against PEPPOL e-invoicing standard |
| GET | `/v1/invoice/validate-xsd` | Validate against UBL 2.1 XSD schema |

### Invoice Management

#### Storage & Organisation

| Method | Route | Description |
|---|---|---|
| POST | `/v1/admin/invoice/store` | Store invoice linked to user profile |
| GET | `/v1/admin/invoice/list` | List all invoices for the authenticated user |
| PUT | `/v1/admin/invoice/tag` | Apply a tag to an invoice (e.g. overdue, credit, debit) |
| PUT | `/v1/admin/invoice/partial-pay` | Record partial payments on an invoice |
| PUT | `/v1/admin/invoice/add-credit-debit` | Attach credit or debit note to an invoice |

#### Medium Features

| Method | Route | Description |
|---|---|---|
| PUT | `/v1/admin/invoice/installment-plan` | Set up an instalment payment schedule |
| PUT | `/v1/admin/invoice/password-protection` | Password-protect an invoice |
| GET | `/v1/admin/invoice/filter` | Filter invoices by tag or ID |
| PUT | `/v1/admin/invoice/credit-debit/update` | Update existing credit/debit notes |

#### Stretch Features

| Method | Route | Description |
|---|---|---|
| POST | `/v1/admin/notify` | Send a notification to a user |
| PUT | `/v1/admin/external-email` | Grant external email access to an invoice |
| POST | `/v1/admin/analytics` | Generate an invoice analytics report |
| POST | `/v1/admin/merge` | Merge two invoices into one |

---

## Features

**MVP**
- User account creation with ABN validation via the ATO Lookup API
- JWT-based authentication and session management
- UBL order document upload (XML/JSON) with duplicate detection
- Automatic conversion of order documents to draft UBL 2.1 invoices
- Full validation against ATO, ABR, PEPPOL, and UBL XSD schemas

**Major**
- Invoice storage linked to user profiles
- Partial payment support
- Invoice tagging (overdue, credit, debit, etc.)
- Credit and debit note creation

**Medium**
- Instalment payment plans
- Password-protected invoices
- Invoice filtering by tag or ID
- Credit/debit note maintenance

**Stretch**
- User notifications
- External email access sharing
- Invoice analytics and reporting
- Invoice merging

---

## Non-Functional Requirements

- **Scalability:** Supports high volumes of invoice processing without performance degradation
- **Security:** JWT authentication; sensitive financial data protected in compliance with ATO regulations
- **Performance:** Invoice creation and validation completed in under 2 seconds per request
- **Error Handling:** Detailed validation feedback for all incorrect or missing fields
