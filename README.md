# digital-banking-fraud-detection
Java Based Digital Banking Fraud Detection &amp; Simulation Engine


1. Technology Stack

Java + Spring Boot

Spring Data JPA (Hibernate)

MySQL Database

REST APIs

Maven Build Tool

Simulator (Core Java)

“We used Spring Boot for backend APIs, JPA for ORM mapping, and MySQL for persistence. Fraud detection logic is implemented in Java, and a simulator module generates test transactions.”


2. System Architecture

Flow:

Account → Transaction API → Fraud Detection Service → Rule Engine → Fraud Result → Database

“First, an account is created. Transactions are submitted through REST APIs. The Fraud Detection Service processes them, invokes the rule engine, generates fraud results, and stores both transaction and alert data in the database.”


3. Database & Entities

Entities implemented:

Account

Transaction

FraudResult

Relationships:

Account → One-to-Many → Transactions

Transaction → One-to-One → FraudResult

“The Account entity stores customer account details. Transactions are linked to accounts. Each transaction produces one fraud evaluation result containing risk score and triggered rules.”


4. Account Class Explanation

Fields:

accountNumber (Unique)

customerName

accountType

balance

active

createdAt

Features:

Validation annotations

Auto timestamp (@PrePersist)

“This class represents bank accounts. It ensures data validation and automatically stores creation timestamps. It is referenced by transactions for fraud analysis.”


5. Transaction Class Explanation

Fields:

transactionId

account (ManyToOne)

amount

type (ATM / POS / ONLINE)

location

merchant

deviceId

transactionTime

fraudFlag

“This class stores transaction details. Fraud detection rules analyze fields like amount, location, time, and merchant. Fraud status is updated after evaluation.”


6. FraudResult Class

Stores:

fraudDetected (True/False)

riskScore

ruleTriggered

evaluatedAt

“This acts as the fraud alert record. It keeps a risk score and rule trace so investigators know why a transaction was flagged.”


7. Fraud Detection Flow

Receive transaction

Validate account

Save transaction

Run fraud rules

Calculate risk score

Mark fraud flag

Store FraudResult

“This flow ensures every transaction is persisted first, then evaluated. This helps rules that depend on transaction history.”


8. Rule Engine Design

Interface: FraudRule

Methods:

evaluate()

ruleName()

riskScore()

Engine:

Executes all rules

Aggregates risk score

Compares with threshold

“All rules implement a common interface. The engine runs them, sums risk scores, and flags fraud if threshold is exceeded.”


9. Implemented Fraud Rules

High Amount Rule

Foreign Location Rule

Odd Hours Rule

Rapid Transactions Rule

Suspicious Merchant Rule

“We implemented multiple real-world fraud scenarios. Each rule contributes a weighted risk score.”


10. Example Rule Logic

High Amount Rule:

Threshold: ₹75,000

Risk Score: 0.8

Odd Hours Rule:

Time: 12 AM – 5 AM

Risk Score: 0.5

“If a transaction exceeds ₹75,000, it is highly suspicious. Transactions during odd hours also increase risk.”


11.Rapid Transactions Rule

Logic:

≥ 3 transactions

Within 1 minute

Same account

Risk Score: 0.9

“This rule detects burst activity, common in account takeover or card cloning fraud.”


12. REST APIs Implemented

POST /api/accounts → Create account
POST /api/fraud/transactions → Detect fraud
GET /api/fraud/summary → System status

“These APIs allow ingestion of accounts and transactions and return fraud evaluation results.”


13. Transaction Simulator

Components:

TransactionGenerator

FraudSimulationRunner

Generates:

Random amounts

Locations

Merchants

Time patterns

“The simulator generates synthetic transactions to test fraud rules without manual API calls.”



14. Simulation Output

Displays:

Transaction details

Triggered rules

Risk score

Fraud decision

Fraud rate summary

“This helps validate detection accuracy and rule effectiveness.”


15. Exception Handling

Implemented:

AccountNotFoundException

GlobalExceptionHandler

Handles:

Validation errors

Runtime errors

404 responses

“This ensures clean API error responses and better debugging.”


16. ML Integration (Future Scope)

MLFraudEngine (Stub)

Future plan:

Train model on fraud data

Integrate via REST / ONNX

Hybrid rule + ML detection

“I created a placeholder ML engine. Later we can integrate machine learning for adaptive fraud detection.”


17. Current Progress Status

✅ Rule engine implemented
✅ APIs working
✅ Database integrated
✅ Simulator working
⚠ Alert filters pending
⚠ Dashboard pending
⚠ ML integration pending

“Core backend detection is complete. Visualization and ML enhancements are next.”


18. Conclusion

Built scalable fraud detection backend

Implemented real fraud rules

Added simulation testing

Ready for dashboard & ML expansion

“This project demonstrates a modular fraud detection engine ready for enterprise extension.”
