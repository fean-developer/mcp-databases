-- PostgreSQL version of the schema and logic

CREATE TABLE Customers (
    CustomerId SERIAL PRIMARY KEY,
    FullName VARCHAR(150) NOT NULL,
    SSN CHAR(11) UNIQUE NOT NULL,
    BirthDate DATE NOT NULL,
    Address VARCHAR(255),
    Phone VARCHAR(20),
    Email VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE loan_status AS ENUM ('Active', 'Closed', 'Overdue', 'Canceled');
CREATE TABLE Loans (
    LoanId SERIAL PRIMARY KEY,
    CustomerId INT NOT NULL REFERENCES Customers(CustomerId),
    PrincipalAmount NUMERIC(18,2) NOT NULL,
    InterestRate NUMERIC(5,2) NOT NULL,
    InstallmentsCount INT NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE,
    Status loan_status,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TYPE installment_status AS ENUM ('Pending', 'Paid', 'Overdue');
CREATE TABLE Installments (
    InstallmentId SERIAL PRIMARY KEY,
    LoanId INT NOT NULL REFERENCES Loans(LoanId),
    InstallmentNumber INT NOT NULL,
    Amount NUMERIC(18,2) NOT NULL,
    DueDate DATE NOT NULL,
    PaidDate DATE,
    Status installment_status
);

CREATE TYPE payment_method AS ENUM ('BankSlip', 'PIX', 'Transfer', 'CreditCard');
CREATE TABLE Payments (
    PaymentId SERIAL PRIMARY KEY,
    InstallmentId INT NOT NULL REFERENCES Installments(InstallmentId),
    PaidAmount NUMERIC(18,2) NOT NULL,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PaymentMethod payment_method
);

CREATE TABLE Collaterals (
    CollateralId SERIAL PRIMARY KEY,
    LoanId INT NOT NULL REFERENCES Loans(LoanId),
    Type VARCHAR(50) NOT NULL,
    Description VARCHAR(255),
    EstimatedValue NUMERIC(18,2)
);

CREATE TYPE user_role AS ENUM ('Admin', 'Manager', 'Analyst');
CREATE TABLE Users (
    UserId SERIAL PRIMARY KEY,
    FullName VARCHAR(150) NOT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role user_role
);

-- Função para gerar parcelas (Price)
CREATE OR REPLACE FUNCTION GenerateInstallments(p_LoanId INT) RETURNS VOID AS $$
DECLARE
    v_PrincipalAmount NUMERIC(18,2);
    v_InterestRate NUMERIC(5,2);
    v_InstallmentsCount INT;
    v_StartDate DATE;
    v_InstallmentValue NUMERIC(18,2);
    v_i INT := 1;
    v_MonthlyRate NUMERIC(18,8);
BEGIN
    SELECT "PrincipalAmount", "InterestRate", "InstallmentsCount", "StartDate"
      INTO v_PrincipalAmount, v_InterestRate, v_InstallmentsCount, v_StartDate
      FROM "Loans" WHERE "LoanId" = p_LoanId;
    v_MonthlyRate := v_InterestRate / 100.0;
    v_InstallmentValue := v_PrincipalAmount * (v_MonthlyRate / (1 - POWER(1 + v_MonthlyRate, -v_InstallmentsCount)));
    WHILE v_i <= v_InstallmentsCount LOOP
        INSERT INTO "Installments" ("LoanId", "InstallmentNumber", "Amount", "DueDate", "Status")
        VALUES (
            p_LoanId,
            v_i,
            ROUND(v_InstallmentValue, 2),
            v_StartDate + (v_i || ' month')::interval,
            'Pending'
        );
        v_i := v_i + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Função para gerar parcelas (SAC)
CREATE OR REPLACE FUNCTION GenerateInstallments_SAC(p_LoanId INT) RETURNS VOID AS $$
DECLARE
    v_PrincipalAmount NUMERIC(18,2);
    v_InterestRate NUMERIC(5,2);
    v_InstallmentsCount INT;
    v_StartDate DATE;
    v_Amortization NUMERIC(18,2);
    v_RemainingBalance NUMERIC(18,2);
    v_InstallmentValue NUMERIC(18,2);
    v_i INT := 1;
    v_Interest NUMERIC(18,2);
BEGIN
    SELECT "PrincipalAmount", "InterestRate", "InstallmentsCount", "StartDate"
      INTO v_PrincipalAmount, v_InterestRate, v_InstallmentsCount, v_StartDate
      FROM "Loans" WHERE "LoanId" = p_LoanId;
    v_Amortization := v_PrincipalAmount / v_InstallmentsCount;
    v_RemainingBalance := v_PrincipalAmount;
    WHILE v_i <= v_InstallmentsCount LOOP
        v_Interest := v_RemainingBalance * (v_InterestRate / 100.0);
        v_InstallmentValue := v_Amortization + v_Interest;
        INSERT INTO "Installments" ("LoanId", "InstallmentNumber", "Amount", "DueDate", "Status")
        VALUES (
            p_LoanId,
            v_i,
            ROUND(v_InstallmentValue, 2),
            v_StartDate + (v_i || ' month')::interval,
            'Pending'
        );
        v_RemainingBalance := v_RemainingBalance - v_Amortization;
        v_i := v_i + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- View LoanSummary

CREATE OR REPLACE VIEW loansummary AS
SELECT 
    l.loanid,
    c.fullname AS customername,
    l.principalamount,
    l.interestrate,
    l.installmentscount,
    l.startdate,
    l.status,
    COALESCE(SUM(p.paidamount), 0) AS totalpaid,
    (l.principalamount - COALESCE(SUM(p.paidamount), 0)) AS remainingbalance,
    CASE 
        WHEN (l.principalamount - COALESCE(SUM(p.paidamount), 0)) <= 0 THEN 'Closed'
        ELSE l.status::text
    END AS currentstatus
FROM loans l
INNER JOIN customers c ON l.customerid = c.customerid
LEFT JOIN installments i ON l.loanid = i.loanid
LEFT JOIN payments p ON i.installmentid = p.installmentid
GROUP BY 
    l.loanid, 
    c.fullname, 
    l.principalamount, 
    l.interestrate, 
    l.installmentscount, 
    l.startdate, 
    l.status;

-- Função para atualizar status de empréstimos e parcelas
CREATE OR REPLACE FUNCTION UpdateLoanAndInstallmentStatus() RETURNS VOID AS $$
BEGIN
    -- 1. Mark installments as 'Paid' if there is at least one payment
    UPDATE "Installments" I
    SET "Status" = 'Paid',
        "PaidDate" = COALESCE("PaidDate", F."FirstPaymentDate")
    FROM (
        SELECT "InstallmentId", MIN("PaymentDate") AS "FirstPaymentDate"
        FROM "Payments"
        GROUP BY "InstallmentId"
    ) F
    WHERE I."InstallmentId" = F."InstallmentId"
      AND I."Status" <> 'Paid';

    -- 2. Mark installments as 'Overdue' if past due and still pending
    UPDATE "Installments"
    SET "Status" = 'Overdue'
    WHERE "Status" = 'Pending'
      AND "DueDate" < CURRENT_DATE;

    -- 3. Mark loans as 'Closed' if all installments are paid
    UPDATE "Loans" L
    SET "Status" = 'Closed'
    WHERE NOT EXISTS (
        SELECT 1 FROM "Installments" I WHERE I."LoanId" = L."LoanId" AND I."Status" <> 'Paid'
    );

    -- 4. Mark loans as 'Overdue' if there are overdue installments
    UPDATE "Loans" L
    SET "Status" = 'Overdue'
    WHERE EXISTS (
        SELECT 1 FROM "Installments" I WHERE I."LoanId" = L."LoanId" AND I."Status" = 'Overdue'
    )
    AND L."Status" NOT IN ('Closed', 'Canceled');

    -- 5. Mark loans as 'Active' if still has pending installments
    UPDATE "Loans" L
    SET "Status" = 'Active'
    WHERE EXISTS (
        SELECT 1 FROM "Installments" I WHERE I."LoanId" = L."LoanId" AND I."Status" = 'Pending'
    )
    AND L."Status" NOT IN ('Closed', 'Canceled');
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar status após pagamento
CREATE OR REPLACE FUNCTION trg_update_status_on_payment() RETURNS TRIGGER AS $$
BEGIN
    PERFORM UpdateLoanAndInstallmentStatus();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_status_on_payment
AFTER INSERT ON payments
FOR EACH ROW
EXECUTE FUNCTION trg_update_status_on_payment();
