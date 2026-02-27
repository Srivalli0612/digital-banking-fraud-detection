package com.bank.fraud.rules;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RuleEvaluationStats {

    // ✅ Added Logger
    private static final Logger log = LoggerFactory.getLogger(RuleEvaluationStats.class);

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
        // ✅ Replaced System.out with structured log messages
        log.info("===== FRAUD RULE EVALUATION SUMMARY =====");
        log.info("Total Transactions : {}", totalTransactions);
        log.info("Fraud Detected     : {}", fraudDetected);
        log.info("Normal             : {}", normalTransactions);

        if (totalTransactions > 0) {
            double fraudRate = ((double) fraudDetected / totalTransactions) * 100;
            log.info("Fraud Rate (%)     : {}%", String.format("%.2f", fraudRate));
        } else {
            log.info("Fraud Rate (%)     : 0%");
        }
        
        log.info("========================================");
    }
}