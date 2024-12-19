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

    mapping(string => Doctor) private doctors;
    mapping(string => bool) public isDoctorRegistered;
    mapping(string => mapping(string => AccessPermission)) private patientAccessMap;

    event DoctorRegistered(string indexed hhNumber, string name, address walletAddress);
    event AccessPermissionChanged(string indexed patientHhNumber, string indexed doctorHhNumber, bool granted);

    // Add this at the beginning of the contract
    string[] private registeredDoctors;

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

        function updateDoctorInfo(
        string memory _hhNumber,
        string memory _specialization,
        string memory _hospitalName
            ) external {
                require(isDoctorRegistered[_hhNumber], "Doctor not registered");
                require(doctors[_hhNumber].walletAddress == msg.sender, "Unauthorized access");

                doctors[_hhNumber].specialization = _specialization;
                doctors[_hhNumber].hospitalName = _hospitalName;
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

        emit AccessPermissionChanged(_patientHhNumber, _doctorHhNumber, true);
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