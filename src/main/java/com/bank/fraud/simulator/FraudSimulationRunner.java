package com.bank.fraud.simulator;

import com.bank.fraud.model.*;
import com.bank.fraud.rules.RuleEngine;
import com.bank.fraud.rules.RuleEvaluationResult;
import com.bank.fraud.rules.RuleEvaluationStats;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;

@Component
public class FraudSimulationRunner implements CommandLineRunner {

    // ✅ Added Logger
    private static final Logger log = LoggerFactory.getLogger(FraudSimulationRunner.class);

    private final RuleEngine ruleEngine;

    public FraudSimulationRunner(RuleEngine ruleEngine) {
        this.ruleEngine = ruleEngine;
    }

    @Override
    public void run(String... args) {

        RuleEvaluationStats stats = new RuleEvaluationStats();

        Account account = new Account();
        account.setAccountNumber("ACC123456");
        account.setCustomerName("Test User");
        account.setAccountType(AccountType.SAVINGS);
        account.setBalance(BigDecimal.valueOf(500000));

        TransactionGenerator generator = new TransactionGenerator();

        log.info("Starting Fraud Simulation for account: {}", account.getAccountNumber());

        for (int i = 1; i <= 20; i++) {

            Transaction tx = generator.generate(account);
            RuleEvaluationResult result = ruleEngine.evaluate(tx);

            stats.incrementTotal();
            
            BigDecimal score = result.getNormalizedScore();
            
            RiskLevel riskLevel = calculateRiskLevel(score);
            
            //Fraud Decision or fraud flag
            boolean isFraud = riskLevel == RiskLevel.HIGH_RISK
                    || riskLevel == RiskLevel.CRITICAL_RISK;

            // Map riskLevel to priority
            AlertPriority priority = mapPriority(riskLevel);
            
            
//            // Decide fraud threshold for simulation
//            boolean isFraud = score.compareTo(new BigDecimal("0.6")) >= 0;

            if (isFraud) {
                stats.incrementFraud();
                log.warn("FRAUD DETECTED - Tx #{}: Amount: {}, Rules: {}, Score: {}",
                        i, tx.getAmount(),
                        result.getTriggeredRules(),
                        score);
            } else {
                stats.incrementNormal();
                log.info("Normal Transaction - Tx #{}: Amount: {}, Score: {}",
                        i, tx.getAmount(),
                        score);
            }

            // ✅ Structured logging for the full transaction details
//            log.debug("Full Tx Details: ID: {}, Loc: {}, Merchant: {}, Time: {}, Sender: {}, Receiver: {}",
//                tx.getTransactionId(),
//                tx.getLocation(),
//                tx.getMerchant(),
//                tx.getTransactionTime(),
//                tx.getSenderName(),
//                tx.getReceiverName()
//            );
            
            log.info("Sender: {}", tx.getSenderName());
            log.info("Receiver: {}", tx.getReceiverName());
            log.info("Transaction ID: {}", tx.getTransactionId());
            log.info("Transaction Type: {}", tx.getTransactionType());
            log.info("Status: {}", tx.getStatus());
            log.info("Transaction Time: {}", tx.getTransactionTime());
            log.info("Merchant: {}", tx.getMerchant());
            log.info("Location: {}", tx.getLocation());
            log.info("Risk Level: {}", riskLevel);

            
            
            
            log.info("\n");
            
            
            
        }
        
        log.info("Simulation completed.");
        
        stats.printSummary(); 
    }
    
    private RiskLevel calculateRiskLevel(BigDecimal score) {
        if (score.compareTo(new BigDecimal("0.3")) < 0) {
            return RiskLevel.LOW_RISK;
        } else if (score.compareTo(new BigDecimal("0.6")) < 0) {
            return RiskLevel.MEDIUM_RISK;
        } else if (score.compareTo(new BigDecimal("0.8")) < 0) {
            return RiskLevel.HIGH_RISK;
        } else {
            return RiskLevel.CRITICAL_RISK;
        }
    }
    
    private AlertPriority mapPriority(RiskLevel level) {
        switch (level) {
            case LOW_RISK:
                return AlertPriority.LOW;
            case MEDIUM_RISK:
                return AlertPriority.MEDIUM;
            case HIGH_RISK:
                return AlertPriority.HIGH;
            case CRITICAL_RISK:
                return AlertPriority.CRITICAL;
            default:
                return AlertPriority.LOW;
        }
    }
}