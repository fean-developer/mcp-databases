CREATE TABLE Customers (
    CustomerId INT PRIMARY KEY AUTO_INCREMENT,
    FullName VARCHAR(150) NOT NULL,
    SSN CHAR(11) UNIQUE NOT NULL,
    BirthDate DATE NOT NULL,
    Address VARCHAR(255),
    Phone VARCHAR(20),
    Email VARCHAR(100),
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
/* 2025-08-28 16:57:13 [65 ms] */ 
CREATE TABLE Loans (
    LoanId INT PRIMARY KEY AUTO_INCREMENT,
    CustomerId INT NOT NULL,
    PrincipalAmount DECIMAL(18,2) NOT NULL,
    InterestRate DECIMAL(5,2) NOT NULL,
    InstallmentsCount INT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,
    Status ENUM('Active', 'Closed', 'Overdue', 'Canceled'),
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId)
);
/* 2025-08-28 16:57:24 [30 ms] */ 
CREATE TABLE Installments (
    InstallmentId INT PRIMARY KEY AUTO_INCREMENT,
    LoanId INT NOT NULL,
    InstallmentNumber INT NOT NULL,
    Amount DECIMAL(18,2) NOT NULL,
    DueDate DATE NOT NULL,
    PaidDate DATE NULL,
    Status ENUM('Pending', 'Paid', 'Overdue'),
    FOREIGN KEY (LoanId) REFERENCES Loans(LoanId)
);
/* 2025-08-28 16:57:35 [32 ms] */ 
CREATE TABLE Payments (
    PaymentId INT PRIMARY KEY AUTO_INCREMENT,
    InstallmentId INT NOT NULL,
    PaidAmount DECIMAL(18,2) NOT NULL,
    PaymentDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod ENUM('BankSlip', 'PIX', 'Transfer', 'CreditCard'),
    FOREIGN KEY (InstallmentId) REFERENCES Installments(InstallmentId)
);
/* 2025-08-28 16:57:49 [27 ms] */ 
CREATE TABLE Collaterals (
    CollateralId INT PRIMARY KEY AUTO_INCREMENT,
    LoanId INT NOT NULL,
    Type VARCHAR(50) NOT NULL,
    Description VARCHAR(255),
    EstimatedValue DECIMAL(18,2),
    FOREIGN KEY (LoanId) REFERENCES Loans(LoanId)
);
/* 2025-08-28 16:58:27 [23 ms] */ 
CREATE TABLE Users (
    UserId INT PRIMARY KEY AUTO_INCREMENT,
    FullName VARCHAR(150) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role ENUM('Admin', 'Manager', 'Analyst')
);
/* 2025-08-28 16:58:45 [29 ms] */ 
DELIMITER //
CREATE PROCEDURE GenerateInstallments(IN p_LoanId INT)
BEGIN
    DECLARE v_PrincipalAmount DECIMAL(18,2);
    DECLARE v_InterestRate DECIMAL(5,2);
    DECLARE v_InstallmentsCount INT;
    DECLARE v_StartDate DATE;
    DECLARE v_InstallmentValue DECIMAL(18,2);
    DECLARE v_i INT DEFAULT 1;
    DECLARE v_MonthlyRate DECIMAL(18,8);

    SELECT PrincipalAmount, InterestRate, InstallmentsCount, StartDate
        INTO v_PrincipalAmount, v_InterestRate, v_InstallmentsCount, v_StartDate
        FROM Loans WHERE LoanId = p_LoanId;

    SET v_MonthlyRate = v_InterestRate / 100.0;
    SET v_InstallmentValue = v_PrincipalAmount * (v_MonthlyRate / (1 - POW(1 + v_MonthlyRate, -v_InstallmentsCount)));

    WHILE v_i <= v_InstallmentsCount DO
        INSERT INTO Installments (LoanId, InstallmentNumber, Amount, DueDate, Status)
        VALUES (
            p_LoanId,
            v_i,
            ROUND(v_InstallmentValue, 2),
            DATE_ADD(v_StartDate, INTERVAL v_i MONTH),
            'Pending'
        );
        SET v_i = v_i + 1;
    END WHILE;
END //
DELIMITER ;
/* 2025-08-28 16:59:25 [32 ms] */ 
DELIMITER //
CREATE PROCEDURE GenerateInstallments_SAC(IN p_LoanId INT)
BEGIN
    DECLARE v_PrincipalAmount DECIMAL(18,2);
    DECLARE v_InterestRate DECIMAL(5,2);
    DECLARE v_InstallmentsCount INT;
    DECLARE v_StartDate DATE;
    DECLARE v_Amortization DECIMAL(18,2);
    DECLARE v_RemainingBalance DECIMAL(18,2);
    DECLARE v_InstallmentValue DECIMAL(18,2);
    DECLARE v_i INT DEFAULT 1;
    DECLARE v_Interest DECIMAL(18,2);

    SELECT PrincipalAmount, InterestRate, InstallmentsCount, StartDate
        INTO v_PrincipalAmount, v_InterestRate, v_InstallmentsCount, v_StartDate
        FROM Loans WHERE LoanId = p_LoanId;

    SET v_Amortization = v_PrincipalAmount / v_InstallmentsCount;
    SET v_RemainingBalance = v_PrincipalAmount;

    WHILE v_i <= v_InstallmentsCount DO
        SET v_Interest = v_RemainingBalance * (v_InterestRate / 100.0);
        SET v_InstallmentValue = v_Amortization + v_Interest;
        INSERT INTO Installments (LoanId, InstallmentNumber, Amount, DueDate, Status)
        VALUES (
            p_LoanId,
            v_i,
            ROUND(v_InstallmentValue, 2),
            DATE_ADD(v_StartDate, INTERVAL v_i MONTH),
            'Pending'
        );
        SET v_RemainingBalance = v_RemainingBalance - v_Amortization;
        SET v_i = v_i + 1;
    END WHILE;
END //
DELIMITER ;
/* 2025-08-28 16:59:59 [26 ms] */ 
CREATE VIEW LoanSummary AS
SELECT 
    L.LoanId,
    C.FullName AS CustomerName,
    L.PrincipalAmount,
    L.InterestRate,
    L.InstallmentsCount,
    L.StartDate,
    L.Status,
    IFNULL(SUM(P.PaidAmount), 0) AS TotalPaid,
    (L.PrincipalAmount - IFNULL(SUM(P.PaidAmount), 0)) AS RemainingBalance,
    CASE 
        WHEN (L.PrincipalAmount - IFNULL(SUM(P.PaidAmount), 0)) <= 0 THEN 'Closed'
        ELSE L.Status
    END AS CurrentStatus
FROM Loans L
INNER JOIN Customers C ON L.CustomerId = C.CustomerId
LEFT JOIN Installments I ON L.LoanId = I.LoanId
LEFT JOIN Payments P ON I.InstallmentId = P.InstallmentId
GROUP BY 
    L.LoanId, 
    C.FullName, 
    L.PrincipalAmount, 
    L.InterestRate, 
    L.InstallmentsCount, 
    L.StartDate, 
    L.Status;
/* 2025-08-28 17:01:35 [37 ms] */ 
DELIMITER //
CREATE PROCEDURE UpdateLoanAndInstallmentStatus()
BEGIN
    -- 1. Mark installments as 'Paid' if there is at least one payment
    UPDATE Installments I
    JOIN (
        SELECT InstallmentId, MIN(PaymentDate) AS FirstPaymentDate
        FROM Payments
        GROUP BY InstallmentId
    ) F ON I.InstallmentId = F.InstallmentId
    SET I.Status = 'Paid',
        I.PaidDate = IFNULL(I.PaidDate, F.FirstPaymentDate)
    WHERE I.Status <> 'Paid';

    -- 2. Mark installments as 'Overdue' if past due and still pending
    UPDATE Installments
    SET Status = 'Overdue'
    WHERE Status = 'Pending'
      AND DueDate < CURDATE();

    -- 3. Mark loans as 'Closed' if all installments are paid
    UPDATE Loans L
    SET L.Status = 'Closed'
    WHERE NOT EXISTS (
        SELECT 1 FROM Installments I WHERE I.LoanId = L.LoanId AND I.Status <> 'Paid'
    );

    -- 4. Mark loans as 'Overdue' if there are overdue installments
    UPDATE Loans L
    SET L.Status = 'Overdue'
    WHERE EXISTS (
        SELECT 1 FROM Installments I WHERE I.LoanId = L.LoanId AND I.Status = 'Overdue'
    )
    AND L.Status NOT IN ('Closed', 'Canceled');

    -- 5. Mark loans as 'Active' if still has pending installments
    UPDATE Loans L
    SET L.Status = 'Active'
    WHERE EXISTS (
        SELECT 1 FROM Installments I WHERE I.LoanId = L.LoanId AND I.Status = 'Pending'
    )
    AND L.Status NOT IN ('Closed', 'Canceled');
END //
DELIMITER ;
/* 2025-08-28 17:02:48 [31 ms] */ 
DELIMITER //
CREATE TRIGGER TRG_UpdateStatus_OnPayment
AFTER INSERT ON Payments
FOR EACH ROW
BEGIN
    CALL UpdateLoanAndInstallmentStatus();
END //
DELIMITER ;