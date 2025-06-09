# config.py

# --- Configuration Constants ---
CONFIG_FILE_NAME = "app_config.json"
DEFAULT_LOGO_PATH = "logo.png"
DEFAULT_ICON_PATH = "logo.ico"

# --- Standard Subfolder Names ---
SUBFOLDER_NAMES = {
    "departmentDetails": "Department_Documents",
    "oemVendorDetails": "OEM_Vendor_Documents",
    "proposalDocuments": "Proposal_Documents",
    "ceoApprovalDocuments": "CEO_Approval_Documents",
    "workOrderDocuments": "Work_Order_Documents",
    "scopeOfWorkDetails": "Scope_Of_Work_Documents",
    "oenDetails": "OEN_Documents",
    "miscDocuments": "Misc_Documents"
}

# --- Initial Project Data Structure ---
initial_project_data_template = {
  'projectName': '', 'projectLead': '', 'status': 'PENDING',
  'departmentDetails': { 'name': '', 'address': '', 'memoId': '', 'memoDate': '', 'documents': [] },
  'oemVendorDetails': { 'oemName': '', 'vendorName': '', 'price': '', 'date': '', 'documents': [] },
  'scopeOfWorkDetails': { 'scope': '', 'documents': [] },
  'proposalOrderDetails': {
    'officeProposalId': '', 'proposalDate': '', 'proposalDocuments': [],
    'ceoApprovalDocuments': [],
    'departmentWorkOrderId': '', 'issuingDate': '', 'workOrderDocuments': []
  },
  'billOfMaterials': { 'items': [], 'amountInWords': '' },
  'oenDetails': { 'oenRegistrationNo': '', 'registrationDate': '', 'officeOenNo': '', 'oenDate': '', 'documents': [] },
  'financialDetails': { 'transactions': [], 'totalPendingInWords': '', 'totalAmountReceived': 0.0, 'totalAmountPending': 0.0 },
  'workingFolder': '', 'projectFolderPath': '', 'createdAt': '', 'updatedAt': '',
}