package com.bank.fraud.simulator;

import com.bank.fraud.model.*;
import com.bank.fraud.rules.RuleEngine;
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
            FraudResult result = ruleEngine.evaluate(tx);

            stats.incrementTotal();

            if (result.getFraudDetected()) {
                stats.incrementFraud();
                // ✅ Using log.warn for detected fraud
                log.warn("FRAUD DETECTED - Tx #{}: Amount: {}, Rules: {}", 
                    i, tx.getAmount(), result.getRuleTriggered());
            } else {
                stats.incrementNormal();
                // ✅ Using log.info for regular transactions
                log.info("Normal Transaction - Tx #{}: Amount: {}, Score: {}", 
                    i, tx.getAmount(), result.getRiskScore());
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
            
            
            log.info("\n");
            
            
            
        }
        
        log.info("Simulation completed.");
        
        stats.printSummary(); 
    }
}