// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// ContractPatient: Patient Registration and Information Management
contract ContractPatient {
    struct Patient {
        address walletAddress;
        string name;
        string dateOfBirth;
        string gender;
        string bloodGroup;
        string homeAddress;
        string email;
        string hhNumber;
        bytes32 passwordHash;
    }

    mapping(string => Patient) private patients;
    mapping(string => bool) public isPatientRegistered;
    
    event PatientRegistered(string indexed hhNumber, string name, address walletAddress);
    event PatientInfoUpdated(string indexed hhNumber);

    // Register a new patient
    function registerPatient(
        string memory _name,
        string memory _dateOfBirth,
        string memory _gender,
        string memory _bloodGroup,
        string memory _homeAddress,
        string memory _email,
        string memory _hhNumber,
        string memory _password
    ) external {
        require(!isPatientRegistered[_hhNumber], "Patient already registered");

        Patient memory newPatient = Patient({
            walletAddress: msg.sender,
            name: _name,
            dateOfBirth: _dateOfBirth,
            gender: _gender,
            bloodGroup: _bloodGroup,
            homeAddress: _homeAddress,
            email: _email,
            hhNumber: _hhNumber,
            passwordHash: keccak256(abi.encodePacked(_password))
        });

        patients[_hhNumber] = newPatient;
        isPatientRegistered[_hhNumber] = true;
        
        emit PatientRegistered(_hhNumber, _name, msg.sender);
    }

    // Update patient information
    function updatePatientInfo(
        string memory _hhNumber,
        string memory _homeAddress,
        string memory _email
    ) external {
        require(isPatientRegistered[_hhNumber], "Patient not registered");
        require(patients[_hhNumber].walletAddress == msg.sender, "Unauthorized access");

        patients[_hhNumber].homeAddress = _homeAddress;
        patients[_hhNumber].email = _email;

        emit PatientInfoUpdated(_hhNumber);
    }

    // Validate patient login
    function validatePatientLogin(string memory _hhNumber, string memory _password) 
        external 
        view 
        returns (bool) 
    {
        require(isPatientRegistered[_hhNumber], "Patient not registered");
        return patients[_hhNumber].passwordHash == keccak256(abi.encodePacked(_password));
    }

    // Get patient details (limited access)
    function getPatientDetails(string memory _hhNumber) 
        external 
        view 
        returns (
            address walletAddress,
            string memory name,
            string memory dateOfBirth,
            string memory gender,
            string memory bloodGroup,
            string memory homeAddress,
            string memory email,
            string memory hhNumber
        ) 
    {
        require(isPatientRegistered[_hhNumber], "Patient not registered");
        Patient memory patient = patients[_hhNumber];
        return (
            patient.walletAddress,
            patient.name,
            patient.dateOfBirth,
            patient.gender,
            patient.bloodGroup,
            patient.homeAddress,
            patient.email,
            patient.hhNumber
        );
    }
}

// ContractDoctor: Doctor Registration and Medical Record Access Management
contract ContractDoctor {
    struct Doctor {
        address walletAddress;
        string name;
        string specialization;
        string hospitalName;
        string hhNumber;
        bytes32 passwordHash;
    }

    struct AccessPermission {
        string patientHhNumber;
        bool hasAccess;
        uint256 grantTimestamp;
    }

    struct MedicalRecord {
    string patientHhNumber;
    string doctorHhNumber;
    string recordHash;
    string notes;
    string encryptedData;
    uint256 timestamp;
    bool isDeleted;
    }   

    mapping(string => Doctor) private doctors;
    mapping(string => bool) public isDoctorRegistered;
    mapping(string => mapping(string => AccessPermission)) private patientAccessMap;

    // Mapping to track all patients that granted access to a doctor
    mapping(string => string[]) private doctorPatients;

    // Mapping from patient HH number to array of medical record IDs
    mapping(string => uint256[]) private patientRecords;

    event DoctorRegistered(string indexed hhNumber, string name, address walletAddress);
    event AccessPermissionChanged(string indexed patientHhNumber, string indexed doctorHhNumber, bool granted);

    // Add these new events inside the ContractDoctor contract
    event MedicalRecordCreated(
        uint256 indexed recordId,
        string patientHhNumber,
        string doctorHhNumber,
        uint256 timestamp
    );

    event MedicalRecordDeleted(
        uint256 indexed recordId,
        string patientHhNumber,
        string doctorHhNumber,
        uint256 timestamp
    );

    // Add this at the beginning of the contract
    string[] private registeredDoctors;

    // Array to store all medical records
    MedicalRecord[] private medicalRecords;

    // Register a new doctor
    function registerDoctor(
        string memory _name,
        string memory _specialization,
        string memory _hospitalName,
        string memory _hhNumber,
        string memory _password
    ) external {
        require(!isDoctorRegistered[_hhNumber], "Doctor already registered");
        registeredDoctors.push(_hhNumber);

        Doctor memory newDoctor = Doctor({
            walletAddress: msg.sender,
            name: _name,
            specialization: _specialization,
            hospitalName: _hospitalName,
            hhNumber: _hhNumber,
            passwordHash: keccak256(abi.encodePacked(_password))
        });

        doctors[_hhNumber] = newDoctor;
        isDoctorRegistered[_hhNumber] = true;

        emit DoctorRegistered(_hhNumber, _name, msg.sender);
    }
    // Validate doctor login
    function validateDoctorLogin(string memory _hhNumber, string memory _password) 
        external 
        view 
        returns (bool) 
    {
        require(isDoctorRegistered[_hhNumber], "Doctor not registered");
        return doctors[_hhNumber].passwordHash == keccak256(abi.encodePacked(_password));
    }

    // Grant access to a patient's medical record
    function grantPatientAccess(
        string memory _patientHhNumber, 
        string memory _doctorHhNumber
    ) external {
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");

        patientAccessMap[_patientHhNumber][_doctorHhNumber] = AccessPermission({
            patientHhNumber: _patientHhNumber,
            hasAccess: true,
            grantTimestamp: block.timestamp
        });

        // Add patient to doctor's patient list if not already present
        bool patientExists = false;
        string[] storage patients = doctorPatients[_doctorHhNumber];
        for(uint i = 0; i < patients.length; i++) {
            if(keccak256(abi.encodePacked(patients[i])) == keccak256(abi.encodePacked(_patientHhNumber))) {
                patientExists = true;
                break;
            }
        }
        if(!patientExists) {
            doctorPatients[_doctorHhNumber].push(_patientHhNumber);
        }

        emit AccessPermissionChanged(_patientHhNumber, _doctorHhNumber, true);
    }

    // Get all patients that granted access to a doctor
    function getDoctorPatients(string memory _doctorHhNumber) 
        external 
        view 
        returns (string[] memory) 
    {
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");
        return doctorPatients[_doctorHhNumber];
    }

    // Revoke access to a patient's medical record
    function revokePatientAccess(
        string memory _patientHhNumber, 
        string memory _doctorHhNumber
    ) external {
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");

        patientAccessMap[_patientHhNumber][_doctorHhNumber].hasAccess = false;

        emit AccessPermissionChanged(_patientHhNumber, _doctorHhNumber, false);
    }

    // Check if a doctor has access to a patient's record
    function checkPatientAccess(
        string memory _patientHhNumber, 
        string memory _doctorHhNumber
    ) external view returns (bool) {
        return patientAccessMap[_patientHhNumber][_doctorHhNumber].hasAccess;
    }

    // Get doctor details (limited access)
    function getDoctorDetails(string memory _hhNumber) 
        external 
        view 
        returns (
            address walletAddress,
            string memory name,
            string memory specialization,
            string memory hospitalName,
            string memory hhNumber
        ) 
    {
        require(isDoctorRegistered[_hhNumber], "Doctor not registered");
        Doctor memory doctor = doctors[_hhNumber];
        return (
            doctor.walletAddress,
            doctor.name,
            doctor.specialization,
            doctor.hospitalName,
            doctor.hhNumber
        );
    }

    // Get all doctors with access to a patient
    function getDoctorsWithAccess(string memory _patientHhNumber) 
        external 
        view 
        returns (string[] memory doctorHhNumbers) 
    {
        uint256 count = 0;
        string[] memory tempDoctors = new string[](1000); // Assuming max 1000 doctors
        
        // First pass: count doctors with access
        for (uint i = 0; i < registeredDoctors.length; i++) {
            string memory doctorHhNumber = registeredDoctors[i];
            if (patientAccessMap[_patientHhNumber][doctorHhNumber].hasAccess) {
                tempDoctors[count] = doctorHhNumber;
                count++;
            }
        }
        
        // Create properly sized array
        doctorHhNumbers = new string[](count);
        for (uint i = 0; i < count; i++) {
            doctorHhNumbers[i] = tempDoctors[i];
        }
        
        return doctorHhNumbers;
    }

    // Create a new medical record
    function createMedicalRecord(
        string memory _patientHhNumber,
        string memory _doctorHhNumber,
        string memory _recordHash,
        string memory _notes,
        string memory _encryptedData
    ) external returns (uint256) {
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");
        require(patientAccessMap[_patientHhNumber][_doctorHhNumber].hasAccess, "Doctor does not have access");

        MedicalRecord memory newRecord = MedicalRecord({
            patientHhNumber: _patientHhNumber,
            doctorHhNumber: _doctorHhNumber,
            recordHash: _recordHash,
            notes: _notes,
            encryptedData: _encryptedData,
            timestamp: block.timestamp,
            isDeleted: false
        });

        medicalRecords.push(newRecord);
        uint256 recordId = medicalRecords.length - 1;
        patientRecords[_patientHhNumber].push(recordId);

        emit MedicalRecordCreated(recordId, _patientHhNumber, _doctorHhNumber, block.timestamp);
        return recordId;
    }

    // Add this function to the ContractDoctor contract
    function updateMedicalRecord(
        string memory _patientHhNumber,
        string memory _doctorHhNumber,
        string memory _oldRecordHash,
        string memory _newRecordHash,
        string memory _notes,
        string memory _encryptedData
    ) external returns (bool) {
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");
        require(patientAccessMap[_patientHhNumber][_doctorHhNumber].hasAccess, "Doctor does not have access");

        uint256[] memory recordIds = patientRecords[_patientHhNumber];
        bool recordFound = false;
        
        for (uint256 i = 0; i < recordIds.length; i++) {
            MedicalRecord storage record = medicalRecords[recordIds[i]];
            if (!record.isDeleted && 
                keccak256(abi.encodePacked(record.recordHash)) == keccak256(abi.encodePacked(_oldRecordHash))) {
                
                // Verify the record belongs to this doctor
                require(
                    keccak256(abi.encodePacked(record.doctorHhNumber)) == keccak256(abi.encodePacked(_doctorHhNumber)),
                    "Only the creator can update the record"
                );
                
                // Update the record
                record.recordHash = _newRecordHash;
                record.notes = _notes;
                record.encryptedData = _encryptedData;
                record.timestamp = block.timestamp;
                
                recordFound = true;
                break;
            }
        }
        
        require(recordFound, "Record not found");
        return true;
    }

    // Get all medical records for a patient
    function getPatientMedicalRecords(string memory _patientHhNumber, string memory _doctorHhNumber) 
        external 
        view 
        returns (MedicalRecord[] memory) 
    {
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");
        require(patientAccessMap[_patientHhNumber][_doctorHhNumber].hasAccess, "Doctor does not have access");

        uint256[] memory recordIds = patientRecords[_patientHhNumber];
        uint256 activeRecordCount = 0;

        // Count active records
        for (uint256 i = 0; i < recordIds.length; i++) {
            if (!medicalRecords[recordIds[i]].isDeleted) {
                activeRecordCount++;
            }
        }

        // Create array of active records
        MedicalRecord[] memory activeRecords = new MedicalRecord[](activeRecordCount);
        uint256 currentIndex = 0;

        for (uint256 i = 0; i < recordIds.length; i++) {
            if (!medicalRecords[recordIds[i]].isDeleted) {
                activeRecords[currentIndex] = medicalRecords[recordIds[i]];
                currentIndex++;
            }
        }

        return activeRecords;
    }

    // Get a specific medical record
    function getMedicalRecord(uint256 _recordId, string memory _doctorHhNumber) 
        external 
        view 
        returns (MedicalRecord memory) 
    {
        require(_recordId < medicalRecords.length, "Record does not exist");
        require(!medicalRecords[_recordId].isDeleted, "Record has been deleted");
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");
        require(
            patientAccessMap[medicalRecords[_recordId].patientHhNumber][_doctorHhNumber].hasAccess,
            "Doctor does not have access"
        );

        return medicalRecords[_recordId];
    }

    // Soft delete a medical record
    function deleteMedicalRecord(uint256 _recordId, string memory _doctorHhNumber) external {
        require(_recordId < medicalRecords.length, "Record does not exist");
        require(!medicalRecords[_recordId].isDeleted, "Record already deleted");
        require(isDoctorRegistered[_doctorHhNumber], "Doctor not registered");
        require(
            keccak256(abi.encodePacked(medicalRecords[_recordId].doctorHhNumber)) == 
            keccak256(abi.encodePacked(_doctorHhNumber)),
            "Only the creator can delete the record"
        );
        
        medicalRecords[_recordId].isDeleted = true;
        
        emit MedicalRecordDeleted(
            _recordId,
            medicalRecords[_recordId].patientHhNumber,
            _doctorHhNumber,
            block.timestamp
        );
    }

    function getPatientAllMedicalRecords(string memory _patientHhNumber) 
        external 
        view 
        returns (MedicalRecord[] memory) 
    {
        // Get all record IDs for the patient
        uint256[] memory recordIds = patientRecords[_patientHhNumber];
        uint256 activeRecordCount = 0;

        // Count active (non-deleted) records
        for (uint256 i = 0; i < recordIds.length; i++) {
            if (!medicalRecords[recordIds[i]].isDeleted) {
                activeRecordCount++;
            }
        }

        // Create array of active records
        MedicalRecord[] memory activeRecords = new MedicalRecord[](activeRecordCount);
        uint256 currentIndex = 0;

        // Fill the array with active records
        for (uint256 i = 0; i < recordIds.length; i++) {
            if (!medicalRecords[recordIds[i]].isDeleted) {
                activeRecords[currentIndex] = medicalRecords[recordIds[i]];
                currentIndex++;
            }
        }

        return activeRecords;
    }
}

// ContractAudit: Immutable Audit Trail for Medical Record Actions
contract ContractAudit {
    enum ActionType { 
        CREATE, 
        UPDATE, 
        VIEW, 
        GRANT_ACCESS, 
        REVOKE_ACCESS 
    }

    struct AuditLog {
        string entityId;  // Patient or Doctor HH Number
        ActionType actionType;
        address performer;
        uint256 timestamp;
        string details;
    }

    AuditLog[] public auditLogs;

    event AuditLogCreated(
        string indexed entityId, 
        ActionType indexed actionType, 
        address indexed performer
    );

    // Log an audit entry
    function logAudit(
        string memory _entityId,
        ActionType _actionType,
        string memory _details
    ) external {
        AuditLog memory newLog = AuditLog({
            entityId: _entityId,
            actionType: _actionType,
            performer: msg.sender,
            timestamp: block.timestamp,
            details: _details
        });

        auditLogs.push(newLog);

        emit AuditLogCreated(_entityId, _actionType, msg.sender);
    }

    // Retrieve audit logs for a specific entity
    function getAuditLogsForEntity(string memory _entityId) 
        external 
        view 
        returns (AuditLog[] memory) 
    {
        uint256 count = 0;
        for (uint256 i = 0; i < auditLogs.length; i++) {
            if (keccak256(abi.encodePacked(auditLogs[i].entityId)) == keccak256(abi.encodePacked(_entityId))) {
                count++;
            }
        }

        AuditLog[] memory entityLogs = new AuditLog[](count);
        uint256 index = 0;
        for (uint256 i = 0; i < auditLogs.length; i++) {
            if (keccak256(abi.encodePacked(auditLogs[i].entityId)) == keccak256(abi.encodePacked(_entityId))) {
                entityLogs[index] = auditLogs[i];
                index++;
            }
        }

        return entityLogs;
    }
}