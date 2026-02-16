package com.bank.fraud.rules;

public class RuleEvaluationStats {

    private int totalTransactions;
    private int fraudDetected;
    private int normalTransactions;

    public void incrementTotal() {
        totalTransactions++;
    }

    public void incrementFraud() {
        fraudDetected++;
    }

    public void incrementNormal() {
        normalTransactions++;
    }

    public void printSummary() {
        System.out.println("===== FRAUD RULE EVALUATION =====");
        System.out.println("Total Transactions : " + totalTransactions);
        System.out.println("Fraud Detected     : " + fraudDetected);
        System.out.println("Normal             : " + normalTransactions);
        if (totalTransactions > 0) {
            System.out.println("Fraud Rate (%)     : " +
                    ((double) fraudDetected / totalTransactions) * 100);
        } else {
            System.out.println("Fraud Rate (%)     : 0");
        }
        System.out.println("================================");
    }
}
